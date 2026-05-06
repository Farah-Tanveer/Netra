from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
import pandas as pd
import json
from datetime import datetime
from pathlib import Path
import os
import hmac
import hashlib
import base64
import time
from functools import wraps

from utils.packet_reader import PacketSniffer, PORT_SERVICE_MAP

app = Flask(__name__)
CORS(app)

# ===== SECURITY CONFIG =====
SECRET_KEY = os.environ.get("SECRET_KEY", "netra-super-secret-key-2024")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin123")
DOS_LIMIT = 100  # Requests
DOS_WINDOW = 60  # Seconds
BLOCK_DURATION = 300 # Seconds

# ===== CONFIG =====
TRAFFIC_FILE = "network_traffic.csv"
LOGS_FILE = "logs.txt"
STATS_FILE = "stats.json"
USERS_FILE = "users.json"

# ===== REAL-TIME SNIFFER INSTANCE =====
sniffer = PacketSniffer(csv_file=TRAFFIC_FILE, log_file=LOGS_FILE)

# ===== USER MANAGEMENT (First Principles) =====
def hash_password(password):
    """Hash a password using PBKDF2-SHA256"""
    salt = SECRET_KEY[:16].encode()
    return hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000).hex()

def load_users():
    if not Path(USERS_FILE).exists():
        return {}
    try:
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    except: return {}

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=2)

# ===== SECURITY UTILS (First Principles JWT) =====
def base64_url_encode(data):
    return base64.urlsafe_b64encode(data).decode('utf-8').rstrip('=')

def base64_url_decode(data):
    padding = '=' * (4 - len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)

def create_token(user_id):
    header = base64_url_encode(json.dumps({"alg": "HS256", "typ": "JWT"}).encode())
    payload = base64_url_encode(json.dumps({
        "user_id": user_id,
        "exp": time.time() + 3600, # 1 hour
        "iat": time.time()
    }).encode())
    
    signature_base = f"{header}.{payload}"
    signature = hmac.new(SECRET_KEY.encode(), signature_base.encode(), hashlib.sha256).digest()
    return f"{signature_base}.{base64_url_encode(signature)}"

def decode_token(token):
    try:
        parts = token.split('.')
        if len(parts) != 3: return None
        
        header, payload, signature = parts
        signature_base = f"{header}.{payload}"
        expected_sig = hmac.new(SECRET_KEY.encode(), signature_base.encode(), hashlib.sha256).digest()
        
        if base64_url_encode(expected_sig) != signature:
            return None
            
        data = json.loads(base64_url_decode(payload).decode())
        if data.get('exp', 0) < time.time():
            return None
        return data
    except Exception:
        return None

# ===== DOS PROTECTION =====
class RateLimiter:
    def __init__(self):
        self.requests = {}
        self.blocked = {}

    def check(self, ip):
        now = time.time()
        if ip in self.blocked:
            if now < self.blocked[ip]:
                return False
            del self.blocked[ip]
        
        if ip not in self.requests: self.requests[ip] = []
        self.requests[ip] = [t for t in self.requests[ip] if now - t < DOS_WINDOW]
        
        if len(self.requests[ip]) >= DOS_LIMIT:
            self.blocked[ip] = now + BLOCK_DURATION
            write_log(f"[SECURITY ALERT] DoS detected from {ip}. IP Blocked.")
            return False
            
        self.requests[ip].append(now)
        return True

limiter = RateLimiter()

# ===== DECORATORS =====
def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not decode_token(token):
            return jsonify({"error": "Unauthorized. Valid JWT required.", "success": False}), 401
        return f(*args, **kwargs)
    return decorated

@app.before_request
def security_check():
    # Use X-Forwarded-For if behind a proxy (Render/Heroku)
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    if ',' in ip: ip = ip.split(',')[0].strip() # Get the original client IP
    
    if not limiter.check(ip):
        return jsonify({
            "error": "DoS Protection: Too many requests.", 
            "alert": "SECURITY_DOS_ATTACK",
            "blocked_until": BLOCK_DURATION
        }), 429

@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; img-src 'self' data:;"
    return response

# ===== LOGGING & STATS =====
def write_log(message):
    """Log system events with timestamps"""
    try:
        with open(LOGS_FILE, "a", encoding="utf-8") as f:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"{timestamp} - {message}\n")
    except Exception as e:
        print(f"Log error: {e}")

def save_stats(stats):
    """Persist statistics to JSON"""
    try:
        with open(STATS_FILE, "w", encoding="utf-8") as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Stats save error: {e}")

def load_stats():
    """Load statistics from JSON"""
    try:
        if Path(STATS_FILE).exists():
            with open(STATS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception as e:
        print(f"Stats load error: {e}")
    return {"sessions": 0, "total_packets": 0, "total_data": 0}

# ===== ROUTES =====

@app.route('/')
def index():
    """Serve landing page"""
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    """Handle authentication"""
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    users = load_users()
    if username in users and users[username] == hash_password(password):
        token = create_token(username)
        write_log(f"[AUTH] User '{username}' login successful")
        return jsonify({"success": True, "token": token})
    
    # Fallback for initial admin
    if username == "admin" and password == ADMIN_PASSWORD:
        token = create_token("admin")
        return jsonify({"success": True, "token": token})

    write_log(f"[AUTH ALERT] Failed login attempt for user: {username}")
    return jsonify({"success": False, "message": "Invalid credentials"}), 401

@app.route('/register', methods=['POST'])
def register():
    """Handle user registration"""
    data = request.json
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    
    if not username or not password:
        return jsonify({"success": False, "message": "Username and password required"}), 400
    
    users = load_users()
    if username in users or username == "admin":
        return jsonify({"success": False, "message": "Username already exists"}), 400
        
    users[username] = hash_password(password)
    save_users(users)
    write_log(f"[AUTH] New user registered: {username}")
    return jsonify({"success": True, "message": "Registration successful"})

@app.route('/dashboard')
def dashboard():
    """Serve dashboard page"""
    return render_template('dashboard.html')

@app.route('/stats')
def stats_page():
    """Serve stats page"""
    return render_template('stats.html')

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get monitoring status"""
    live_stats = sniffer.get_stats()
    saved_stats = load_stats()
    return jsonify({
        "monitoring": sniffer.is_running,
        "packet_count": live_stats["total"],
        "total_sessions": saved_stats.get("sessions", 0),
        "live_stats": live_stats
    })

@app.route('/api/start-monitoring', methods=['POST'])
@require_auth
def start_monitoring_api():
    """Start real-time packet capture"""
    # Increment session count
    stats = load_stats()
    stats["sessions"] = stats.get("sessions", 0) + 1
    save_stats(stats)

    result = sniffer.start()
    write_log("[START] Real-time monitoring session initiated")
    return jsonify(result)

@app.route('/api/stop-monitoring', methods=['POST'])
@require_auth
def stop_monitoring_api():
    """Stop real-time packet capture"""
    result = sniffer.stop()

    # Update persistent stats
    live = sniffer.get_stats()
    stats = load_stats()
    stats["total_packets"] = stats.get("total_packets", 0) + live["total"]
    stats["total_data"] = stats.get("total_data", 0) + live["total_data"]
    save_stats(stats)

    write_log(f"[STOP] Monitoring session ended | Packets Captured: {live['total']}")
    return jsonify(result)

@app.route('/api/reset-session', methods=['POST'])
@require_auth
def reset_session():
    """Clear all traffic data and logs"""
    try:
        sniffer.stop()
        # Reset CSV
        if Path(TRAFFIC_FILE).exists():
            pd.DataFrame(columns=['Time', 'Source_IP', 'Destination_IP', 'Protocol', 'Source_Port', 'Destination_Port', 'Packet_Size']).to_csv(TRAFFIC_FILE, index=False)
        # Clear logs
        with open(LOGS_FILE, 'w') as f:
            f.write(f"{datetime.now()} - [RESET] Data and logs cleared by user\n")
        # Reset stats
        save_stats({"sessions": 0, "total_packets": 0, "total_data": 0})
        
        return jsonify({"success": True, "message": "Session reset successfully"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/live-packets', methods=['GET'])
def get_live_packets():
    """Get real-time captured packets from the sniffer buffer."""
    try:
        limit = int(request.args.get('limit', 50))
        protocol = request.args.get('protocol', 'ALL')
        src_ip = request.args.get('src_ip', '')
        dest_ip = request.args.get('dest_ip', '')

        packets = sniffer.get_live_packets(count=200)

        # Apply filters
        if protocol and protocol != 'ALL':
            packets = [p for p in packets if p['Protocol'] == protocol]
        if src_ip:
            packets = [p for p in packets if p['Source_IP'] == src_ip]
        if dest_ip:
            packets = [p for p in packets if p['Destination_IP'] == dest_ip]

        # Get latest N packets
        packets = packets[-limit:]

        live_stats = sniffer.get_stats()

        return jsonify({
            "data": packets,
            "stats": live_stats,
            "is_live": True,
            "timestamp": datetime.now().isoformat(),
            "success": True
        })
    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500

@app.route('/api/export-csv', methods=['GET'])
def export_csv():
    """Export the traffic CSV file"""
    try:
        if Path(TRAFFIC_FILE).exists():
            return send_file(TRAFFIC_FILE, as_attachment=True, download_name="network_traffic_export.csv", mimetype="text/csv")
        else:
            return jsonify({"error": "No traffic data available", "success": False}), 404
    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500

@app.route('/api/traffic-data', methods=['GET'])
def get_traffic_data():
    """Get filtered traffic data from CSV (historical + live)"""
    try:
        protocol = request.args.get('protocol', 'ALL')
        src_ip = request.args.get('src_ip', '')
        dest_ip = request.args.get('dest_ip', '')
        limit = int(request.args.get('limit', 50))

        if not Path(TRAFFIC_FILE).exists():
            return jsonify({"data": [], "stats": {}, "error": "No traffic data file"})

        df = pd.read_csv(TRAFFIC_FILE)

        # Apply filters
        if protocol and protocol != 'ALL':
            df = df[df['Protocol'] == protocol]
        if src_ip:
            df = df[df['Source_IP'] == src_ip]
        if dest_ip:
            df = df[df['Destination_IP'] == dest_ip]

        # Add service names
        df['Service'] = df['Destination_Port'].map(
            lambda x: PORT_SERVICE_MAP.get(int(x), "Unknown")
        )

        # Calculate stats
        stats = {
            "total": len(df),
            "tcp": len(df[df['Protocol'] == 'TCP']),
            "udp": len(df[df['Protocol'] == 'UDP']),
            "icmp": len(df[df['Protocol'] == 'ICMP']),
            "avg_size": round(df['Packet_Size'].mean(), 2) if len(df) > 0 else 0,
            "total_data": round(df['Packet_Size'].sum() / 1024, 2)  # KB
        }

        data = df.tail(limit).to_dict(orient='records')
        
        return jsonify({
            "data": data,
            "stats": stats,
            "timestamp": datetime.now().isoformat(),
            "success": True
        })

    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats_detailed():
    """Get detailed statistics for stats page"""
    try:
        if not Path(TRAFFIC_FILE).exists():
            return jsonify({
                "error": "No data available",
                "protocols": {},
                "top_sources": {},
                "top_ports": {}
            })

        df = pd.read_csv(TRAFFIC_FILE)

        # Protocol distribution
        protocol_counts = df['Protocol'].value_counts().to_dict()

        # Top source IPs
        top_src = df['Source_IP'].value_counts().head(5).to_dict()

        # Top destination ports
        top_ports = df.groupby('Destination_Port').size().nlargest(5).to_dict()
        
        # Add service names to ports
        top_ports_services = {
            str(PORT_SERVICE_MAP.get(int(port), f"Port {port}")): count 
            for port, count in top_ports.items()
        }

        # Average packet size
        avg_size = round(df['Packet_Size'].mean(), 2) if len(df) > 0 else 0

        # Total data transferred
        total_data_kb = round(df['Packet_Size'].sum() / 1024, 2)

        # Packet size distribution
        size_bins = [0, 64, 512, 1500, float('inf')]
        size_labels = ['Small (<64B)', 'Medium (64-512B)', 'Large (512-1.5KB)', 'Jumbo (>1.5KB)']
        df['size_category'] = pd.cut(df['Packet_Size'], bins=size_bins, labels=size_labels)
        size_dist = df['size_category'].value_counts().to_dict()

        return jsonify({
            "protocols": protocol_counts,
            "top_sources": top_src,
            "top_ports": top_ports_services,
            "size_dist": size_dist,
            "total_packets": len(df),
            "unique_sources": df['Source_IP'].nunique(),
            "unique_destinations": df['Destination_IP'].nunique(),
            "avg_packet_size": avg_size,
            "total_data_kb": total_data_kb,
            "success": True
        })

    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500

@app.route('/api/logs', methods=['GET'])
def get_logs():
    """Get system logs"""
    try:
        limit = int(request.args.get('limit', 50))
        if Path(LOGS_FILE).exists():
            with open(LOGS_FILE, 'r', encoding='utf-8') as f:
                logs = f.readlines()[-limit:]
            # Strip whitespace and filter out empty lines
            logs = [l.strip() for l in logs if l.strip()]
            return jsonify({"logs": logs, "success": True})
        return jsonify({"logs": [], "success": True})
    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500

# ===== ERROR HANDLERS =====
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not found"}), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({"error": "Server error"}), 500

if __name__ == '__main__':
    # Initialize files if they don't exist
    Path(LOGS_FILE).touch(exist_ok=True)
    if not Path(STATS_FILE).exists():
        save_stats({"sessions": 0, "total_packets": 0, "total_data": 0})
    write_log("[INIT] Netra Application Started")
    print("\n" + "="*50)
    print("Netra - Network Traffic Monitoring Platform")
    print("  Real-Time Packet Sniffing Enabled (Scapy)")
    print("="*50)
    print("Server running at: http://127.0.0.1:5000")
    print("="*50 + "\n")
    app.run(debug=True, port=5000)
