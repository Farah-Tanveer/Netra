import warnings
warnings.filterwarnings("ignore")
from fpdf import FPDF

class Report(FPDF):
    def header(self):
        self.set_font("Helvetica","B",10)
        self.set_text_color(100,100,100)
        self.cell(0,8,"Netra - Network Traffic Monitoring Platform | Project Report",align="C",new_x="LMARGIN",new_y="NEXT")
        self.line(10,self.get_y(),200,self.get_y())
        self.ln(4)
    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica","I",8)
        self.set_text_color(128,128,128)
        self.cell(0,10,f"Page {self.page_no()}/{{nb}}",align="C")
    def section(self,num,title):
        self.set_font("Helvetica","B",14)
        self.set_text_color(0,80,160)
        self.cell(0,10,f"{num}. {title}",new_x="LMARGIN",new_y="NEXT")
        self.line(10,self.get_y(),200,self.get_y())
        self.ln(3)
    def sub(self,title):
        self.set_font("Helvetica","B",11)
        self.set_text_color(40,40,40)
        self.cell(0,8,title,new_x="LMARGIN",new_y="NEXT")
        self.ln(1)
    def body(self,txt):
        self.set_font("Helvetica","",10)
        self.set_text_color(30,30,30)
        self.multi_cell(0,5.5,txt)
        self.ln(2)
    def bullet(self,txt):
        self.set_font("Helvetica","",10)
        self.set_text_color(30,30,30)
        self.cell(8,5.5,"  - ")
        self.multi_cell(0,5.5,txt)
        self.ln(1)

pdf = Report()
pdf.alias_nb_pages()
pdf.set_auto_page_break(auto=True,margin=20)

# TITLE PAGE
pdf.add_page()
pdf.ln(50)
pdf.set_font("Helvetica","B",28)
pdf.set_text_color(0,70,150)
pdf.cell(0,15,"NETRA",align="C",new_x="LMARGIN",new_y="NEXT")
pdf.set_font("Helvetica","",14)
pdf.set_text_color(60,60,60)
pdf.cell(0,10,"Network Traffic Monitoring & Analysis Platform",align="C",new_x="LMARGIN",new_y="NEXT")
pdf.ln(8)
pdf.line(60,pdf.get_y(),150,pdf.get_y())
pdf.ln(12)
pdf.set_font("Helvetica","B",13)
pdf.set_text_color(0,0,0)
pdf.cell(0,8,"Project Report",align="C",new_x="LMARGIN",new_y="NEXT")
pdf.ln(20)
pdf.set_font("Helvetica","",11)
info=[("Course","Computer Networks"),("Author","Farah Tanveer"),("Institution","University of Karachi (UBIT)"),("Date","May 2026")]
for k,v in info:
    pdf.set_font("Helvetica","B",11)
    pdf.cell(60,8,k+":",align="R")
    pdf.set_font("Helvetica","",11)
    pdf.cell(0,8,"  "+v,new_x="LMARGIN",new_y="NEXT")

# TABLE OF CONTENTS
pdf.add_page()
pdf.set_font("Helvetica","B",16)
pdf.set_text_color(0,70,150)
pdf.cell(0,12,"Table of Contents",new_x="LMARGIN",new_y="NEXT")
pdf.line(10,pdf.get_y(),200,pdf.get_y())
pdf.ln(6)
toc=["Abstract","Introduction","Problem Statement & Objectives","Literature Review / Background Study","System Architecture & Design","Technology Stack","Module Descriptions","Implementation Details","Key Features","API Endpoints & Routes","Data Flow & Workflow","Testing & Results","Security Considerations","Future Enhancements","Conclusion","References"]
for i,t in enumerate(toc,1):
    pdf.set_font("Helvetica","",11)
    pdf.set_text_color(30,30,30)
    pdf.cell(0,7,f"  {i}.  {t}",new_x="LMARGIN",new_y="NEXT")

# 1. ABSTRACT
pdf.add_page()
pdf.section("1","Abstract")
pdf.body("Netra is a real-time network traffic monitoring and analysis platform developed as a semester project for the Computer Networks course. The platform captures live network packets using the Scapy library in Python, processes and logs them, and presents the data through a modern, responsive web dashboard built with Flask. It supports protocol-level filtering (TCP, UDP, ICMP), IP-based search, CSV data export, and comprehensive statistical analysis including protocol distribution, top source IPs, and destination port analytics. The system demonstrates fundamental networking concepts such as packet sniffing, protocol identification, port-to-service mapping, and real-time data streaming in a practical, user-friendly application.")

# 2. INTRODUCTION
pdf.section("2","Introduction")
pdf.body("Computer networks form the backbone of modern digital communication. Understanding how data traverses a network at the packet level is essential for network administrators, security professionals, and students of computer science. Netra (meaning 'eye' in Sanskrit) is designed to provide real-time visibility into network traffic, enabling users to monitor, capture, analyze, and export packet data through an intuitive web-based interface.")
pdf.body("The project bridges the gap between theoretical networking concepts taught in academia and their practical application. By implementing a live packet sniffer integrated with a full-stack web application, Netra demonstrates OSI/TCP-IP model concepts, protocol behavior, and traffic analysis in an accessible manner.")

# 3. PROBLEM STATEMENT
pdf.section("3","Problem Statement & Objectives")
pdf.sub("Problem Statement")
pdf.body("Network traffic analysis tools like Wireshark are powerful but complex for beginners. There is a need for a lightweight, web-based, user-friendly platform that allows students and junior administrators to monitor and understand network traffic without steep learning curves.")
pdf.sub("Objectives")
for o in ["Design and implement a real-time packet sniffing engine using Scapy","Build a responsive web dashboard for live traffic visualization","Provide multi-criteria filtering (Protocol, Source IP, Destination IP)","Generate statistical analysis of captured traffic (protocol distribution, top sources, port analytics)","Enable CSV export of captured data for offline analysis","Implement session-based monitoring with persistent logging","Demonstrate core Computer Networks concepts in a practical application"]:
    pdf.bullet(o)

# 4. LITERATURE REVIEW
pdf.section("4","Literature Review / Background Study")
pdf.sub("4.1 Packet Sniffing")
pdf.body("Packet sniffing is the practice of capturing data packets as they travel across a network. Tools like Wireshark, tcpdump, and Scapy enable this functionality. Scapy, a Python-based interactive packet manipulation library, provides granular control over packet capture and dissection, making it ideal for educational projects.")
pdf.sub("4.2 TCP/IP Protocol Suite")
pdf.body("The TCP/IP model defines how data is packetized, addressed, transmitted, routed, and received. Key protocols relevant to this project include: TCP (Transmission Control Protocol) for reliable, connection-oriented communication; UDP (User Datagram Protocol) for lightweight, connectionless communication; ICMP (Internet Control Message Protocol) for diagnostic and error-reporting purposes; and IP (Internet Protocol) for addressing and routing.")
pdf.sub("4.3 Web-Based Monitoring Systems")
pdf.body("Modern network monitoring solutions increasingly adopt web-based interfaces for accessibility. Tools like Nagios, Zabbix, and PRTG use dashboards for real-time visualization. Netra follows this paradigm using Flask as a lightweight web framework suitable for rapid prototyping and academic demonstration.")

# 5. SYSTEM ARCHITECTURE
pdf.section("5","System Architecture & Design")
pdf.sub("5.1 Architecture Overview")
pdf.body("Netra follows a three-tier architecture:\n  1. Presentation Layer - HTML/CSS/JS frontend with responsive UI\n  2. Application Layer - Flask web server handling routing, API endpoints, and business logic\n  3. Data Layer - CSV file storage, JSON stats persistence, and in-memory ring buffer")
pdf.sub("5.2 Directory Structure")
pdf.set_font("Courier","",9)
for line in ["Netra/","  app.py              # Main Flask application (287 lines)","  network_traffic.csv  # Captured packet data","  logs.txt             # System event logs","  stats.json           # Persistent session statistics","  utils/","    __init__.py         # Module exports","    packet_reader.py    # PacketSniffer class (229 lines)","  templates/","    index.html          # Landing page (174 lines)","    dashboard.html      # Monitoring dashboard (181 lines)","    stats.html          # Statistics page (148 lines)","  static/","    style.css           # Global stylesheet (305 lines)","    script.js           # Frontend logic (456 lines)","    images/             # Background assets"]:
    pdf.cell(0,4.5,"    "+line,new_x="LMARGIN",new_y="NEXT")
pdf.ln(4)

# 6. TECHNOLOGY STACK
pdf.section("6","Technology Stack")
rows=[("Python 3.13","Core programming language"),("Flask","Lightweight WSGI web framework"),("Scapy","Packet capture and dissection library"),("Pandas","Data manipulation and CSV analysis"),("HTML5 / CSS3","Semantic markup and premium styling"),("JavaScript (ES6+)","Frontend interactivity and async API calls"),("Flask-CORS","Cross-Origin Resource Sharing support"),("JSON","Statistics persistence format"),("CSV","Packet data storage format")]
pdf.set_font("Helvetica","B",10)
pdf.set_fill_color(0,70,150)
pdf.set_text_color(255,255,255)
pdf.cell(55,7,"Technology",border=1,fill=True)
pdf.cell(0,7,"Purpose",border=1,fill=True,new_x="LMARGIN",new_y="NEXT")
pdf.set_text_color(30,30,30)
for i,(t,p) in enumerate(rows):
    pdf.set_fill_color(240,245,255) if i%2==0 else pdf.set_fill_color(255,255,255)
    pdf.set_font("Helvetica","B",10)
    pdf.cell(55,7,t,border=1,fill=True)
    pdf.set_font("Helvetica","",10)
    pdf.cell(0,7,p,border=1,fill=True,new_x="LMARGIN",new_y="NEXT")
pdf.ln(4)

# 7. MODULE DESCRIPTIONS
pdf.section("7","Module Descriptions")
pdf.sub("7.1 PacketSniffer (utils/packet_reader.py)")
pdf.body("The core engine of Netra. This module implements the PacketSniffer class which encapsulates all packet capture functionality:\n- Thread-safe packet capture using Python threading and Scapy\n- In-memory ring buffer (deque with maxlen=500) for real-time streaming\n- Automatic CSV persistence for every captured packet\n- Protocol identification (TCP/UDP/ICMP) with port extraction\n- Port-to-service name mapping (35+ well-known services including HTTP, HTTPS, SSH, DNS, FTP, SMTP, MySQL, PostgreSQL, RDP, etc.)\n- Session statistics tracking (packet count, byte count, protocol distribution)\n- Start/Stop lifecycle management with clean state reset")
pdf.sub("7.2 Flask Application (app.py)")
pdf.body("The application server provides 10 routes including 7 RESTful API endpoints. It manages the sniffer lifecycle, serves HTML templates, handles filtering logic using Pandas DataFrames, computes real-time statistics, and provides system logging with timestamps. Session tracking persists across restarts via stats.json.")
pdf.sub("7.3 Frontend (script.js + templates)")
pdf.body("The frontend is a multi-page application with three views: Landing Page (marketing/intro), Dashboard (real-time monitoring), and Statistics (analytical insights). It uses vanilla JavaScript with async/await for API communication, implements a 1.5-second auto-refresh polling loop during active monitoring, and provides toast notifications, theme toggling (dark/light), scroll animations, and particle effects.")

# 8. IMPLEMENTATION DETAILS
pdf.section("8","Implementation Details")
pdf.sub("8.1 Packet Capture Mechanism")
pdf.body("Scapy's sniff() function is invoked in a daemon thread with a BPF filter 'ip' to capture only IP-layer traffic. The timeout parameter is set to 1 second, after which the sniff loop recursively restarts if monitoring is still active. This design ensures the sniffer remains responsive to stop commands while maintaining continuous capture. Each packet is dissected to extract: timestamp, source/destination IP, protocol type, source/destination ports, and packet size in bytes.")
pdf.sub("8.2 Thread Safety")
pdf.body("A threading.Lock protects all shared state (packet_count, total_bytes, protocol_counts, packet_buffer). The ring buffer uses collections.deque with maxlen=500, providing O(1) append and automatic eviction of oldest entries, ensuring bounded memory usage during extended monitoring sessions.")
pdf.sub("8.3 Data Persistence")
pdf.body("Captured packets are written to network_traffic.csv with columns: Time, Source_IP, Destination_IP, Protocol, Packet_Size, Source_Port, Destination_Port. The CSV is cleared at the start of each new session to provide clean per-session data. Session metadata (total sessions, cumulative packets, cumulative data) persists in stats.json across application restarts.")
pdf.sub("8.4 Frontend Architecture")
pdf.body("The UI uses a glassmorphism design system with CSS custom properties for theming. Key design patterns include: backdrop-filter blur effects, gradient text rendering, CSS Grid for responsive layouts, IntersectionObserver for scroll-triggered animations, and CSS keyframe animations for particle effects and UI micro-interactions.")

# 9. KEY FEATURES
pdf.section("9","Key Features")
features=[("Real-Time Packet Capture","Live sniffing with Scapy, 1.5s polling, instant UI updates"),("Protocol Filtering","Filter by TCP, UDP, or ICMP in real-time"),("IP-Based Search","Filter packets by source or destination IP address"),("Statistical Analysis","Protocol distribution, top 5 source IPs, top 5 destination ports with percentages"),("CSV Export","One-click download of captured traffic data"),("Dark/Light Theme","Persistent theme preference with Ctrl+K keyboard shortcut"),("System Logging","Timestamped event logs for all monitoring actions"),("Responsive Design","Mobile-first layout adapting to all screen sizes"),("Service Identification","Automatic port-to-service mapping (HTTP, DNS, SSH, etc.)"),("Session Management","Clean state reset per session with cumulative statistics")]
for title,desc in features:
    pdf.set_font("Helvetica","B",10)
    pdf.cell(60,6,title+":")
    pdf.set_font("Helvetica","",10)
    pdf.multi_cell(0,6,desc)
    pdf.ln(1)

# 10. API ENDPOINTS
pdf.section("10","API Endpoints & Routes")
apis=[("GET /","Landing page (index.html)"),("GET /dashboard","Dashboard page (dashboard.html)"),("GET /stats","Statistics page (stats.html)"),("GET /api/status","Returns monitoring status and live stats"),("POST /api/start-monitoring","Starts packet capture, clears CSV, increments session count"),("POST /api/stop-monitoring","Stops capture, persists cumulative stats"),("GET /api/live-packets","Returns real-time packets from ring buffer with filters"),("GET /api/traffic-data","Returns filtered historical data from CSV via Pandas"),("GET /api/stats","Returns detailed statistics (protocol dist, top IPs, top ports)"),("GET /api/logs","Returns recent system log entries"),("GET /api/export-csv","Downloads network_traffic.csv as attachment")]
pdf.set_font("Helvetica","B",9)
pdf.set_fill_color(0,70,150)
pdf.set_text_color(255,255,255)
pdf.cell(60,6,"Endpoint",border=1,fill=True)
pdf.cell(0,6,"Description",border=1,fill=True,new_x="LMARGIN",new_y="NEXT")
pdf.set_text_color(30,30,30)
for i,(e,d) in enumerate(apis):
    pdf.set_fill_color(240,245,255) if i%2==0 else pdf.set_fill_color(255,255,255)
    pdf.set_font("Courier","",8)
    pdf.cell(60,6,e,border=1,fill=True)
    pdf.set_font("Helvetica","",9)
    pdf.cell(0,6,d,border=1,fill=True,new_x="LMARGIN",new_y="NEXT")
pdf.ln(4)

# 11. DATA FLOW
pdf.section("11","Data Flow & Workflow")
pdf.body("1. User clicks 'Start Capturing' on the Dashboard\n2. Frontend sends POST /api/start-monitoring\n3. Backend initializes PacketSniffer: clears CSV, resets counters, starts daemon thread\n4. Scapy captures IP packets on the default interface\n5. Each packet is dissected, appended to ring buffer, and written to CSV\n6. Frontend polls GET /api/live-packets every 1.5 seconds\n7. Dashboard renders packet table, updates stat counters in real-time\n8. User clicks 'Stop' - POST /api/stop-monitoring\n9. Backend stops sniffer thread, persists cumulative stats to stats.json\n10. User navigates to Statistics page for deep analysis\n11. Frontend fetches GET /api/stats - backend computes analytics via Pandas\n12. User can export captured data as CSV at any time")

# 12. TESTING
pdf.section("12","Testing & Results")
pdf.body("The application was tested on Windows 10/11 with Python 3.13 and Npcap driver for packet capture. Testing verified:")
for t in ["Successful capture of TCP, UDP, and ICMP packets on local network","Correct protocol identification and port extraction","Accurate port-to-service mapping for well-known services","Real-time UI updates during active monitoring sessions","Proper CSV file generation with valid data formatting","Filter functionality for protocol, source IP, and destination IP","Statistics computation accuracy (percentages, averages, counts)","Theme persistence across page navigation and browser sessions","Clean session reset (CSV cleared, counters zeroed) on new capture","Responsive layout on desktop and mobile viewports","System log accuracy with proper timestamping"]:
    pdf.bullet(t)
pdf.body("Sample test session captured 49 packets with 19.34 KB of data, correctly identifying TCP, UDP, and ICMP protocol distributions with accurate service name resolution.")

# 13. SECURITY
pdf.section("13","Security Considerations")
for s in ["Packet capture requires administrator/root privileges (Npcap on Windows)","CORS is enabled via Flask-CORS for development flexibility","Input validation on API query parameters prevents injection","The application runs on localhost (127.0.0.1) by default for safety","No sensitive packet payload data is stored - only metadata headers","CSV and log files use UTF-8 encoding to prevent encoding attacks"]:
    pdf.bullet(s)

# 14. FUTURE
pdf.section("14","Future Enhancements")
for f in ["Deep Packet Inspection (DPI) for payload-level analysis","Integration with machine learning models for anomaly/intrusion detection","Database backend (SQLite/PostgreSQL) replacing CSV for scalability","WebSocket-based real-time streaming replacing polling","PCAP file import/export for compatibility with Wireshark","User authentication and role-based access control","Network topology visualization and geographic IP mapping","Bandwidth monitoring and alerting thresholds","Docker containerization for easy deployment"]:
    pdf.bullet(f)

# 15. CONCLUSION
pdf.section("15","Conclusion")
pdf.body("Netra successfully demonstrates the practical application of computer networking concepts through a fully functional, real-time network traffic monitoring platform. The project integrates packet sniffing (Scapy), web development (Flask), data analysis (Pandas), and modern UI design into a cohesive system that captures, processes, visualizes, and exports network traffic data. The platform provides an accessible alternative to complex tools like Wireshark for educational purposes, while maintaining extensibility for future enhancements. Through this project, core concepts of the TCP/IP protocol suite, packet structure, port-service associations, and network analysis have been explored and implemented in a hands-on manner.")

# 16. REFERENCES
pdf.section("16","References")
refs=["Kurose, J.F. & Ross, K.W. - Computer Networking: A Top-Down Approach, 8th Edition","Scapy Documentation - https://scapy.readthedocs.io/","Flask Documentation - https://flask.palletsprojects.com/","Pandas Documentation - https://pandas.pydata.org/docs/","RFC 793 - Transmission Control Protocol (TCP)","RFC 768 - User Datagram Protocol (UDP)","RFC 792 - Internet Control Message Protocol (ICMP)","MDN Web Docs - https://developer.mozilla.org/","Npcap Documentation - https://npcap.com/"]
for i,r in enumerate(refs,1):
    pdf.set_font("Helvetica","",10)
    pdf.cell(0,6,f"[{i}] {r}",new_x="LMARGIN",new_y="NEXT")

pdf.output("report.pdf")
print("SUCCESS: report.pdf generated!")
