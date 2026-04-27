# Netra — Network Traffic Monitoring and Analysis Platform

## Project Report

---

### Student Project — Computer Networks

**Project Title:** Network Traffic Monitoring and Analysis Platform  
**Tool Name:** Netra  
**Programming Language:** Python  
**Framework:** Flask (Backend), HTML/CSS/JavaScript (Frontend)  
**Date:** April 2026

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [System Architecture](#2-system-architecture)
3. [Implementation Details](#3-implementation-details)
4. [Dataset Description](#4-dataset-description)
5. [Screenshots and Results](#5-screenshots-and-results)
6. [Conclusion](#6-conclusion)

---

## 1. Introduction

### 1.1 Problem Statement

Modern networks generate massive volumes of traffic every second. Understanding this traffic — who is communicating, what protocols are being used, and how much data is flowing — is essential for network administrators, security analysts, and anyone studying computer networks. This project addresses the need for a tool that can capture, display, filter, and analyze live network traffic in an accessible, web-based interface.

### 1.2 Objectives

The primary objectives of this project are:

- **Capture real-time network packets** from the host machine's network interface using the Scapy library.
- **Display packet-level details** including source/destination IP addresses, protocols (TCP, UDP, ICMP), port numbers, and derived service names.
- **Provide filtering capabilities** to let users narrow down traffic by protocol type, source IP, and destination IP.
- **Compute and display statistics** such as total packet count, per-protocol counts, average packet size, and data volume.
- **Maintain system logs** to record monitoring session events with timestamps.
- **Present all information** through a clean, well-organized web-based interface built with standard HTML, CSS, and JavaScript.

### 1.3 Scope

The system is designed as a single-user, locally-hosted monitoring platform. It captures live IP traffic (TCP, UDP, ICMP) from the machine's active network interface and stores the captured data in a CSV file for persistence. The web interface runs on Flask at `http://127.0.0.1:5000`.

---

## 2. System Architecture

### 2.1 High-Level Architecture

The system follows a **three-tier architecture** consistent with software engineering best practices:

```
┌─────────────────────────────────────────────────┐
│             PRESENTATION LAYER                  │
│  (HTML Templates + CSS + JavaScript)            │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐        │
│  │  Landing  │ │Dashboard │ │  Stats   │        │
│  │  Page     │ │  Page    │ │  Page    │        │
│  └──────────┘ └──────────┘ └──────────┘        │
├─────────────────────────────────────────────────┤
│             APPLICATION LAYER                   │
│  (Flask REST API — app.py)                      │
│  ┌────────────────────────────────────────────┐ │
│  │  /api/start-monitoring  (POST)             │ │
│  │  /api/stop-monitoring   (POST)             │ │
│  │  /api/live-packets      (GET)              │ │
│  │  /api/traffic-data      (GET)              │ │
│  │  /api/stats             (GET)              │ │
│  │  /api/logs              (GET)              │ │
│  │  /api/status            (GET)              │ │
│  └────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────┤
│             DATA LAYER                          │
│  ┌─────────────────┐ ┌──────────┐ ┌──────────┐ │
│  │ PacketSniffer   │ │logs.txt  │ │stats.json│ │
│  │ (Scapy Thread)  │ │          │ │          │ │
│  │       ↓         │ └──────────┘ └──────────┘ │
│  │ network_traffic │                            │
│  │     .csv        │                            │
│  └─────────────────┘                            │
└─────────────────────────────────────────────────┘
```

### 2.2 Component Overview

| Component | File | Purpose |
|---|---|---|
| Flask Backend | `app.py` | Routes, API endpoints, request handling |
| Packet Sniffer | `utils/packet_reader.py` | Real-time Scapy capture in background thread |
| Landing Page | `templates/index.html` | Project introduction and navigation |
| Dashboard | `templates/dashboard.html` | Live monitoring, filters, packet table, logs |
| Statistics Page | `templates/stats.html` | Protocol distribution, top IPs, top ports |
| Frontend Logic | `static/script.js` | API calls, UI updates, auto-refresh, filters |
| Stylesheet | `static/style.css` | Dark/light theming, responsive layout |
| Dataset | `network_traffic.csv` | Captured packet records (persistent storage) |
| System Logs | `logs.txt` | Timestamped event log |
| Session Stats | `stats.json` | Persistent session count and totals |

### 2.3 Technology Stack

| Technology | Role |
|---|---|
| **Python 3** | Core programming language |
| **Flask** | Lightweight web framework for backend |
| **Scapy** | Real-time packet capture and protocol parsing |
| **Pandas** | CSV data reading, filtering, and statistical analysis |
| **HTML5** | Page structure and semantic markup |
| **CSS3** | Styling, dark/light themes, responsive design |
| **JavaScript (ES6)** | Asynchronous API calls, DOM updates, interactivity |

---

## 3. Implementation Details

### 3.1 Real-Time Packet Sniffing (Extra Credit Feature)

The core differentiator of this project is its use of **real-time packet capture** rather than simulated data. This is implemented in the `PacketSniffer` class (`utils/packet_reader.py`).

**How it works:**

1. When the user clicks **Start**, the Flask backend calls `sniffer.start()`.
2. A **daemon thread** is spawned that runs Scapy's `sniff()` function with an `ip` BPF filter.
3. Each captured packet triggers a callback (`_process_packet`) that extracts:
   - Source and Destination IP addresses (from the IP layer)
   - Protocol type — TCP, UDP, or ICMP (from layer inspection)
   - Source and Destination port numbers (from TCP/UDP layers; 0 for ICMP)
   - Packet size in bytes (`len(pkt)`)
   - Timestamp at capture time
4. Extracted data is stored in two places simultaneously:
   - **In-memory ring buffer** (deque, max 500 entries) for instant live display
   - **CSV file** (`network_traffic.csv`) for persistent storage and historical analysis
5. When the user clicks **Stop**, the sniffer thread is gracefully terminated.

**Thread safety** is ensured via `threading.Lock` on all shared data structures.

### 3.2 Port-to-Service Mapping

The system maps well-known port numbers to human-readable service names. Over **35 port mappings** are included:

| Port | Service | Port | Service |
|------|---------|------|---------|
| 20 | FTP-Data | 443 | HTTPS |
| 21 | FTP | 445 | SMB |
| 22 | SSH | 587 | SMTP |
| 25 | SMTP | 993 | IMAPS |
| 53 | DNS | 3306 | MySQL |
| 80 | HTTP | 3389 | RDP |
| 110 | POP3 | 5432 | PostgreSQL |
| 143 | IMAP | 8080 | HTTP-Alt |
| 161 | SNMP | ... | ... |

### 3.3 Filter System

The dashboard provides three filter dimensions:

1. **Protocol Type** — Dropdown menu with options: All Protocols, TCP, UDP, ICMP
2. **Source IP** — Text input to filter by exact source IP address
3. **Destination IP** — Text input to filter by exact destination IP address

Filters are applied server-side using Pandas DataFrame operations for historical data and Python list comprehension for live data. The user can apply filters with the **Filter** button and reset all filters with the **Reset** button.

### 3.4 Statistics Generation

The system computes the following statistics:

| Statistic | Description |
|---|---|
| Total Packets | Count of all captured/stored packets |
| TCP Packets | Count of TCP protocol packets |
| UDP Packets | Count of UDP protocol packets |
| ICMP Packets | Count of ICMP protocol packets |
| Average Packet Size | Mean of all packet sizes in bytes |
| Total Data | Sum of all packet sizes (displayed in KB) |
| Unique Source IPs | Count of distinct source addresses |
| Unique Destination IPs | Count of distinct destination addresses |
| Top 5 Source IPs | Most active source addresses |
| Top 5 Destination Ports | Most frequently accessed services |
| Protocol Distribution | Percentage breakdown by protocol |

### 3.5 Logging System

All system events are recorded in `logs.txt` with timestamps:

- Application startup (`[INIT]`)
- Monitoring start (`[START]`)
- Monitoring stop with packet count and data volume (`[STOP]`)
- Sniffer thread lifecycle (`[SNIFFER]`)
- Errors (`[ERROR]`)

Logs are displayed in the dashboard's **System Logs** panel with color-coded entries.

### 3.6 Frontend Interface

The web interface consists of three pages:

**Landing Page (`/`):**
- Project introduction with animated hero section
- Feature cards explaining system capabilities
- Technology stack display
- Contact form

**Dashboard (`/dashboard`):**
- Start/Stop monitoring buttons
- Protocol/Source IP/Destination IP filters with Filter and Reset buttons
- Six statistics cards (Packets, TCP, UDP, ICMP, Avg Size, Data)
- Live packet table with columns: Time, Source IP, Destination IP, Protocol, Src Port, Dst Port, Service, Size
- System Logs panel with color-coded entries

**Statistics Page (`/stats`):**
- Summary cards (Total Packets, Unique Sources, Unique Destinations, Avg Packet Size, Total Data)
- Protocol distribution with percentage bars
- Top Source IPs listing
- Top Destination Ports with service names

---

## 4. Dataset Description

### 4.1 Dataset File

The dataset is stored in `network_traffic.csv` and is **automatically populated by the real-time packet sniffer**. It is not manually created or simulated — every record represents a genuine packet captured from the network.

### 4.2 Dataset Schema

| Field | Type | Example | Description |
|---|---|---|---|
| Time | String | `21:17:03` | Capture timestamp (HH:MM:SS) |
| Source_IP | String | `192.168.1.5` | IP address of the sender |
| Destination_IP | String | `8.8.8.8` | IP address of the receiver |
| Protocol | String | `TCP` | Protocol type (TCP/UDP/ICMP) |
| Packet_Size | Integer | `512` | Size of the packet in bytes |
| Source_Port | Integer | `52341` | Sender's port number |
| Destination_Port | Integer | `80` | Receiver's port number |

### 4.3 Sample Records

```
Time,Source_IP,Destination_IP,Protocol,Packet_Size,Source_Port,Destination_Port
21:17:03,142.250.187.74,10.49.78.82,TCP,70,443,64969
21:17:03,10.49.78.35,239.255.255.250,UDP,179,1900,1900
21:17:03,10.49.72.180,10.49.79.255,UDP,92,137,137
21:17:04,8.8.8.8,10.49.78.82,TCP,127,443,65278
```

---

## 5. Screenshots and Results

### 5.1 Test Results

During development testing, the system was verified to work correctly:

| Test | Result |
|---|---|
| Start monitoring via API | ✅ Success — Scapy thread started |
| Live packet capture | ✅ 2,211 packets captured in ~7 seconds |
| Stop monitoring via API | ✅ Thread stopped, stats saved |
| Filter by protocol | ✅ Correct subset returned |
| Filter by IP | ✅ Correct subset returned |
| Reset filters | ✅ All filters cleared, full data shown |
| Statistics computation | ✅ All stats calculated correctly |
| Log recording | ✅ All events logged with timestamps |
| CSV persistence | ✅ Data survives server restarts |
| Dark/Light theme | ✅ Both themes render correctly |

### 5.2 Screenshots

*(Insert screenshots of the running system here)*

- Screenshot 1: Landing Page
- Screenshot 2: Dashboard — Before Monitoring
- Screenshot 3: Dashboard — During Live Capture (packets flowing in table)
- Screenshot 4: Dashboard — System Logs Panel
- Screenshot 5: Statistics Page

---

## 6. Conclusion

### 6.1 Summary

Netra is a fully functional network traffic monitoring and analysis platform built with Python (Flask + Scapy) and standard web technologies (HTML, CSS, JavaScript). It goes beyond the basic project requirements by implementing **real-time packet sniffing** using the Scapy library, capturing actual network traffic instead of relying on simulated data.

### 6.2 Requirements Fulfillment

All functional, interface, dataset, filter, and statistics requirements specified in the project brief have been implemented and verified. Additionally, the real-time packet sniffing bonus feature has been implemented.

### 6.3 Key Takeaways

- **Networking Concepts Applied:** IP addressing, TCP/UDP/ICMP protocol identification, port-to-service mapping, packet structure analysis.
- **Software Engineering Practices:** Three-tier architecture, separation of concerns, RESTful API design, thread safety, error handling, logging.
- **Programming Skills:** Python backend development, asynchronous JavaScript, responsive CSS, API integration.

### 6.4 Future Improvements

- Packet payload inspection for deeper protocol analysis
- Export functionality (PDF/CSV download from the interface)
- Persistent database storage (SQLite) for large-scale data retention
- Network anomaly detection using statistical thresholds

---

**End of Report**
