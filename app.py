from flask import Flask, render_template, request, redirect
import pandas as pd

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

    return render_template(
        "index.html",
        data=data,
        monitoring=monitoring,
        stats=stats
    )


@app.route('/start', methods=['POST'])
def start_monitoring():
    global monitoring
    monitoring = True
    return redirect('/')


@app.route('/stop', methods=['POST'])
def stop_monitoring():
    global monitoring
    monitoring = False
    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)