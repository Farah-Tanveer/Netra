# 👁️ Netra — Network Intelligence Platform

Netra is a premium, real-time network traffic monitoring and analysis platform. Designed for security professionals and network administrators, it provides sub-millisecond visibility into every packet flowing through your infrastructure with a stunning cyber-themed interface.

![Netra Landing Page Preview](https://raw.githubusercontent.com/Farah-Tanveer/Netra/main/static/images/Screenshot1.png)

---

![Netra Dashboard Preview](https://raw.githubusercontent.com/Farah-Tanveer/Netra/main/static/images/Screenshot2.png)

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

### 🛡️ Security Features (New)
- **User Registration**: Users can now create unique accounts for secure access management.
- **JWT Authentication**: Secure session management using industry-standard JSON Web Tokens.
- **DoS Protection**: Real-time rate limiting and IP blocking to prevent Denial of Service attacks.
- **Password Hashing**: Passwords are securely hashed using PBKDF2 with SHA-256 (First-Principles).
- **Security Headers**: Hardened with CSP, HSTS, XSS Protection, and No-Sniff headers.

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

## 📂 Project Structure
- `app.py`: Main Flask application server.
- `static/`: Frontend assets (CSS, JS, Images).
- `templates/`: HTML templates for Dashboard and Stats.
- `requirements.txt`: Python dependencies.
- `Procfile`: Deployment configuration for Gunicorn.
- `BCSF24M016_report.pdf`: Updated project documentation.

## 🚀 Deployment Guide (Render)
1. **Prepare Repository**: Ensure all files are committed to your GitHub repository.
2. **Create New Web Service**: On Render, click "New" -> "Web Service".
3. **Connect Repository**: Select your Netra repository.
4. **Configure Settings**:
   - **Environment**: `Python`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
5. **Environment Variables**: Add the following in the Render Dashboard:
   - `SECRET_KEY`: (Your secret key)
   - `ADMIN_PASSWORD`: (Your desired default admin password)
6. **Deploy**: Click "Create Web Service". Render will automatically build and launch Netra.

## 🛡️ Security Configuration
- **HTTPS**: Render provides automatic SSL.
- **Secrets**: Use environment variables for sensitive data.
- **Persistence**: Note that Render's free tier has an ephemeral file system. Captures and logs will reset on every redeploy. For persistent storage, consider attaching a Render Disk or using an external database.

## 📝 License
This project is licensed under the MIT License - see the LICENSE file for details.
