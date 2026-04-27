"""
Netra — Real-Time Packet Sniffer using Scapy
Captures live network traffic on the host machine.
"""

import threading
import csv
import os
from datetime import datetime
from collections import deque

try:
    from scapy.all import sniff, IP, TCP, UDP, ICMP, conf
    SCAPY_AVAILABLE = True
except ImportError:
    SCAPY_AVAILABLE = False

# ===== PORT TO SERVICE MAPPING =====
PORT_SERVICE_MAP = {
    20: "FTP-Data", 21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP",
    53: "DNS", 67: "DHCP", 68: "DHCP", 69: "TFTP", 80: "HTTP",
    110: "POP3", 119: "NNTP", 123: "NTP", 135: "RPC", 137: "NetBIOS",
    138: "NetBIOS", 139: "NetBIOS", 143: "IMAP", 161: "SNMP",
    162: "SNMP-Trap", 389: "LDAP", 443: "HTTPS", 445: "SMB",
    465: "SMTPS", 514: "Syslog", 587: "SMTP", 993: "IMAPS",
    995: "POP3S", 1433: "MSSQL", 1521: "Oracle", 3306: "MySQL",
    3389: "RDP", 5432: "PostgreSQL", 5900: "VNC", 6379: "Redis",
    8080: "HTTP-Alt", 8443: "HTTPS-Alt", 27017: "MongoDB"
}


class PacketSniffer:
    """
    Real-time packet sniffer that captures live network traffic
    using Scapy and stores results in CSV + in-memory buffer.
    """

    def __init__(self, csv_file="network_traffic.csv", log_file="logs.txt", max_buffer=500):
        self.csv_file = csv_file
        self.log_file = log_file
        self.is_running = False
        self.sniffer_thread = None
        self.packet_count = 0
        self.total_bytes = 0
        self.lock = threading.Lock()

        # In-memory ring buffer for recent packets (for live streaming)
        self.packet_buffer = deque(maxlen=max_buffer)

        # Protocol counters
        self.protocol_counts = {"TCP": 0, "UDP": 0, "ICMP": 0}

        # Ensure CSV has headers
        self._init_csv()

    def _init_csv(self):
        """Create the CSV file with headers if it doesn't exist or is empty."""
        if not os.path.exists(self.csv_file) or os.path.getsize(self.csv_file) == 0:
            with open(self.csv_file, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([
                    "Time", "Source_IP", "Destination_IP", "Protocol",
                    "Packet_Size", "Source_Port", "Destination_Port"
                ])

    def _write_log(self, message):
        """Append a timestamped log entry."""
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"{ts} - {message}\n")
        except Exception:
            pass

    def _process_packet(self, pkt):
        """Callback: extract fields from a captured Scapy packet."""
        if not self.is_running:
            return

        if not pkt.haslayer(IP):
            return

        try:
            ip_layer = pkt[IP]
            src_ip = ip_layer.src
            dst_ip = ip_layer.dst
            size = len(pkt)
            timestamp = datetime.now().strftime("%H:%M:%S")

            # Determine protocol and ports
            protocol = "OTHER"
            src_port = 0
            dst_port = 0

            if pkt.haslayer(TCP):
                protocol = "TCP"
                src_port = pkt[TCP].sport
                dst_port = pkt[TCP].dport
            elif pkt.haslayer(UDP):
                protocol = "UDP"
                src_port = pkt[UDP].sport
                dst_port = pkt[UDP].dport
            elif pkt.haslayer(ICMP):
                protocol = "ICMP"
                src_port = 0
                dst_port = 0

            # Skip non-IP-based protocols we don't track
            if protocol == "OTHER":
                return

            # Derive service name from destination port
            service = PORT_SERVICE_MAP.get(dst_port, "Unknown")

            record = {
                "Time": timestamp,
                "Source_IP": src_ip,
                "Destination_IP": dst_ip,
                "Protocol": protocol,
                "Packet_Size": size,
                "Source_Port": src_port,
                "Destination_Port": dst_port,
                "Service": service
            }

            with self.lock:
                self.packet_count += 1
                self.total_bytes += size
                if protocol in self.protocol_counts:
                    self.protocol_counts[protocol] += 1

                # Add to ring buffer
                self.packet_buffer.append(record)

                # Append to CSV (without Service column to keep CSV format consistent)
                try:
                    with open(self.csv_file, "a", newline="", encoding="utf-8") as f:
                        writer = csv.writer(f)
                        writer.writerow([
                            timestamp, src_ip, dst_ip, protocol,
                            size, src_port, dst_port
                        ])
                except Exception:
                    pass

        except Exception:
            pass

    def _sniff_loop(self):
        """Run the Scapy sniffer — this blocks until stopped."""
        try:
            self._write_log("[SNIFFER] Real-time packet capture started")
            # Use store=0 for memory efficiency; stop_filter checks our flag
            sniff(
                prn=self._process_packet,
                store=0,
                stop_filter=lambda _: not self.is_running,
                # Capture only IP traffic to reduce noise
                filter="ip",
                # Timeout every 1s to check if we should stop
                timeout=1
            )
        except Exception as e:
            self._write_log(f"[SNIFFER ERROR] {e}")

        # If we're still supposed to be running, restart (timeout triggered)
        if self.is_running:
            self._sniff_loop()

    def start(self):
        """Start capturing packets in a background thread."""
        if self.is_running:
            return {"success": False, "message": "Already running"}

        if not SCAPY_AVAILABLE:
            return {"success": False, "message": "Scapy is not installed"}

        self.is_running = True
        self.packet_count = 0
        self.total_bytes = 0
        self.protocol_counts = {"TCP": 0, "UDP": 0, "ICMP": 0}
        self.packet_buffer.clear()

        self.sniffer_thread = threading.Thread(target=self._sniff_loop, daemon=True)
        self.sniffer_thread.start()

        self._write_log("[START] Real-time monitoring session initiated")
        return {"success": True, "message": "Real-time packet capture started"}

    def stop(self):
        """Stop the packet capture."""
        if not self.is_running:
            return {"success": False, "message": "Not running"}

        self.is_running = False

        # Wait briefly for the sniffer thread to finish
        if self.sniffer_thread and self.sniffer_thread.is_alive():
            self.sniffer_thread.join(timeout=3)

        self._write_log(
            f"[STOP] Monitoring ended | Packets: {self.packet_count} | "
            f"Data: {round(self.total_bytes / 1024, 2)} KB"
        )
        return {
            "success": True,
            "message": "Monitoring stopped",
            "packets_captured": self.packet_count,
            "total_bytes": self.total_bytes
        }

    def get_live_packets(self, count=50):
        """Return the most recent `count` packets from the ring buffer."""
        with self.lock:
            packets = list(self.packet_buffer)
            return packets[-count:]

    def get_stats(self):
        """Return current session statistics."""
        with self.lock:
            avg_size = round(self.total_bytes / self.packet_count, 2) if self.packet_count > 0 else 0
            return {
                "total": self.packet_count,
                "tcp": self.protocol_counts.get("TCP", 0),
                "udp": self.protocol_counts.get("UDP", 0),
                "icmp": self.protocol_counts.get("ICMP", 0),
                "avg_size": avg_size,
                "total_data": round(self.total_bytes / 1024, 2),
                "is_running": self.is_running
            }
