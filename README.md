# 👁️ Netra — Network Intelligence Platform

Netra is a premium, real-time network traffic monitoring and analysis platform. Designed for security professionals and network administrators, it provides sub-millisecond visibility into every packet flowing through your infrastructure with a stunning cyber-themed interface.

![Netra Landing Page Preview](https://raw.githubusercontent.com/Farah-Tanveer/Netra/main/static/images/Screenshot1.png) *(Note: Replace with actual screenshot)*

![Netra Dashboard Preview](https://raw.githubusercontent.com/Farah-Tanveer/Netra/main/static/images/Screenshot2.png) *(Note: Replace with actual screenshot)*

## ✨ Key Features

- **🚀 Real-Time Packet Sniffing**: Capture live IP traffic (TCP, UDP, ICMP) with sub-millisecond precision using Scapy.
- **📊 Advanced Analytics**: Detailed protocol distribution, top source/destination analysis, and port usage statistics.
- **🔍 Smart Filtering**: Instantly filter traffic by Protocol, Source IP, or Destination IP to find exactly what you need.
- **💾 Data Portability**: Export all captured traffic to standard CSV format for offline analysis in Excel or Pandas.
- **🌙 Premium Cyber UI**: High-end glassmorphism design with persistent Dark/Light modes and smooth micro-animations.
- **📝 System Logging**: Comprehensive timestamped logs of all monitoring activities and sniffer events.
- **🛠️ Service Identification**: Automatic mapping of destination ports to well-known service names (HTTP, DNS, SSH, etc.).

## 🛠️ Technology Stack

- **Backend**: Python 3.13, Flask, Scapy, Pandas
- **Frontend**: Vanilla JavaScript (ES6+), CSS3 (Glassmorphism), HTML5
- **Data Persistence**: CSV (Traffic Data), JSON (Session Stats), TXT (System Logs)
- **Monitoring**: Multi-threaded Background Sniffer

## 🚀 Getting Started

### Prerequisites

- **Python 3.10+**
- **Npcap (Windows)** or **libpcap (Linux/Mac)**: Required for packet sniffing.
  - *Windows*: Download and install from [npcap.com](https://npcap.com/). Select "Install Npcap in WinPcap API-compatible Mode" during setup.

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Farah-Tanveer/Netra.git
   cd Netra
   ```

2. **Install dependencies:**
   ```bash
   pip install flask flask-cors scapy pandas fpdf2
   ```

3. **Run the application:**
   ```bash
   # Note: Administrator/Root privileges are required for packet sniffing
   python app.py
   ```

4. **Open in browser:**
   Navigate to `http://127.0.0.1:5000`

## 📁 Project Structure

```text
Netra/
├── app.py              # Main Flask server & API routes
├── generate_report.py  # PDF report generation utility
├── network_traffic.csv # Captured packet storage
├── logs.txt            # System event logs
├── stats.json          # Persistent session statistics
├── utils/
│   ├── packet_reader.py # Core PacketSniffer engine (Scapy logic)
│   └── __init__.py
├── static/
│   ├── script.js       # Frontend logic & API communication
│   ├── style.css       # Premium cyber-themed styling
│   └── images/         # UI assets
└── templates/
    ├── index.html      # Modern Landing Page
    ├── dashboard.html  # Live Monitoring Dashboard
    └── stats.html      # Analytical Insights Page
```

## 📄 Project Documentation

A detailed 16-section project report (`report.pdf`) is available in the root directory, covering system architecture, implementation details, and security considerations. This is ideal for academic submissions or technical deep-dives.

## 🎓 Course Information

- **Course**: Computer Networks
- **Instructor**: University of Karachi (UBIT)
- **Project Date**: May 2026

## 👤 Author

**Farah Tanveer**
- GitHub: [@Farah-Tanveer](https://github.com/Farah-Tanveer)

## ⚖️ License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
