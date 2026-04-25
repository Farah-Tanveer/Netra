from flask import Flask, render_template
import pandas as pd

app = Flask(__name__)

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
    # Read CSV file
    df = pd.read_csv("network_traffic.csv")

    # Add Service column
    services = []
    for port in df["Destination_Port"]:
        service = port_service_map.get(port, "Unknown")
        services.append(service)

    df["Service"] = services

    # Convert dataframe to list
    data = df.to_dict(orient="records")

    return render_template("index.html", data=data)

if __name__ == '__main__':
    app.run(debug=True)