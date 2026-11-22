# TIDE: Test Integrity in Developer Environments
## Comprehensive Project Documentation & Computer Networks (CN) PBL Technical Report

---

### Academic Metadata
- **Project Title:** TIDE — Test Integrity in Developer Environments
- **Domain:** Computer Networks, Distributed Systems & Network Security
- **Project Type:** Project-Based Learning (PBL) Course Submission
- **Target OS / Environment:** Windows 10/11 Lab Environments (60+ Nodes)
- **Core Technology Stack:** Python 3.12, FastAPI, WebSockets (RFC 6455), Asyncio, UDP/IP Sockets, Win32 API, React, Vite, TypeScript, SQLite, Jev AI / Groq / Heuristics

---

## 1. Executive Summary & Abstract

Traditional computer science and engineering laboratory examinations face a fundamental architectural dilemma: **students must legitimately utilize native desktop development and analysis tools** (e.g., Visual Studio Code, Code::Blocks, GCC compilers, Command Prompts, Wireshark, VMware, Packet Tracer), yet modern AI coding assistants (ChatGPT, Claude, Copilot, DeepSeek) and illicit local collaboration allow trivial academic dishonesty.

Existing commercial proctoring solutions rely on **Kiosk Lockdown Browsers** (such as Safe Exam Browser or Respondus). These platforms enforce integrity by constraining the operating system into a single locked browser window. In computer science and networking laboratories, this approach completely fails because students cannot compile C/C++ code, capture network packets in Wireshark, or configure virtual machines inside a web browser. Consequently, institutions have historically fallen back to physical isolation: **"unplug the LAN cable"**.

Physical cable disconnection fails reliably in practice:
1. Students secretly reconnect Ethernet cables or associate with unauthorized mobile Wi-Fi hotspots / USB tethering.
2. Students access questions early from cloud LMS platforms (Google Classroom, Drive, Webmail) prior to disconnection.
3. Students transfer pre-written solutions via unauthorized peer-to-peer (P2P) local connections or USB drives.
4. Invigilators cannot physically monitor 60 student monitors simultaneously.

**TIDE (Test Integrity in Developer Environments)** solves this by shifting from *rigid desktop lock-down* to **active network and OS-level edge monitoring with a centralized decision and telemetry pipeline**. TIDE deploys a lightweight edge agent (`tide-agent.exe`, ~25 MB) on each student workstation and an authoritative central server (`tide-server`) on the teacher's machine. By default, TIDE operates in **"Internet: Allowed & Monitored"** mode, making it safe to leave network connections active by inspecting browser address bars via Windows UI Automation (closing prohibited AI/cloud sites within milliseconds), monitoring active socket states to detect unauthorized peer-to-peer LAN connections, performing cryptographic pre-exam code inventorying, and synchronizing distributed clocks using **Cristian's Algorithm**.

---

## 2. Problem Statement & Threat Modeling

### 2.1 The Laboratory Environment
In a typical computer networking laboratory:
- **Workstations:** 60 client PCs running Windows 10/11 connected via a local Gigabit Ethernet switch or 802.11ac/ax Wi-Fi access point.
- **Subnet Configuration:** Single Class C or Class B private broadcast domain (e.g., `192.168.1.0/24` or `10.0.0.0/24`).
- **Required Software:** IDEs (VS Code), Network Analyzers (Wireshark), Virtualization (VMware), Shells (`cmd`, `powershell`), Compilers (`gcc`, `python`).

### 2.2 Attack Vectors & TIDE Countermeasures

| # | Attack Vector / Student Exploit | Network & System Exploitation Mechanism | TIDE Countermeasure & Detection Layer |
|---|---|---|---|
| **1** | **Cloud AI Assistants** | HTTPS traffic to `chatgpt.com`, `claude.ai`, `gemini.google.com`, `poe.com`. | **Edge UI Automation & Local Rule Enforcement:** Edge agent reads active browser address bar host every 500ms; automatically issues `Ctrl+W` tab kill; unknown hosts classified via Jev AI decision engine. |
| **2** | **Rogue Network Tethering** | Student enables USB tethering or mobile Wi-Fi hotspot to bypass campus proxy. | **Network Interface & Gateway Monitoring:** OS socket and adapter polling detects new active NICs, Wi-Fi SSID changes (`netsh wlan show interfaces`), or default gateway updates. |
| **3** | **Pre-Test Question Leaks** | Questions distributed via LMS or email prior to physical cable disconnection. | **Controlled Network Ingestion:** Questions exist exclusively inside TIDE server memory/database; distributed over WebSocket only at the exact server start timestamp; assigned by seat parity (Set A: Odd, Set B: Even). |
| **4** | **Peer-to-Peer LAN Collaboration** | Students establish ad-hoc HTTP servers (`python -m http.server`), Netcat listeners, or SMB shares to transmit code. | **Socket State Table Inspection:** Agent polls `psutil.net_connections("inet")` for `ESTABLISHED` TCP connections to RFC 1918 private IP addresses excluding the authoritative teacher server IP. |
| **5** | **Pre-existing Code Reuse** | Reusing assignments or source files stored on the local hard drive or USB thumb drive. | **Cryptographic AST/Winnowing Fingerprinting:** Pre-flight scan inventories local drives, hashing normalized token n-grams; flags file opening or code injection exceeding similarity thresholds. |
| **6** | **Passive Packet Inspection** | Running Wireshark for legitimate network lab exercises. | **Promiscuous Mode Pass-through:** Passive raw socket capture via Npcap does not create `ESTABLISHED` TCP sockets, enabling Wireshark to run without false-positive alerts. |
| **7** | **Agent Termination** | Student terminates the agent process via Task Manager or CLI (`taskkill`). | **Heartbeat Timeout Watchdog:** Missing heartbeats (>10s) trigger server-side state transition to "Agent Offline" (Grey/Red) accompanied by an immutable critical alert. |

---

## 3. High-Level System Architecture & Topology

TIDE implements a **Distributed Client-Server Star Topology** combined with an **Edge-Fog-Cloud Decision Hierarchy**:

```
+-----------------------------------------------------------------------------------+
|                            LOCAL AREA NETWORK (LAN)                               |
|                                                                                   |
|   +------------------------------------+                                          |
|   |         STUDENT PC (SEAT 01)       |                                          |
|   |  +------------------------------+  |                                          |
|   |  |   Native Developer Tools     |  |                                          |
|   |  | (VS Code, Wireshark, Shell)  |  |                                          |
|   |  +--------------+---------------+  |                                          |
|   |                 | (OS Hooks)       |                                          |
|   |  +--------------v---------------+  |                                          |
|   |  |    TIDE Edge Agent Process   |  |                                          |
|   |  | - UDP Discovery Client       |  |                                          |
|   |  | - Window / Host Watcher      |  |                                          |
|   |  | - Socket Connection Watcher  |  |                                          |
|   |  | - Dual Active Probe Engine   |  |                                          |
|   |  | - Local Rule Enforcement     |  |                                          |
|   |  | - Outbox Store & Forward     |  |                                          |
|   |  +--------------+---------------+  |                                          |
|   +-----------------|------------------+                                          |
|                     |                                                             |
|                     | Full-Duplex WebSocket (ws://) + HTTP REST                   |
|                     | Authenticated with 256-bit SHA-256 Tokens                   |
|                     |                                                             |
|   +-----------------v------------------+         +----------------------------+   |
|   |     TEACHER LAPTOP (SERVER)        |         |   TEACHER BROWSER CONSOLE  |   |
|   |  +------------------------------+  |         |  +-----------------------+ |   |
|   |  |  FastAPI + Uvicorn (Port 8765|  |         |  |  React + Vite + TS    | |   |
|   |  |  UDP Discovery Daemon (47800)|  |         |  |  60-Seat Live Matrix  | |   |
|   |  |  WebSocket Hub Router        |  |◄───────►|  |  Evidence Reviewer    | |   |
|   |  |  Cristian's Sync Master Clock|  |   WS    |  |  Code Growth Visualizer| |   |
|   |  |  Ingest & State Machine      |  |         |  +-----------------------+ |   |
|   |  |  SQLite State & Evidence DB  |  |         +----------------------------+   |
|   |  +--------------+---------------+  |                                          |
|   +-----------------|------------------+                                          |
+---------------------|-------------------------------------------------------------+
                      | HTTPS Outbound (Only teacher machine requires internet)
                      v
        +----------------------------+
        |   CLOUD DECISION ENGINE    |
        |  OpenRouter / Jev AI API   |
        | (Classifies Ambiguous URLs)|
        +----------------------------+
```

### 3.1 Component Breakdown

1. **TIDE Agent (`tide_agent`):**
   - Implemented in Python 3.12, compiled to a single standalone executable (`tide-agent.exe`) via PyInstaller.
   - Embeds Windows UI Automation, `pywin32`, `psutil`, `mss` (screenshot capture), and `pywebview` (rendering UI via native Edge WebView2).
   - Functions as an autonomous edge monitor capable of executing local policy rules even during transient network dropouts.

2. **TIDE Server (`tide_server`):**
   - Built on FastAPI, Starlette WebSockets, and Asyncio.
   - Operates a UDP broadcast discovery daemon on port `47800`.
   - Manages exam state transitions, question file encryption/distribution, parity set allocation, Cristian's master clock, and code similarity engines.
   - Stores all state, telemetry, and evidence in SQLite (`tide.db`).

3. **Teacher Console (`console`):**
   - Single Page Application (SPA) built with React 18, Vite, TypeScript, and Tailwind CSS.
   - Connects to the server via `/ws/console` to receive live seat matrix updates, flag feeds, and student code snapshots.

4. **Classifier Pipeline (`tide_server.classify`):**
   - Multi-tier decision pipeline: `Local Cache -> Jev AI (OpenRouter Decisions API) -> Offline Heuristics Fallback`.
   - Evaluates unfamiliar application titles and URLs, returning structured classifications with numerical confidence scores ($p \ge 0.90 \implies \text{Auto-Act}$).

---

## 4. Deep-Dive: Computer Networks Concepts in TIDE

As a Computer Networks PBL submission, TIDE incorporates foundational concepts from every layer of the network protocol stack.

```
+---------------------------------------------------------------------------------------+
| LAYER 7: APPLICATION LAYER                                                            |
| - WebSocket Protocol (RFC 6455) for persistent full-duplex agent/server streaming     |
| - HTTP/1.1 REST APIs with JSON payloads & multipart/form-data MIME uploads           |
| - Dual-Engine Active Internet Probes: HTTP NCSI probe (msftconnecttest) & Cloudflare  |
| - Cloud API Interfacing: HTTPS REST Calls to OpenRouter Decisions API                 |
+---------------------------------------------------------------------------------------+
| LAYER 6: PRESENTATION LAYER                                                           |
| - Base64 Encoding/Decoding of binary evidence (JPEG screenshots) and question files   |
| - Data Serialization: UTF-8 JSON wire framing                                         |
| - Data Compression: ZIP archive creation & extraction for lab submissions             |
+---------------------------------------------------------------------------------------+
| LAYER 5: SESSION LAYER                                                                |
| - Cryptographic Session Tokens: 256-bit URL-safe tokens via secrets module            |
| - One-Way Token Hashing: SHA-256 for secure database storage                          |
| - Session State Machine: Handshake validation, auto-reconnect with exponential backoff|
| - Outbox Pattern: Store-and-Forward queue guaranteeing at-least-once telemetry delivery|
+---------------------------------------------------------------------------------------+
| LAYER 4: TRANSPORT LAYER                                                              |
| - UDP (User Datagram Protocol): Connectionless broadcast discovery on port 47800     |
| - TCP (Transmission Control Protocol): Connection-oriented, reliable byte stream     |
| - Active TCP Handshake Probing: socket.create_connection(("1.1.1.1", 443))            |
| - Transport Connection Inspection: psutil.net_connections("inet") for CONN_ESTABLISHED|
| - Port Multiplexing & Addressing: UDP 47800, TCP 8765, TCP 443, TCP 80               |
+---------------------------------------------------------------------------------------+
| LAYER 3: NETWORK LAYER                                                                |
| - IPv4 Addressing & Subnetting: Broadcast domain containment (255.255.255.255)        |
| - RFC 1918 Private IPv4 Address Filtering: Class A (10/8), Class B (172.16/12),       |
|   Class C (192.168/16) differentiation using ipaddress module                         |
| - Rogue LAN Peer Detection: Identifying inter-workstation communication               |
| - Routing Table & Gateway Inspection: Detecting rogue default routes (hotspots)       |
+---------------------------------------------------------------------------------------+
| LAYER 1 & 2: PHYSICAL & DATA LINK LAYERS                                              |
| - Network Interface Card (NIC) Monitoring: Polling interface operational state (isup) |
| - IEEE 802.11 (Wi-Fi) SSID Inspection: Detecting unauthorized BSSID/SSID associations |
| - Promiscuous Mode Compatibility: Allowing Wireshark raw packet capture without alerts|
+---------------------------------------------------------------------------------------+
```

---

### 4.1 Layer 1 & 2: Physical & Data Link Layer Concepts

#### 4.1.1 Network Interface Card (NIC) State Monitoring
The edge agent continuously interrogates the host operating system's network adapter subsystem using `psutil.net_if_stats()`.
- **Interface Up/Down State:** It detects link-state transitions (`st.isup`). If a student physically connects an Ethernet cable during an exam designated as *Internet Blocked*, the agent immediately captures the interface transition.
- **Hardware Loopback Filtering:** The agent specifically identifies and ignores virtual loopback adapters (`loopback in name.lower()`), isolating physical network interface cards.

#### 4.1.2 IEEE 802.11 (Wi-Fi) SSID & Association Inspection
In modern university environments, students often tether their PCs to 4G/5G mobile hotspots. TIDE implements wireless link-layer identification in `tide_agent/win/net.py`:
- The agent calls the Windows Native WLAN API via `netsh wlan show interfaces`.
- A regular expression parser extracts the current **Service Set Identifier (SSID)**:
  $$\text{Regex: } \verb|^\s*SSID\s*:\s*(.+)$|$$
- The system caches SSIDs and tracks associations. If an adapter switches from the institutional access point (e.g., `Univ-Lab-WiFi`) to an ad-hoc mobile SSID (e.g., `iPhone 15`), TIDE flags the network transition with telemetry specifying the exact SSID string.

#### 4.1.3 Promiscuous Mode & Wireshark Compatibility
In Computer Networking courses, students frequently need to capture packets using **Wireshark** to inspect ARP, ICMP, TCP, or DNS headers.
- **Why Naive Anti-Cheat Fails:** Standard endpoint protection software often kills Wireshark or treats packet sniffing as malicious behavior.
- **How TIDE Solves It:** Wireshark captures packets by placing the Network Interface Card into **promiscuous mode** via Npcap/WinPcap kernel drivers. Promiscuous capture operates purely at Layer 2 and Layer 3 without creating transport-layer TCP socket structures. Because TIDE's LAN monitoring specifically monitors Layer 4 socket connection tables (`psutil.net_connections("inet")`), Wireshark captures traffic passively without triggering false alarms.

---

### 4.2 Layer 3: Network Layer Concepts

#### 4.2.1 IPv4 Addressing & Limited Broadcast
To achieve **Zero-Configuration Networking (Zeroconf)** on an unmanaged laboratory LAN, TIDE utilizes IPv4 **Limited Broadcast**:
- **Broadcast Address:** `255.255.255.255`
- Under IPv4 standards (RFC 919 / RFC 922), packets addressed to `255.255.255.255` are delivered to all hosts within the local physical broadcast domain / subnet, but are strictly prohibited from being forwarded across network routers.
- This ensures that when a student agent broadcasts a discovery packet, it reaches the teacher's server on the same lab switch without leaking across the wider university campus WAN.

#### 4.2.2 RFC 1918 Private IPv4 Address Analysis
TIDE utilizes Python's standard `ipaddress` library to parse and classify network addresses into standardized scopes:
- **Private Address Ranges (RFC 1918):**
  - `10.0.0.0/8` (Class A)
  - `172.16.0.0/12` (Class B)
  - `192.168.0.0/16` (Class C)
- **Loopback Range (RFC 1122):** `127.0.0.0/8`

#### 4.2.3 Rogue LAN Peer-to-Peer (P2P) Detection
One of the most widespread cheating mechanisms in programming exams is the creation of unauthorized local file shares (e.g., Python HTTP servers, Netcat file pipes, Windows SMB shares).
TIDE enforces peer isolation through transport-to-network cross-layer inspection (`lan_peers` in `tide_agent/win/net.py`):

```python
def lan_peers(server_ip: str) -> list[Peer]:
    peers = []
    for c in psutil.net_connections("inet"):
        if c.status != psutil.CONN_ESTABLISHED or not c.raddr:
            continue
        ip = c.raddr.ip
        try:
            addr = ipaddress.ip_address(ip)
        except ValueError:
            continue
        # Exclude public IPs, loopback, and the authoritative TIDE server
        if not addr.is_private or addr.is_loopback or ip == server_ip:
            continue
        try:
            name = psutil.Process(c.pid).name() if c.pid else ""
        except psutil.Error:
            name = ""
        peers.append(Peer(ip, c.raddr.port, name))
    return peers
```

**Network Logic Breakdown:**
1. Interrogate active internet sockets (`inet`).
2. Filter for established bidirectional connections (`CONN_ESTABLISHED`).
3. Extract the remote endpoint IP address (`c.raddr.ip`).
4. Validate that `addr.is_private == True` (verifying the target is on the LAN).
5. Ensure `addr.is_loopback == False` (excluding local inter-process sockets).
6. Verify `ip != server_ip` (ensuring legitimate traffic to the teacher is permitted).
7. If all criteria are met, an **unauthorized LAN peer connection** is detected, identifying the exact remote IP, destination port, and originating process name (e.g., `curl.exe`, `python.exe`).

---

### 4.3 Layer 4: Transport Layer Concepts

#### 4.3.1 UDP vs. TCP Protocol Selection

TIDE deliberately uses both UDP and TCP, choosing the appropriate transport layer protocol based on operational requirements:

```
+------------------------------------------------------------------------------------+
|                               TRANSPORT LAYER USAGE                                |
|                                                                                    |
|         UDP (User Datagram Protocol)              TCP (Transmission Control)       |
|         - Port: 47800                             - Port: 8765                     |
|         - Socket Type: SOCK_DGRAM                 - Socket Type: SOCK_STREAM       |
|         - Paradigm: Connectionless                - Paradigm: Connection-Oriented  |
|         - Overhead: 8-byte header                 - Overhead: 20-60 byte header    |
|         - Delivery: Unreliable, No Handshake      - Delivery: Reliable, 3-Way HS   |
|         - Feature: Supports Broadcast             - Feature: Flow/Congestion Ctrl  |
|         - Use Case: Zero-Config Discovery         - Use Case: WebSockets, REST,    |
|                                                                 Active Internet Probe|
+------------------------------------------------------------------------------------+
```

#### 4.3.2 UDP Broadcast Discovery Mechanism
In a 60-seat lab, manually typing the teacher's server IP address on 60 workstations is error-prone. TIDE implements an automated UDP discovery protocol:
- **Client (Agent) Implementation (`agent/tide_agent/discovery.py`):**
  ```python
  s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
  s.settimeout(timeout)
  s.sendto(b"TIDE?", ("255.255.255.255", port))
  data, addr = s.recvfrom(1024)
  server_ip = addr[0]
  server_port = json.loads(data)["port"]
  ```
- **Server Implementation (`server/tide_server/discovery.py`):**
  - Uses `asyncio.DatagramProtocol`.
  - Binds to `(0.0.0.0, 47800)`.
  - When a datagram containing `b"TIDE?"` is received, it immediately unicasts a datagram back to the sender containing `{"tide": 1, "port": 8765}`.
- **Why UDP is Ideal Here:**
  1. **Broadcast Capability:** TCP does not support broadcasting (it is strictly point-to-point). UDP natively supports broadcasting to `255.255.255.255`.
  2. **Zero Connection Overhead:** Discovery requires a single question and single answer; establishing a 3-way TCP handshake to an unknown IP is impossible.

#### 4.3.3 Dual-Engine Active Internet Probing
Determining whether a host truly has active internet connectivity is non-trivial. Simple link-state checks fail because an Ethernet cable connected to a local switch shows "Link Up" even when the default gateway has no WAN access.
TIDE deploys a **dual-probe active detection engine** executing in parallel threads (`agent/tide_agent/win/net.py`):

1. **Layer 7 HTTP Probe (NCSI - Network Connectivity Status Indicator):**
   - Dispatches an HTTP GET request to `http://www.msftconnecttest.com/connecttest.txt` (timeout: 1.5s).
   - Validates that the response payload equals `"Microsoft Connect Test"`.
   - Protects against **Captive Portals** (which return HTTP 200/302 redirects with login HTML rather than the expected text string).
2. **Layer 4 TCP Handshake Probe:**
   - Initiates a raw TCP 3-way handshake to Cloudflare's Anycast DNS server:
     `socket.create_connection(("1.1.1.1", 443), timeout=1.5)`
   - Checks if SYN $\to$ SYN-ACK $\to$ ACK succeeds.
   - Bypasses local DNS resolution failures (since it targets a raw IP address directly).
3. **Concurrent Execution:**
   - Executed via `ThreadPoolExecutor(max_workers=2)`. If either probe succeeds within 1.5 seconds, the host is confirmed to have outbound internet access.

---

### 4.4 Layer 5: Session Layer Concepts

#### 4.4.1 Cryptographic Session Tokens & Authentication
Session management cannot rely on unauthenticated IP addresses because IP spoofing or DHCP lease reallocations would compromise session state.
- **Token Generation:** Upon pairing via `POST /api/pair`, the server issues a cryptographically secure 256-bit URL-safe token:
  $$\text{token} = \verb|secrets.token_urlsafe(32)|$$
- **Storage Security:** The server never stores the raw token in plaintext. It hashes the token using SHA-256 (`hashlib.sha256`) before committing to the SQLite database.
- **WebSocket Handshake Authentication:** When establishing the persistent WebSocket connection (`/ws/agent`), the agent must transmit a `hello` frame containing this token within a strict 5-second timeout. If the token hash does not match an active seat, the server aborts the connection with custom WebSocket close code `4401` (Unauthorized).

#### 4.4.2 The Outbox Pattern: Store-and-Forward Network Resilience
During laboratory tests, local Wi-Fi networks frequently suffer from transient interference, packet loss, or brief access point reboots.
To guarantee telemetry durability, the TIDE agent implements a **Store-and-Forward Outbox Architecture** (`agent/tide_agent/outbox.py` and `link.py`):

```
+-----------------------------------------------------------------------------+
|                           EDGE OUTBOX ARCHITECTURE                          |
|                                                                             |
|   Telemetry Event / Flag Generated                                          |
|                │                                                            |
|                ▼                                                            |
|     Is WebSocket Connected?                                                 |
|          ├─── YES ───► Transmit JSON Frame over WebSocket                   |
|          └─── NO  ───► Append to Disk: Outbox File (JSON Lines)             |
|                              │                                              |
|                      [Network Restored]                                     |
|                              │                                              |
|                              ▼                                              |
|                    Drain Outbox File                                        |
|                    Send Buffered Packets in FIFO Order                      |
|                    Unlink (Delete) Spool File                               |
+-----------------------------------------------------------------------------+
```

- When the network link drops, non-ephemeral messages (`signal`, `flag`, `snapshot`) are serialized to disk using thread-locked file operations (`outbox.append`).
- Volatile messages like `heartbeat` are excluded from buffering (`NOT_BUFFERED = {"heartbeat"}`).
- Upon reconnection, `Link.run()` invokes `self.outbox.drain()`, flushing all buffered events to the server before resuming live streaming.

#### 4.4.3 Exponential Backoff Algorithm
To prevent network congestion and **Thundering Herd problems** when a network switch restarts, the agent reconnects using truncated exponential backoff:
$$T_{\text{backoff}} = \min(T_{\text{initial}} \times 2^{n}, T_{\text{max}})$$
Where $T_{\text{initial}} = 1.0\text{ s}$ and $T_{\text{max}} = 5.0\text{ s}$.

---

### 4.5 Layer 6: Presentation Layer Concepts

#### 4.5.1 Data Serialization & Wire Framing
All WebSocket and HTTP payloads are formatted using UTF-8 encoded JSON.
- Standardized frame schema: `{"t": "<type>", ...payload}`
- Agent-to-Server types: `hello`, `heartbeat`, `preflight`, `event`, `signal`, `flag`, `evidence`, `snapshot`.
- Server-to-Agent types: `welcome`, `start`, `act`, `time`, `notice`, `end`.

#### 4.5.2 Binary-to-Text Encoding (Base64)
Because JSON is a text-based format, binary assets cannot be transmitted natively without escaping:
- **Screenshots:** When a high-severity flag triggers, `mss` captures the primary screen, scales it down to 1280px JPEG format (~120 KB), converts the byte buffer to ASCII Base64 (`base64.b64encode`), and transmits it inside an `evidence` message payload.
- **Question Files:** Binary question attachments (PDFs, starter ZIP archives) are Base64 encoded by the server and transferred to student agents within the `start` payload.

#### 4.5.3 Data Compression & Archiving
At the conclusion of the exam, the agent creates an uncorrupted PKZIP archive (`zipfile.ZipFile`) containing all source code and documents created in `C:\Exam\<roll>\`, transmitting it via multipart/form-data HTTP POST to `/api/submit`.

---

### 4.6 Layer 7: Application Layer Concepts

#### 4.6.1 The WebSocket Protocol (RFC 6455)
HTTP request-response polling introduces significant latency and unacceptable network overhead for 60 concurrent clients. TIDE utilizes **RFC 6455 WebSockets**:
- **Connection Handshake:** Initiated via HTTP Upgrade request (`GET /ws/agent HTTP/1.1`, `Upgrade: websocket`, `Connection: Upgrade`).
- **Framing Overhead:** Once established, WebSocket frames carry a tiny 2 to 10 byte header overhead, compared to 500–1000 bytes of HTTP request/response headers per message.
- **Full-Duplex Communication:** Allows the server to push instantaneous remote commands (`act`: `close_tab`, `kill`, `overlay`) to the agent without waiting for client polling.

#### 4.6.2 RESTful API Endpoints
TIDE complements WebSockets with specialized HTTP REST endpoints:
- `POST /api/pair`: Client registration, hardware binding, and token issuance.
- `POST /api/submit`: Final student project submission (multipart/form-data).
- `GET /api/teacher/summary`: Exam monitoring statistics.
- `POST /api/teacher/start`: Question release trigger.
- `POST /api/teacher/extend`: Clock extension propagation.
- `GET /api/teacher/export.csv`: Comprehensive CSV export of exam events and flags.

---

## 5. Distributed Network Synchronization: Cristian's Algorithm

### 5.1 The Clock Synchronization Problem
In a distributed network, physical clocks drift due to temperature variations, crystal oscillator inaccuracies, and software thread scheduling. If the exam duration is 60 minutes:
- A student could maliciously adjust their local system clock backwards by 30 minutes to gain unauthorized exam time.
- Relying on local client clocks makes synchronized question release and time expiration impossible.
- Standard NTP (Network Time Protocol) requires external UDP port 123 access, which is frequently blocked on isolated laboratory subnets.

### 5.2 Mathematical Formulation of Cristian's Algorithm
TIDE implements **Cristian's Algorithm (1989)** during the initial WebSocket handshake (`agent/tide_agent/clock.py`):

```
       CLIENT (Student PC)                             SERVER (Teacher Laptop)
        Local Time: T_0
               │
               │─────── Request (t="hello", local_time=T_0) ───────►
               │                                                    │
               │                                            Server Timestamp: T_server
               │                                                    │
               │◄────── Reply (t="welcome", server_time=T_server) ──│
               │
        Local Time: T_1
```

1. **Step 1:** The agent records its local monotonic time $T_0$ (`sent = time.time()`) and transmits it in the `hello` payload.
2. **Step 2:** The server receives the frame and stamps its authoritative master clock time $T_{\text{server}}$ (`welcome["server_time"]`).
3. **Step 3:** The agent receives the response at local time $T_1$ (`received = time.time()`).
4. **Step 4: Round Trip Time (RTT) Calculation:**
   $$\text{RTT} = T_1 - T_0$$
5. **Step 5: Symmetric Latency Assumption:**
   Assuming network transit times from client to server and server to client are roughly symmetric:
   $$T_{\text{propagation}} \approx \frac{\text{RTT}}{2} = \frac{T_1 - T_0}{2}$$
6. **Step 6: Clock Offset ($\theta$) Computation:**
   $$\theta = T_{\text{server}} - \left( T_0 + \frac{\text{RTT}}{2} \right) = T_{\text{server}} - \frac{T_0 + T_1}{2}$$
7. **Step 7: Synchronized Clock Transformation:**
   For all future countdown operations, the client converts local timestamps to authoritative server time:
   $$T_{\text{authoritative}} = T_{\text{local}} + \theta$$

```python
# Implemented in agent/tide_agent/clock.py
def compute_offset(sent: float, server_time: float, received: float) -> float:
    """server_now - local_now, assuming the server stamped reply halfway through RTT."""
    return server_time - (sent + received) / 2
```

**Security Consequence:** The server provides a single absolute expiration timestamp $T_{\text{ends\_at}}$. Changing the local Windows clock has zero effect on the countdown timer because the offset $\theta$ compensates directly for the local shift.

---

## 6. Network Security, Cryptography & Threat Analysis

```
+-----------------------------------------------------------------------------------+
|                            TIDE SECURITY THREAT MATRIX                            |
|                                                                                   |
|  Threat / Attack Vector     | Vulnerability Mechanism    | TIDE Defense           |
|-----------------------------|----------------------------|------------------------|
|  Man-in-the-Middle (MitM)   | ARP Spoofing / Packet Sniff| CSPRNG Tokens + SHA-256|
|  Impersonation / Hijacking  | Claiming a classmate's roll| Seat-to-Token Binding  |
|  Replay Attack              | Replaying captured frames  | Monotonic Timestamps   |
|  Denial of Service (DoS)    | Flooding WebSocket frames  | Payload Limiting & Caps|
|  Clock Manipulation         | Altering Windows Clock     | Cristian's Master Sync |
+-----------------------------------------------------------------------------------+
```

### 6.1 Cryptographic Implementations
1. **Cryptographically Secure Pseudo-Random Number Generation (CSPRNG):**
   - Implemented via Python's `secrets` module, utilizing OS-level entropy pools (`CryptGenRandom` on Windows / `/dev/urandom` on POSIX).
   - Generates 256 bits of entropy: `secrets.token_urlsafe(32)`.
2. **Cryptographic Hashing:**
   - Implemented using SHA-256 (`hashlib.sha256`).
   - Ensures that even if the teacher's SQLite database is copied, raw session tokens cannot be recovered from hashes.

### 6.2 Threat Mitigation Analysis
- **ARP Spoofing & Session Hijacking:** On an unmanaged switch, an attacker could attempt ARP poisoning. However, each WebSocket connection is tied to a specific seat ID and token hash established during the initial pairing handshake.
- **Student Impersonation:** If Seat 5 attempts to pair with Roll Number "CS201", the server verifies whether Seat 5 or "CS201" is already registered. If a collision occurs, it returns `HTTP 409 Conflict`.
- **Production Hardening Roadmap:**
  - Transport Layer Security (TLS 1.3) with X.509 certificate pinning.
  - IEEE 802.1X Network Access Control (NAC) for port-level MAC authentication.
  - Running the agent as a Windows SYSTEM Service to prevent process termination.

---

## 7. Network Bandwidth & Scalability Analysis

In a 60-seat lab test operating over a shared Wi-Fi router (e.g., 300 Mbps aggregate throughput), unoptimized network telemetry could cause packet storms or router crashes.

### 7.1 Bandwidth Budget per Node

| Telemetry Type | Frequency | Payload Size (Raw) | Average Bandwidth |
|---|---|---|---|
| **Heartbeat Ping** | Every 3 seconds | ~40 bytes | $\approx 107\text{ bps}$ |
| **Active Internet Probes** | Every 5 seconds | ~150 bytes | $\approx 240\text{ bps}$ |
| **Window/Host Delta** | Event-driven ($\approx 1/\text{min}$) | ~200 bytes | $\approx 27\text{ bps}$ |
| **Incremental Code Snapshot** | Every 30 seconds | ~1.5 KB (Delta text) | $\approx 400\text{ bps}$ |
| **Evidence Screenshot** | On-Flag only (Rare, $\approx 2/\text{test}$) | ~120 KB (JPEG) | $\approx 3.2\text{ kbps}$ (amortized) |
| **TOTAL PER NODE** | — | — | $\approx 4.0\text{ kbps}$ |

### 7.2 Total Lab Bandwidth (60 Workstations)
$$\text{Total Lab Throughput} = 60 \times 4.0\text{ kbps} \approx 240\text{ kbps} \approx 0.24\text{ Mbps}$$

**Conclusion:** The entire 60-seat telemetry stream consumes **less than 0.1%** of a standard 100 Mbps Ethernet or 802.11n/ac Wi-Fi connection.

### 7.3 Delta Encoding & Snapshot Optimization
To eliminate redundant file transmissions over the LAN:
- The agent hashes each examined file with SHA-256 (`exam_folder.py`).
- Every 30 seconds, the agent scans `C:\Exam\<roll>\`.
- **Only files whose SHA-256 hash has changed** since the previous snapshot are transmitted across the WebSocket. Unaltered starter templates are never re-sent.

---

## 8. Codebase Implementation & File Breakdown

The TIDE repository is structured into modular packages separating edge, core, and server responsibilities:

```
Tide/
├── common/             --> Shared data models, protocol definitions, policy rules
│   └── tide_common/
│       ├── protocol.py --> Wire protocol definitions (Kind, Signal, msg)
│       ├── policy.py   --> Whitelist/blacklist definitions (processes, hosts, extensions)
│       └── fingerprint.py --> Winnowing algorithm (AST tokenization, CRC32 n-grams)
├── agent/              --> Edge monitoring daemon (tide-agent.exe)
│   └── tide_agent/
│       ├── discovery.py--> UDP broadcast discovery client (Port 47800)
│       ├── link.py     --> Persistent WebSocket client with auto-reconnect
│       ├── outbox.py   --> Store-and-forward disk spooler
│       ├── clock.py    --> Cristian's clock synchronization implementation
│       ├── pairing.py  --> HTTP client for /api/pair and /api/submit
│       ├── watchers.py --> Signal extractors (Window, Process, Network, LAN, USB, Clipboard)
│       └── win/net.py  --> Windows native network probing (HTTP NCSI, TCP, psutil)
├── server/             --> Central coordinator & evidence engine
│   └── tide_server/
│       ├── discovery.py--> Asyncio UDP broadcast responder
│       ├── live.py     --> Real-time WebSocket broadcasting to console & agents
│       ├── hub.py      --> Active WebSocket client registry
│       ├── ingest.py   --> Central telemetry ingestion & flag generator
│       ├── monitor.py  --> Heartbeat watchdog & exam countdown timer
│       ├── clock.py    --> Master server time coordinator
│       ├── decide.py   --> Decision matrix (auto-act vs. flag thresholds)
│       └── classify/   --> Multi-tier classification (Jev AI, Groq, Heuristics)
└── console/            --> React + Vite real-time teacher dashboard
```

### 8.1 Key Implementation Mapping

| Functional Module | Source File | Exact Lines of Code | Key Networking / Systems Concept |
|---|---|---|---|
| **UDP Discovery Client** | [discovery.py](file:///c:/Users/pri27/Downloads/Tideeeee/agent/tide_agent/discovery.py#L10-L23) | L10–L23 | `socket.AF_INET`, `socket.SOCK_DGRAM`, `SO_BROADCAST`, `255.255.255.255:47800` |
| **UDP Discovery Server** | [discovery.py](file:///c:/Users/pri27/Downloads/Tideeeee/server/tide_server/discovery.py#L6-L23) | L6–L23 | `asyncio.DatagramProtocol`, datagram responder |
| **WebSocket Connection Manager** | [link.py](file:///c:/Users/pri27/Downloads/Tideeeee/agent/tide_agent/link.py#L26-L60) | L26–L60 | RFC 6455 WebSockets, reconnect loop, backoff, outbox draining |
| **Cristian's Sync Algorithm** | [clock.py](file:///c:/Users/pri27/Downloads/Tideeeee/agent/tide_agent/clock.py#L5-L18) | L5–L18 | Round-trip latency estimation, symmetric clock offset $\theta$ |
| **Network & LAN Peer Watcher** | [net.py](file:///c:/Users/pri27/Downloads/Tideeeee/agent/tide_agent/win/net.py#L42-L80) | L42–L80 | Dual HTTP/TCP probes, `psutil.net_connections`, RFC 1918 private IP filter |
| **WLAN SSID Extraction** | [net.py](file:///c:/Users/pri27/Downloads/Tideeeee/agent/tide_agent/win/net.py#L17-L30) | L17–L30 | Shelling out to `netsh wlan show interfaces`, parsing 802.11 SSID |
| **Telemetry Ingestion Engine** | [ingest.py](file:///c:/Users/pri27/Downloads/Tideeeee/server/tide_server/ingest.py#L41-L159) | L41–L159 | Event routing, heartbeat processing, snapshot burst calculations |
| **Heartbeat Watchdog** | [monitor.py](file:///c:/Users/pri27/Downloads/Tideeeee/server/tide_server/monitor.py#L17-L56) | L17–L56 | Dead-man timer, detecting disconnected nodes (>10s) |
| **Winnowing Code Fingerprinting**| [fingerprint.py](file:///c:/Users/pri27/Downloads/Tideeeee/common/tide_common/fingerprint.py#L20-L52)| L20–L52 | Lexical tokenization, CRC32 sliding window hashing, MOSS similarity |

---

## 9. Comprehensive Viva / Evaluation Q&A Guide for Computer Networks

This section provides rigorous, academic-grade answers to questions likely to be asked by a Computer Networks professor or external examiner.

---

### Q1: Why did you choose UDP broadcast for server discovery instead of Multicast DNS (mDNS) or SSDP?
**Answer:**
Multicast DNS (mDNS, RFC 6762) operating over `224.0.0.251:5353` and SSDP (Simple Service Discovery Protocol) over `239.255.255.250:1900` require operational **IGMP (Internet Group Management Protocol) snooping** on local network switches. In many institutional and university lab switches, multicast traffic is aggressively filtered or disabled by default to prevent multicast storms.
In contrast, standard IPv4 Limited Broadcast (`255.255.255.255:47800`) operates reliably on any Layer 2 Ethernet broadcast domain without requiring special switch configuration or multicast group registrations. Furthermore, implementing UDP broadcast requires only ~20 lines of vanilla Python socket code with zero external library dependencies.

---

### Q2: Why use WebSockets rather than standard HTTP/1.1 REST polling?
**Answer:**
In a 60-student lab, polling the server via HTTP GET requests every 1 second creates severe transport-layer overhead:
1. **TCP Connection & Header Overhead:** Each HTTP request requires either re-establishing a TCP connection (3-way handshake) or maintaining keep-alive states, transmitting 500–1000 bytes of redundant HTTP headers per poll:
   $$60 \text{ clients} \times 1 \text{ poll/sec} \times 800 \text{ bytes} \approx 480 \text{ KB/s of pure header waste!}$$
2. **Latency:** If a student opens an AI assistant, HTTP polling incurs an average detection latency of $\frac{\text{polling\_interval}}{2}$.
3. **Full-Duplex Server Push:** WebSockets (RFC 6455) provide persistent, bidirectional framing with a tiny 2 to 10 byte header overhead. This enables the server to immediately push down an `act` message (`close_tab` or `kill`) within milliseconds of a rule violation.

---

### Q3: How does your clock synchronization handle asymmetric network delays?
**Answer:**
Cristian's algorithm inherently assumes symmetric transit delays ($T_{\text{request}} \approx T_{\text{reply}} \approx \frac{\text{RTT}}{2}$).
In a local area network (LAN), where packets traverse a single Ethernet switch with transmission delays of $< 1\text{ ms}$, the asymmetry error is bounded by a fraction of a millisecond:
$$\text{Max Error} = \pm \left( \frac{\text{RTT}}{2} - \min(T_{\text{request}}) \right) < 1\text{ ms}$$
Because academic exam timers operate on a granularity of whole seconds, a sub-millisecond clock skew is mathematically and practically negligible.

---

### Q4: How does TIDE differentiate between legitimate lab traffic (e.g., student using Wireshark) and illegal peer communication?
**Answer:**
TIDE monitors transport-layer socket state tables (`psutil.net_connections("inet")`).
- **Legitimate Wireshark Traffic:** Wireshark uses raw packet capture drivers (Npcap/WinPcap) to bind directly to the Network Interface Card (NIC) in promiscuous mode. Promiscuous packet capture listens to raw frames at the Data Link layer (Layer 2) and does **not** create Layer 4 TCP connection state records in the operating system's TCP/IP stack.
- **Illegal Peer Communication:** If a student runs an HTTP server (`python -m http.server`), Netcat, or an SMB share to copy code, the operating system kernel instantiates a TCP socket in the `ESTABLISHED` state. TIDE detects this entry, validates that the destination IP belongs to an RFC 1918 private subnet, confirms it is not the teacher's server IP, and flags the unauthorized peer-to-peer connection.

---

### Q5: What happens if a student unplugs their network cable or turns off Wi-Fi during the exam?
**Answer:**
TIDE handles network disconnections through a multi-tiered fail-safe:
1. **Local Edge Enforcement:** The agent possesses a complete local copy of the policy deny list. Even while offline, it continues to watch active processes and browser titles, immediately closing prohibited apps and caching flags locally.
2. **Store-and-Forward Outbox:** Disconnected telemetry events are spooled to a thread-safe disk queue (`outbox.py`). When the network recovers, all spooled events are drained and delivered to the server in chronological order.
3. **Server Dead-Man Watchdog:** The server runs a background watchdog task (`monitor.py`). If no heartbeat is received from a paired seat within 10 seconds (`heartbeat_timeout_s`), the seat tile immediately transitions to "Agent Offline" (Grey/Red) and logs a critical flag for the invigilator.

---

### Q6: Can a student bypass the exam timer by changing their computer's system clock?
**Answer:**
No. The edge agent never relies on the client's local wall-clock time. At pairing, the agent calculates a constant clock offset:
$$\theta = T_{\text{server}} - \frac{T_0 + T_1}{2}$$
The exam's end time ($T_{\text{ends\_at}}$) is established by the server. If the student moves the Windows clock backwards by 1 hour, the agent's computation of local time adjusts proportionally, neutralizing the attempt.

---

### Q7: Explain the dual-engine active internet probing mechanism.
**Answer:**
Simple NIC status checks are insufficient because an Ethernet adapter connected to a local switch shows "Link Up" even when there is no internet access. TIDE runs two probes concurrently:
1. **Application Layer HTTP Probe:** Dispatches an HTTP GET to `http://www.msftconnecttest.com/connecttest.txt` expecting the exact response string `"Microsoft Connect Test"`. This validates DNS resolution, routing, and confirms the client is not trapped behind an unauthenticated captive portal.
2. **Transport Layer TCP Probe:** Initiates a raw TCP 3-way handshake to `1.1.1.1:443` (Cloudflare Anycast). This tests Layer 4 internet routing independent of DNS system status.

---

### Q8: What is the purpose of the MOSS-style Winnowing algorithm in a networking project?
**Answer:**
While TIDE focuses on network and system integrity, preventing students from transferring pre-existing code across network shares or USB drives requires payload content verification. The **Winnowing algorithm** parses source code, strips comments and whitespace, substitutes variable identifiers with generic tokens, and generates CRC32 polynomial hashes over sliding $k$-grams. A windowing filter selects the minimum hash within each window, producing a condensed fingerprint that is invariant to variable renaming. This enables rapid comparison of submitted code against pre-exam local drive baselines.

---

### Q9: How are odd/even question sets assigned and distributed across the network?
**Answer:**
To prevent neighboring students from copying from adjacent screens:
1. Question files for Set A and Set B are uploaded to the teacher server.
2. When the teacher clicks **Start**, the server evaluates each seat number:
   $$\text{Set} = \begin{cases} \text{B} & \text{if } \text{seat\_no} \pmod 2 == 0 \text{ and Set B exists} \\ \text{A} & \text{otherwise} \end{cases}$$
3. The server pushes the appropriate question set over the WebSocket connection encoded in Base64. Questions are only written to the student's disk (`C:\Exam\<roll>\`) after the exam officially begins.

---

### Q10: How does TIDE address Man-in-the-Middle (MitM) attacks on the local network?
**Answer:**
In the demo build, authentication is handled via high-entropy 256-bit cryptographic tokens stored as SHA-256 hashes on the server.
In production deployment, all WebSocket and HTTP communication is encapsulated within **TLS 1.3 (Transport Layer Security)**. The agent executable is compiled with an embedded **X.509 Certificate Pin**, ensuring it only establishes TLS handshakes with the authentic teacher server, preventing ARP poisoning and rogue gateway MitM interception.

---

## 10. Team Member Roles, Code Ownership & Viva Voce Division

To ensure equitable Project-Based Learning (PBL) assessment, the TIDE engineering responsibilities are partitioned into four distinct, cohesive architectural domains across the team:

### 10.1 Module Division Matrix

| Team Member | Enrollment No. | Architectural Domain | Core Source Code Ownership | Primary Computer Networks Concepts |
|---|---|---|---|---|
| **Priyanshu Gumber** | 2401030082 | **Transport Layer, Zero-Config Discovery & Clock Sync** | `agent/discovery.py`<br>`server/discovery.py`<br>`agent/clock.py`<br>`server/clock.py`<br>`server/monitor.py` | UDP datagram sockets (`SOCK_DGRAM`), Limited Broadcast (`255.255.255.255:47800`), RFC 919/922 broadcast confinement, Cristian's Clock Synchronization Algorithm, Round-Trip Time ($RTT$) latency compensation. |
| **Toyesh Gupta** | 2401030081 | **Full-Duplex WebSockets, Session Security & Outbox Engine** | `agent/link.py`<br>`server/hub.py`<br>`agent/outbox.py`<br>`common/protocol.py`<br>`server/exam_service.py` | RFC 6455 persistent WebSocket streaming, CSPRNG session token issuance (256 bits), SHA-256 database hashing, Store-and-Forward Outbox pattern, Truncated Exponential Backoff. |
| **Rashi Johari** | 2401030072 | **Boundary Telemetry, Active Probing & Rogue LAN Peers** | `agent/win/net.py`<br>`agent/watchers.py`<br>`agent/platform.py`<br>`agent/win/windows.py` | Cross-layer socket table inspection (`psutil.net_connections`), RFC 1918 private subnets, Promiscuous mode Wireshark pass-through, Layer 7 NCSI HTTP probe, Layer 4 TCP Anycast probe, 802.11 SSID tracking. |
| **Ivy Singh** | 2401030071 | **Telemetry Ingestion, Winnowing Fingerprinting & Classifier** | `server/ingest.py`<br>`common/fingerprint.py`<br>`server/similarity.py`<br>`server/decide.py`<br>`server/classify/*` | Central WebSocket frame dispatching, Server-side Dead-Man Watchdog (>10s timeout), Delta encoding for bandwidth optimization, MOSS-style AST Winnowing algorithm, CRC32 polynomial hashing, Edge-to-Cloud decision hierarchy. |

### 10.2 Viva Voce Individual Defense Ownership

1. **Priyanshu Gumber:** Defends UDP vs. TCP tradeoffs for network discovery, broadcast domain boundaries under RFC 919/922, and the mathematical derivation of Cristian's clock synchronization algorithm ($RTT$ measurement, symmetric propagation delay assumption, and immunity to client clock tampering).
2. **Toyesh Gupta:** Defends the overhead reduction of RFC 6455 WebSockets over HTTP polling (2–10 byte frames vs 800+ bytes headers), session security via 256-bit CSPRNG tokens and SHA-256 hashing at rest, and the Store-and-Forward Outbox queue for network partition tolerance.
3. **Rashi Johari:** Defends cross-layer socket state inspection (`CONN_ESTABLISHED`), RFC 1918 private address filtering for peer-to-peer cheat detection, why Wireshark's promiscuous mode capture runs without false alarms, and dual-engine active internet probing (Layer 7 NCSI HTTP vs Layer 4 TCP).
4. **Ivy Singh:** Defends delta encoding for network bandwidth conservation (~4.0 kbps per PC), the server-side dead-man watchdog timer, the AST Winnowing fingerprinting algorithm (lexical normalization, variable name erasure, CRC32 polynomial hashing), and the multi-tier AI decision pipeline.

---

## 11. Summary & Conclusion

TIDE demonstrates that **robust exam integrity does not require restricting students to artificial browser kiosks or disabling network connectivity**. By combining:
- **Transport Layer Sockets & Broadcast Discovery (UDP/TCP)**
- **Application Layer Streaming (WebSockets RFC 6455 & REST)**
- **Distributed Clock Synchronization (Cristian's Algorithm)**
- **Network Interface & Unauthorized Peer Detection**
- **Edge-Fog-Cloud Decision Pipelines (Local Rules $\to$ Jev AI)**

TIDE provides an authentic, robust, and academically rigorous solution for computer science laboratory evaluations, serving as an ideal Project-Based Learning (PBL) capstone in Computer Networks.
