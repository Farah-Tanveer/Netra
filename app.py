from flask import Flask, render_template, request, redirect
import pandas as pd

app = Flask(__name__)

# Monitoring State
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

@app.route('/')
def home():
    global monitoring

    if monitoring:
        df = pd.read_csv("network_traffic.csv")

        # Service Mapping
        services = []
        for port in df["Destination_Port"]:
            service = port_service_map.get(port, "Unknown")
            services.append(service)

        df["Service"] = services

        data = df.to_dict(orient="records")

    else:
        data = []

    return render_template(
        "index.html",
        data=data,
        monitoring=monitoring
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