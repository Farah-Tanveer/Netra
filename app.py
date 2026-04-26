from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import pandas as pd
import json
from datetime import datetime
from pathlib import Path
import os

app = Flask(__name__)
CORS(app)

# ===== CONFIG =====
TRAFFIC_FILE = "network_traffic.csv"
LOGS_FILE = "logs.txt"
STATS_FILE = "stats.json"

monitoring = False
packet_count = 0

# ===== UTILITY FUNCTIONS =====
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

# ===== PORT TO SERVICE MAPPING =====
PORT_SERVICE_MAP = {
    80: "HTTP", 443: "HTTPS", 53: "DNS", 22: "SSH",
    67: "DHCP", 161: "SNMP", 3306: "MySQL", 5432: "PostgreSQL",
    3389: "RDP", 21: "FTP", 25: "SMTP", 110: "POP3"
}

# ===== ROUTES =====

@app.route('/')
def index():
    """Serve landing page"""
    return render_template('index.html')

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
    global packet_count
    stats = load_stats()
    return jsonify({
        "monitoring": monitoring,
        "packet_count": packet_count,
        "total_sessions": stats.get("sessions", 0)
    })

@app.route('/api/start-monitoring', methods=['POST'])
def start_monitoring_api():
    """Start traffic monitoring"""
    global monitoring, packet_count
    monitoring = True
    packet_count = 0
    stats = load_stats()
    stats["sessions"] = stats.get("sessions", 0) + 1
    save_stats(stats)
    write_log("[START] Monitoring session initiated")
    return jsonify({"success": True, "message": "Monitoring started"})

@app.route('/api/stop-monitoring', methods=['POST'])
def stop_monitoring_api():
    """Stop traffic monitoring"""
    global monitoring, packet_count
    monitoring = False
    write_log(f"[STOP] Monitoring session ended | Packets Captured: {packet_count}")
    return jsonify({"success": True, "message": "Monitoring stopped"})

@app.route('/api/traffic-data', methods=['GET'])
def get_traffic_data():
    """Get filtered traffic data"""
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

        return jsonify({
            "protocols": protocol_counts,
            "top_sources": top_src,
            "top_ports": top_ports_services,
            "total_packets": len(df),
            "unique_sources": df['Source_IP'].nunique(),
            "unique_destinations": df['Destination_IP'].nunique(),
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
    print("="*50)
    print("Server running at: http://127.0.0.1:5000")
    print("="*50 + "\n")
    app.run(debug=True, port=5000)
