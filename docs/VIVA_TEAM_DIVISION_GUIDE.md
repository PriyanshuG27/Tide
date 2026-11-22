# TIDE: 4-Member Team Division & Viva Voce Defense Guide
## Computer Networks (CN) PBL Project — Viva Strategy & Code Ownership

---

### Project & Team Details
- **Project Title:** TIDE — Test Integrity in Developer Environments
- **Course:** Computer Networks (PBL) — Academic Year 2024–25 / 2025–26
- **Institution:** Jaypee Institute of Information Technology (JIIT)
- **Team Size:** 4 Members
  1. **Priyanshu Gumber** (2401030082) — Transport Layer, Zero-Config Networking & Clock Synchronization
  2. **Toyesh Gupta** (2401030081) — Full-Duplex WebSockets, Session Security & Fault-Tolerant Outbox
  3. **Rashi Johari** (2401030072) — Network Boundary Inspection, Active Probing & Rogue LAN Peer Detection
  4. **Ivy Singh** (2401030071) — Telemetry Ingestion, MOSS-Style Fingerprinting & Decision Pipeline

---

## 1. Quick Division Summary (At A Glance)

| Team Member | Enrollment No. | Primary Project Role | Core Codebase Ownership | Core Computer Networks Concepts |
|---|---|---|---|---|
| **Priyanshu Gumber** | 2401030082 | **Lead Architect — Transport Layer, Discovery & Clock Sync** | `agent/discovery.py`<br>`server/discovery.py`<br>`agent/clock.py`<br>`server/clock.py`<br>`server/monitor.py` | UDP datagram sockets (`SOCK_DGRAM`), Limited Broadcast (`255.255.255.255`), RFC 919/922, Cristian's Clock Synchronization Algorithm, Round-Trip Time ($RTT$) estimation. |
| **Toyesh Gupta** | 2401030081 | **Full-Duplex Streaming, Session Security & Edge Outbox** | `agent/link.py`<br>`server/hub.py`<br>`agent/outbox.py`<br>`common/protocol.py`<br>`server/exam_service.py` | RFC 6455 WebSockets full-duplex framing, CSPRNG session tokens, SHA-256 at-rest hashing, Store-and-Forward Outbox pattern, Truncated Exponential Backoff. |
| **Rashi Johari** | 2401030072 | **Network Boundary Watcher, Active Probes & Rogue Peers** | `agent/win/net.py`<br>`agent/watchers.py`<br>`agent/platform.py`<br>`agent/win/windows.py` | Cross-layer socket table inspection (`psutil.net_connections`), RFC 1918 private subnets, Wireshark promiscuous mode pass-through, Layer 7 NCSI HTTP probe, Layer 4 TCP Anycast probe, 802.11 SSID extraction. |
| **Ivy Singh** | 2401030071 | **Telemetry Ingestion, Winnowing Fingerprinting & Classifier** | `server/ingest.py`<br>`common/fingerprint.py`<br>`server/similarity.py`<br>`server/decide.py`<br>`server/classify/*` | Telemetry event routing, Dead-man watchdog (>10s timeout), Delta encoding for bandwidth optimization, MOSS-style AST Winnowing algorithm, CRC32 polynomial hashing, Edge-to-Cloud decision hierarchy. |

---

## 2. In-Depth Member Breakdown & Viva Preparation

---

### MEMBER 1: Priyanshu Gumber (2401030082)
**Designation:** Lead Architect — Transport Layer, Zero-Config Networking & Clock Synchronization

#### 1. What You Built & Own
You developed the entire transport-layer network discovery subsystem and the distributed clock synchronization mechanism:
1. **Zero-Configuration UDP Discovery:** You engineered the automated server-client pairing protocol that eliminates the need to manually configure teacher server IP addresses across 60 student workstations.
2. **Limited Broadcast Socket Programming:** You wrote the low-level socket communication logic using UDP datagrams (`socket.AF_INET`, `socket.SOCK_DGRAM`) and configured broadcast socket options (`SO_BROADCAST`), ensuring packets conform to RFC 919/922 broadcast domain confinement.
3. **Distributed Clock Synchronization (Cristian's Algorithm):** You implemented Cristian's 1989 clock synchronization algorithm to neutralize student attempts to tamper with local Windows system clocks, keeping 60 clients synchronized to the teacher master clock within sub-millisecond precision.

#### 2. Exact Code Files to Open & Explain
- **[`agent/tide_agent/discovery.py` (Lines 10–23)](file:///c:/Users/pri27/Downloads/Tideeeee/agent/tide_agent/discovery.py#L10-L23):**
  Show the examiner where the agent opens a UDP datagram socket, applies `setsockopt(SOL_SOCKET, SO_BROADCAST, 1)`, transmits `b"TIDE?"` to `255.255.255.255:47800`, and receives the server IP from `addr[0]`.
- **[`server/tide_server/discovery.py` (Lines 6–23)](file:///c:/Users/pri27/Downloads/Tideeeee/server/tide_server/discovery.py#L6-L23):**
  Explain the server's asynchronous `asyncio.DatagramProtocol` responder that listens on port `47800` and unicasts back `{"tide": 1, "port": 8765}`.
- **[`agent/tide_agent/clock.py` (Lines 5–18)](file:///c:/Users/pri27/Downloads/Tideeeee/agent/tide_agent/clock.py#L5-L18):**
  Walk through `compute_offset(sent, server_time, received)`:
  $$\text{Offset } \theta = T_{\text{server}} - \frac{T_0 + T_1}{2}$$
  Show how `ServerClock.now()` returns `time.time() + self.offset`.

#### 3. Live Demo Role
- Launch the server (`tide-server --demo`) and show the discovery daemon starting on UDP port 47800.
- Launch the agent (`tide-agent`), demonstrate that it finds the server automatically without typing an IP address, and show the calculated clock offset in the debug log.
- Open the Windows Date & Time settings on the student machine, roll back the clock by 1 hour, and demonstrate that the Tide exam countdown timer does **not** budge because the offset $\theta$ compensates instantaneously.

#### 4. Top Viva Questions for Priyanshu
* **Q1: Why did you use UDP broadcast instead of Multicast DNS (mDNS) or SSDP?**
  * *Answer:* mDNS (`224.0.0.251:5353`) and SSDP (`239.255.255.250:1900`) rely on IP multicast groups. In institutional and university lab switches, multicast is frequently disabled or filtered by IGMP snooping to prevent network flooding. Limited broadcast (`255.255.255.255:47800`) operates universally across any standard Layer 2 Ethernet switch without special network configuration.
* **Q2: Does your broadcast packet leak outside the lab to the whole campus?**
  * *Answer:* No. Under RFC 919 and RFC 922, `255.255.255.255` is a Limited Broadcast address. Routers are strictly prohibited from forwarding limited broadcast packets across network interfaces. The packet is flooded only within the local collision/broadcast domain (the lab switch).
* **Q3: How does Cristian's Algorithm handle network latency and jitter?**
  * *Answer:* Cristian's algorithm calculates Round-Trip Time ($RTT = T_1 - T_0$) and assumes symmetric network delay ($T_{\text{transit}} \approx \frac{RTT}{2}$). On a local lab LAN switch where latency is $<1\text{ ms}$, network asymmetry contributes $<0.5\text{ ms}$ of error. Since exam countdowns operate in whole seconds, this sub-millisecond precision is more than sufficient.
* **Q4: Why can't we just use NTP (Network Time Protocol)?**
  * *Answer:* Standard NTP operates on external UDP port 123. In strict or offline university lab environments, external WAN traffic to public NTP pool servers is blocked. Implementing Cristian's algorithm directly inside our application handshake gives us self-contained synchronization with zero external dependencies.

---

### MEMBER 2: Toyesh Gupta (2401030081)
**Designation:** Full-Duplex Network Streaming, Session Security & Fault-Tolerant Outbox Engine

#### 1. What You Built & Own
You engineered the persistent bidirectional telemetry channel and the edge fault-tolerance architecture:
1. **Full-Duplex WebSocket Streaming (RFC 6455):** You implemented the persistent WebSocket client loop and server hub, enabling bidirectional message transfer with minimal header overhead compared to HTTP polling.
2. **Session Layer Security & Token Authentication:** You designed the cryptographic authentication pipeline using 256-bit CSPRNG tokens, SHA-256 one-way hashing in SQLite, and WebSocket handshake verification using custom RFC 6455 close codes (`4401`).
3. **Edge Outbox Pattern (Store-and-Forward):** You implemented the disk-based persistence queue that buffers telemetry frames during transient Wi-Fi dropouts and replays them in FIFO order upon reconnection, paired with a truncated exponential backoff algorithm.

#### 2. Exact Code Files to Open & Explain
- **[`agent/tide_agent/link.py` (Lines 26–71)](file:///c:/Users/pri27/Downloads/Tideeeee/agent/tide_agent/link.py#L26-L71):**
  Show the `Link.run()` loop connecting via `websockets.connect`, sending the `hello` token frame, handling auth failure (`code == 4401`), and draining pending outbox messages upon reconnection.
- **[`agent/tide_agent/outbox.py` (Lines 6–24)](file:///c:/Users/pri27/Downloads/Tideeeee/agent/tide_agent/outbox.py#L6-L24):**
  Explain the thread-safe `Outbox` class with `append()` and `drain()` using mutex locks to persist un-sent messages to disk as JSON Lines.
- **[`server/tide_server/hub.py` (Lines 6–42)](file:///c:/Users/pri27/Downloads/Tideeeee/server/tide_server/hub.py#L6-L42):**
  Show the `Hub` class managing the mapping of active seat IDs to their corresponding WebSocket instances (`self.agents: dict[int, WebSocket]`) and broadcasting to teacher consoles (`to_console`).
- **[`server/tide_server/exam_service.py` (Lines 25–31, 71–82)](file:///c:/Users/pri27/Downloads/Tideeeee/server/tide_server/exam_service.py#L25-L82):**
  Show `secrets.token_urlsafe(32)` generating 256 bits of entropy and `hashlib.sha256(token.encode()).hexdigest()` hashing the token at rest.

#### 3. Live Demo Role
- Demonstrate the live WebSocket connection between agent and server.
- Simulate a network disconnect: pull the Wi-Fi or disable the adapter. Show that the agent keeps running locally, flags an event, and queues it to `outbox.jsonl` on disk.
- Reconnect the network and show the agent instantly draining the outbox queue, delivering all buffered events to the teacher console without packet loss.
- Show an unauthorized WebSocket connection attempt failing with close code `4401`.

#### 4. Top Viva Questions for Toyesh
* **Q1: Why are WebSockets superior to HTTP GET polling in this architecture?**
  * *Answer:* For 60 workstations polling once per second, HTTP GET requests transmit ~800 bytes of headers per request, generating ~480 KB/s of redundant header traffic. WebSockets (RFC 6455) establish a persistent full-duplex TCP stream with a minimal 2-to-10 byte framing overhead, cutting bandwidth by >98% and allowing the server to push emergency `act` commands (`close_tab` / `kill`) with zero client-polling latency.
* **Q2: Why do you store the SHA-256 hash of the session token rather than the raw token?**
  * *Answer:* Following the Principle of Least Privilege and Defense-in-Depth, if an unauthorized user copies or inspects the teacher's SQLite database file (`tide.db`), they cannot use the database contents to impersonate student seats because SHA-256 is a one-way cryptographic hash function.
* **Q3: Explain the Truncated Exponential Backoff formula used during reconnection.**
  * *Answer:* When a network switch or access point reboots, 60 workstations attempting to reconnect simultaneously create a **Thundering Herd problem** and packet collisions. We implement:
    $$T_{\text{backoff}} = \min(1.0 \times 2^n, 5.0) \text{ seconds}$$
    This introduces spacing between reconnection attempts ($1s \to 2s \to 4s \to 5s$), reducing peak switch congestion during recovery.
* **Q4: Why are heartbeats excluded from the outbox spool queue?**
  * *Answer:* Heartbeats are ephemeral state indicators (`NOT_BUFFERED = {"heartbeat"}`). If a client was disconnected for 30 seconds, replaying 10 stale heartbeat packets upon reconnection provides zero diagnostic value and wastes network throughput; only permanent state transitions (`flags`, `signals`, `snapshots`) require guaranteed delivery.

---

### MEMBER 3: Rashi Johari (2401030072)
**Designation:** Network Boundary Inspection, Active Probing & Rogue LAN Peer Detection

#### 1. What You Built & Own
You built the operating-system-level network telemetry engine, boundary enforcement, and rogue socket detection:
1. **Rogue Peer-to-Peer LAN Connection Detection:** You engineered the cross-layer socket inspector that monitors kernel TCP state tables to detect unauthorized direct file sharing between student machines (e.g., Python HTTP servers, Netcat, SMB shares).
2. **Promiscuous Mode Compatibility (Wireshark Support):** You solved the critical dilemma of allowing students to use Wireshark legitimately for networking labs without triggering false-positive cheating alerts.
3. **Dual-Engine Active Internet Probing:** You built the concurrent multi-threaded probe engine combining Layer 7 HTTP NCSI requests (catching captive portal redirects) and Layer 4 raw TCP 3-way handshakes to Cloudflare Anycast (`1.1.1.1:443`).
4. **Layer 1 & 2 Link & SSID Monitoring:** You integrated native Windows WLAN APIs (`netsh wlan show interfaces`) to detect unauthorized hotspot roaming and physical adapter hotplugging.

#### 2. Exact Code Files to Open & Explain
- **[`agent/tide_agent/win/net.py` (Lines 63–80)](file:///c:/Users/pri27/Downloads/Tideeeee/agent/tide_agent/win/net.py#L63-L80):**
  Walk through `lan_peers(server_ip)`: show how it iterates over `psutil.net_connections("inet")`, checks `c.status == CONN_ESTABLISHED`, parses the destination IP via `ipaddress.ip_address()`, verifies `addr.is_private and not addr.is_loopback and ip != server_ip`, and flags the rogue socket with PID and process name.
- **[`agent/tide_agent/win/net.py` (Lines 42–60)](file:///c:/Users/pri27/Downloads/Tideeeee/agent/tide_agent/win/net.py#L42-L60):**
  Show the dual-probe engine: `_http_probe()` querying `msftconnecttest.com/connecttest.txt` and `_tcp_probe()` establishing a raw TCP connection to `("1.1.1.1", 443)` via `ThreadPoolExecutor(max_workers=2)`.
- **[`agent/tide_agent/win/net.py` (Lines 17–30)](file:///c:/Users/pri27/Downloads/Tideeeee/agent/tide_agent/win/net.py#L17-L30):**
  Show `_ssid()` executing `netsh wlan show interfaces` and extracting the connected wireless SSID via regex `^\s*SSID\s*:\s*(.+)$`.
- **[`agent/tide_agent/watchers.py` (Lines 64–103)](file:///c:/Users/pri27/Downloads/Tideeeee/agent/tide_agent/watchers.py#L64-L103):**
  Show `NetworkWatcher` and `LanWatcher` polling adapters and generating structured `Signal` objects.

#### 3. Live Demo Role
- Launch a simple HTTP file server on a second machine or terminal (`python -m http.server 8080`). Connect to it from the student workstation (`curl http://192.168.1.X:8080`). Show that Tide catches the established TCP socket immediately and raises an unauthorized LAN peer alert naming the process and IP.
- Launch **Wireshark**, start a packet capture on the Wi-Fi/Ethernet interface, and show that Wireshark captures packets freely **without triggering any false alerts** on the teacher console.
- Connect the student machine to a mobile phone hotspot and show the teacher console capturing the new SSID name.

#### 4. Top Viva Questions for Rashi
* **Q1: How do you differentiate between Wireshark packet capturing and illegal peer communication?**
  * *Answer:* Wireshark captures packets by putting the Network Interface Card (NIC) into **promiscuous mode** using Npcap/WinPcap kernel drivers. Promiscuous capture operates at Layers 2 and 3, copying raw frames from the wire without establishing Layer 4 transport sockets. Cheating tools (HTTP servers, Netcat, Windows shares) create transport-layer sockets in the `ESTABLISHED` state. Our engine specifically inspects the kernel's `CONN_ESTABLISHED` TCP table, allowing Wireshark to run passively without generating alerts.
* **Q2: Why is checking if the network cable is plugged in insufficient to test internet access?**
  * *Answer:* Physical link status (`st.isup`) only confirms Layer 1/2 connectivity to the local Ethernet switch. A cable plugged into an unmanaged lab switch with an offline or misconfigured gateway will show "Link Up", but have zero WAN internet connectivity. Active probing at Layers 4 and 7 is required to verify end-to-end internet transit.
* **Q3: What are RFC 1918 private address blocks, and why do you check them in peer detection?**
  * *Answer:* RFC 1918 defines private IPv4 address allocations reserved for local networks: `10.0.0.0/8`, `172.16.0.0/12`, and `192.168.0.0/16`. Our peer detection logic checks `addr.is_private` to ensure the remote IP belongs to the local subnet. We exclude loopback (`127.0.0.0/8`) to permit local inter-process communication, and exclude the teacher's server IP to permit official exam telemetry.
* **Q4: How does your HTTP probe detect Captive Portals?**
  * *Answer:* When connecting to a public or university network that requires web authentication, the gateway transparently hijacks port 80 traffic and returns an HTTP 302 redirect with an HTML login page. Our probe queries `http://www.msftconnecttest.com/connecttest.txt` and verifies that the body string exactly matches `"Microsoft Connect Test"`. If an HTML login page or redirect is received, it fails the validation, exposing the captive portal.

---

### MEMBER 4: Ivy Singh (2401030071)
**Designation:** Telemetry Ingestion, MOSS-Style Code Fingerprinting & Multi-Tier AI Decision Pipeline

#### 1. What You Built & Own
You engineered the central server-side telemetry processor, plagiarism detection engine, and decision classification pipeline:
1. **Server Ingestion & State Machine:** You built the message dispatching engine (`ingest.py`) that processes all incoming WebSocket frames (`heartbeat`, `signal`, `flag`, `evidence`, `snapshot`), decodes Base64 screenshots, and maintains exam state.
2. **Dead-Man Watchdog Timer:** You engineered the server-side monitoring loop (`monitor.py`) that checks agent heartbeats every 2 seconds; if an agent goes silent for >10 seconds, it transitions the seat to "Agent Offline" and raises a critical alert.
3. **MOSS-Style Winnowing Fingerprinting Algorithm:** You implemented the AST tokenization and CRC32 polynomial sliding-window fingerprinting algorithm (`fingerprint.py`) to detect pre-existing or network-shared code re-use invariant to variable renaming.
4. **Multi-Tier AI Decision Pipeline:** You built the hierarchical decision tree (`Local Cache -> Jev AI / Groq API -> Offline Heuristics`), implementing calibrated confidence thresholds ($p \ge 0.90 \implies$ automated enforcement action).

#### 2. Exact Code Files to Open & Explain
- **[`server/tide_server/ingest.py` (Lines 41–100)](file:///c:/Users/pri27/Downloads/Tideeeee/server/tide_server/ingest.py#L41-L100):**
  Show the `handle()` dispatcher routing messages to `_on_heartbeat()`, `_on_signal()`, `_on_flag()`, and `_on_evidence()`. Show Base64 decoding of screenshot bytes into JPEG files (`shots/<id>.jpg`).
- **[`server/tide_server/monitor.py` (Lines 17–56)](file:///c:/Users/pri27/Downloads/Tideeeee/server/tide_server/monitor.py#L17-L56):**
  Walk through the `tick()` function: checking `t - seat.last_seen > heartbeat_timeout_s` (10s), marking seat as `offline`, and pushing `raise_flag(kind="agent_offline", severity="critical")`.
- **[`common/tide_common/fingerprint.py` (Lines 20–52)](file:///c:/Users/pri27/Downloads/Tideeeee/common/tide_common/fingerprint.py#L20-L52):**
  Show `normalize_code()`, tokenization replacing variable names with `"v"`, CRC32 polynomial hashing (`zlib.crc32`), and sliding-window minimum selection (`window = 4, k = 5`).
- **[`server/tide_server/decide.py` (Lines 8–21)](file:///c:/Users/pri27/Downloads/Tideeeee/server/tide_server/decide.py#L8-L21):**
  Show the decision function evaluating label and confidence ($p \ge 0.90$ on `ai_assistant`, `communication`, or `remote_or_file_share` returns `close_tab` or `kill`).

#### 3. Live Demo Role
- Open the Teacher Console dashboard in a browser (`http://localhost:8765`, PIN 2468).
- Demonstrate the live 60-seat matrix streaming telemetry in real-time.
- Simulate an agent failure: kill the agent process via Task Manager. Show that within exactly 10 seconds, the monitor watchdog turns the seat tile grey ("Agent Offline") and generates a critical alert.
- Paste pre-existing code into `C:\Exam\<roll>\` and demonstrate that the Winnowing fingerprinting engine flags "Old code reused" with an exact match percentage, showing how it survives variable renaming.

#### 4. Top Viva Questions for Ivy
* **Q1: How does your Winnowing algorithm survive when a student renames all variables?**
  * *Answer:* The algorithm performs lexical tokenization and normalizes all non-keyword user identifiers into a generic token `"v"`. For example, `int counter = 0;` and `int total_sum = 0;` both tokenize to `[int, "v", =, 0, ;]`. When we hash overlapping $k$-grams of 5 tokens using CRC32, both snippets produce identical hash values, making the similarity calculation 100% invariant to variable renaming.
* **Q2: How do you prevent 60 workstations from overwhelming network bandwidth when submitting snapshots?**
  * *Answer:* We implement **delta encoding**. Every 30 seconds, the agent computes SHA-256 checksums of files in `C:\Exam\<roll>\`. Only files whose SHA-256 hash has changed since the previous snapshot are transmitted over the WebSocket. Starter templates that remain untouched are never transmitted, keeping the per-seat bandwidth consumption at $\approx 4.0\text{ kbps}$.
* **Q3: What is a Dead-Man Watchdog Timer and why is it needed?**
  * *Answer:* A student attempting to cheat could terminate the agent process (`taskkill /F /IM tide-agent.exe`) or freeze its thread. Because a killed agent cannot send an exit notice, the server relies on a dead-man watchdog timer: the agent must transmit a heartbeat every 3 seconds. If the server does not receive a heartbeat for $>10\text{ seconds}$, it knows the client is dead or blocked, automatically raising a critical "Agent Offline" flag.
* **Q4: Why use Jev AI or Groq via a decision API instead of a general generative LLM?**
  * *Answer:* Generative LLMs generate free-form text, which is slow (2–5 seconds per prompt), expensive, and difficult to parse programmatically. Jev and Groq Decisions APIs classify events from a predefined discrete set of labels (`ai_assistant`, `communication`, `allowed_tool`) and return a calibrated numerical probability in $<0.4\text{ seconds}$. This allows us to enforce mathematical threshold rules ($p \ge 0.90 \implies$ auto-act) safely in production.

---

## 3. Team Demo Presentation Script (5-Minute Viva Flow)

| Time | Speaker | Action / Demo Step | Key Technical Terminology Highlighted |
|---|---|---|---|
| **0:00 – 1:00** | **Priyanshu Gumber** | **System Intro & UDP Discovery:** Explains the failure of cable pulling. Launches server. Launches agent. Shows UDP broadcast discovery finding the server on port 47800. Shows Cristian's clock sync offset in logs. Tampering test: rolls back Windows clock by 1 hr — timer stays synced. | `SOCK_DGRAM`, `SO_BROADCAST`, `255.255.255.255`, RFC 919/922, Cristian's Clock Synchronization, Round-Trip Time. |
| **1:00 – 2:15** | **Toyesh Gupta** | **Streaming & Network Fault Tolerance:** Explains RFC 6455 WebSockets vs HTTP polling. Shows live bidirectional streaming. Demonstrates 256-bit token pairing. Pulls network connection to simulate Wi-Fi drop: shows agent buffering events to `outbox.jsonl`. Reconnects: shows instant FIFO drainage. | RFC 6455 WebSockets, CSPRNG tokens, SHA-256 at-rest hashing, Store-and-Forward Outbox, Truncated Exponential Backoff. |
| **2:15 – 3:30** | **Rashi Johari** | **Socket Inspection & Wireshark Demo:** Explains Layer 4 connection state tables. Spawns an ad-hoc Python HTTP server on LAN; triggers a connection; shows Tide raising a rogue LAN peer alert. Launches **Wireshark** in promiscuous mode: shows packets capturing cleanly with zero false alerts. Shows dual-engine internet probe. | `psutil.net_connections`, `CONN_ESTABLISHED`, RFC 1918 private subnets, Promiscuous Mode vs Layer 4 sockets, NCSI HTTP probe, Anycast `1.1.1.1`. |
| **3:30 – 4:45** | **Ivy Singh** | **Ingestion, Watchdogs & Code Fingerprinting:** Shows teacher console live 60-seat matrix. Kills student agent: shows dead-man timer triggering "Agent Offline" at 10s. Pastes pre-written code with renamed variables: shows MOSS-style Winnowing algorithm detecting "Old code reused" at 95% match. Explains decision thresholds. | Ingestion pipeline, Dead-Man Watchdog, Winnowing algorithm, CRC32 polynomial hashing, Delta encoding, Decision thresholds ($p \ge 0.90$). |
| **4:45 – 5:00** | **All Members** | **Conclusion:** Summarizes how the system combines Transport, Network, Session, and Application layer principles to solve academic lab integrity while preserving native developer tool freedom. | Full-stack Computer Networks PBL capstone synthesis. |

---

## 4. Examiner "Gotcha" Questions & Counter-Strategies

1. **"What if an admin student deletes or kills your agent?"**
   * *Answer (Priyanshu / Toyesh):* In user mode, any admin can kill a process. However, Tide's server dead-man watchdog detects the missing heartbeat within 10 seconds and turns the seat grey with an immutable critical flag. In production, Tide deploys as a Windows SYSTEM Service, which unprivileged lab students cannot stop via Task Manager.
2. **"What if the student uses a phone or secondary device under the desk?"**
   * *Answer (Rashi / Ivy):* Software running on a PC cannot detect physical hardware hidden under a desk — that remains the domain of physical invigilation. Tide's purpose is to eliminate screen-monitoring exhaustion: instead of 1 invigilator trying to watch 60 screens simultaneously, Tide tells the invigilator *which exact seat* to walk toward.
3. **"Why not just block internet entirely at the lab router/firewall level?"**
   * *Answer (All):* That is exactly what institutions attempt today, and it consistently fails because students tether to 4G/5G mobile hotspots or plug in USB dongles, bypassing campus router firewalls completely. Tide enforces policy directly at the endpoint operating system, which catches hotspot tethering regardless of campus infrastructure.
