from flask import Flask, render_template, request, redirect
import pandas as pd

from datetime import datetime

def write_log(message):
    with open("logs.txt", "a") as f:
        time_stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"{time_stamp} - {message}\n")
app = Flask(__name__)

monitoring = False

# Port → Service Mapping
port_service_map = {
    80: "HTTP",
    443: "HTTPS",
    53: "DNS",
    22: "SSH",
    67: "DHCP",
    161: "SNMP"
}

@app.route('/', methods=['GET', 'POST'])
def home():
    global monitoring

    data = []

    # Default statistics
    stats = {
        "total": 0,
        "tcp": 0,
        "udp": 0,
        "icmp": 0,
        "avg_size": 0
    }

    if monitoring:
        df = pd.read_csv("network_traffic.csv")

        # Add Service Column
        services = []
        for port in df["Destination_Port"]:
            service = port_service_map.get(port, "Unknown")
            services.append(service)

        df["Service"] = services

        # Apply Filters
        protocol = request.form.get("protocol")
        src_ip = request.form.get("src_ip")
        dest_ip = request.form.get("dest_ip")

        if protocol and protocol != "ALL":
            df = df[df["Protocol"] == protocol]

        if src_ip:
            df = df[df["Source_IP"] == src_ip]

        if dest_ip:
            df = df[df["Destination_IP"] == dest_ip]

        # Generate Statistics
        stats["total"] = len(df)

        stats["tcp"] = len(df[df["Protocol"] == "TCP"])

        stats["udp"] = len(df[df["Protocol"] == "UDP"])

        stats["icmp"] = len(df[df["Protocol"] == "ICMP"])

        if len(df) > 0:
            stats["avg_size"] = round(df["Packet_Size"].mean(), 2)

        data = df.to_dict(orient="records")

    logs = []

    try:
        with open("logs.txt", "r") as f:
            logs = f.readlines()
    except:
        logs = []

    return render_template(
        "index.html",
        data=data,
        monitoring=monitoring,
        stats=stats,
        logs=logs
)


@app.route('/start', methods=['POST'])
def start_monitoring():
    global monitoring
    monitoring = True

    write_log("Monitoring Started")

    return redirect('/')


@app.route('/stop', methods=['POST'])
def stop_monitoring():
    global monitoring
    monitoring = False

    write_log("Monitoring Stopped")

    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)