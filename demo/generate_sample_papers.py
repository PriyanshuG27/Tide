import sys
from pathlib import Path

def generate_pdf(filename: Path, title: str, subtitle: str, set_name: str, meta: list[str], sections: list[tuple[str, list[str]]]):
    """Generates a clean, valid standard PDF 1.4 document."""
    
    # We will build a PDF document with Catalog, Pages, Page, Font(Helvetica, Helvetica-Bold), Content Stream
    def clean_text(s: str) -> str:
        s = s.replace('—', '-').replace('–', '-').replace('“', '"').replace('”', '"').replace('’', "'")
        return s.replace('\\', '\\\\').replace('(', '\\(').replace(')', '\\)')

    ops = []
    # Setup coordinates: Origin at bottom-left, page is 595 x 842 (A4).
    # Header Box
    ops.append("0.12 0.15 0.22 rg")  # Dark Slate Blue
    ops.append("40 760 515 50 re f") # Header banner rectangle
    
    # Header Text
    ops.append("1 1 1 rg")           # White text
    ops.append("BT /F2 16 Tf 55 788 Td (" + clean_text(title) + ") Tj ET")
    ops.append("BT /F1 10 Tf 55 770 Td (" + clean_text(subtitle) + ") Tj ET")
    
    # Set Badge
    ops.append("0.9 0.3 0.25 rg")    # Accent color
    ops.append("450 768 95 32 re f")
    ops.append("1 1 1 rg")
    ops.append("BT /F2 14 Tf 465 780 Td (" + clean_text(f"SET {set_name}") + ") Tj ET")

    # Meta bar
    y = 735
    ops.append("0.2 0.2 0.2 rg")     # Dark text
    ops.append("BT /F1 9 Tf")
    meta_line = "  |  ".join(meta)
    ops.append(f"45 {y} Td ({clean_text(meta_line)}) Tj ET")
    
    # Horizontal rule
    y -= 12
    ops.append("0.8 0.8 0.8 RG 1 w")
    ops.append(f"40 {y} m 555 {y} l S")
    
    y -= 22
    for heading, lines in sections:
        # Section Heading
        ops.append("0.15 0.25 0.45 rg") # Primary accent
        ops.append(f"BT /F2 12 Tf 45 {y} Td ({clean_text(heading)}) Tj ET")
        y -= 6
        ops.append("0.7 0.75 0.85 RG 0.5 w")
        ops.append(f"45 {y} m 555 {y} l S")
        y -= 16
        
        ops.append("0.1 0.1 0.1 rg")
        for line in lines:
            if y < 60:
                break
            is_bold = line.startswith("Input:") or line.startswith("Output:") or line.startswith("Note:")
            font = "/F2" if is_bold else "/F1"
            size = "9.5"
            indent = 60 if (line.startswith("  ") or line.startswith("    ")) else 45
            clean_line = clean_text(line.strip())
            ops.append(f"BT {font} {size} Tf {indent} {y} Td ({clean_line}) Tj ET")
            y -= 14
        y -= 12

    # Footer
    ops.append("0.5 0.5 0.5 rg")
    ops.append(f"BT /F1 8 Tf 45 35 Td ({clean_text('Tide Lab Examination System - DO NOT DETACH OR SHARE - odd/even seat randomized paper')}) Tj ET")
    ops.append("0.8 0.8 0.8 RG 0.5 w")
    ops.append("40 48 m 555 48 l S")

    stream_data = "\n".join(ops).encode("latin1")
    
    objects = []
    def add_obj(body: bytes) -> int:
        objects.append(body)
        return len(objects)

    # Object 1: Catalog
    add_obj(b"<< /Type /Catalog /Pages 2 0 R >>")
    # Object 2: Pages
    add_obj(b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>")
    # Object 3: Page
    add_obj(b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Contents 4 0 R /Resources << /Font << /F1 5 0 R /F2 6 0 R >> >> >>")
    # Object 4: Contents
    add_obj(b"<< /Length " + str(len(stream_data)).encode() + b" >>\nstream\n" + stream_data + b"\nendstream")
    # Object 5: Font F1 (Helvetica)
    add_obj(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>")
    # Object 6: Font F2 (Helvetica-Bold)
    add_obj(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold /Encoding /WinAnsiEncoding >>")

    pdf = bytearray()
    pdf.extend(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offsets = []
    for i, obj in enumerate(objects):
        offsets.append(len(pdf))
        pdf.extend(f"{i+1} 0 obj\n".encode())
        pdf.extend(obj)
        pdf.extend(b"\nendobj\n")

    xref_offset = len(pdf)
    pdf.extend(f"xref\n0 {len(objects)+1}\n0000000000 65535 f \n".encode())
    for off in offsets:
        pdf.extend(f"{off:010d} 00000 n \n".encode())
    
    pdf.extend(f"trailer\n<< /Size {len(objects)+1} /Root 1 0 R >>\nstartxref\n{xref_offset}\n%%EOF\n".encode())

    filename.parent.mkdir(parents=True, exist_ok=True)
    filename.write_bytes(pdf)
    print(f"Generated {filename} ({len(pdf)} bytes)")

def main():
    target_dir = Path("demo/papers")
    target_dir.mkdir(parents=True, exist_ok=True)

    # --- SET A ---
    set_a_meta = ["Course: CS301 Algorithms & Networking Lab", "Assigned: Odd Seats (PC-01, PC-03...)", "Duration: 90 Mins", "Max Marks: 50"]
    set_a_sections = [
        ("INSTRUCTIONS TO CANDIDATES", [
            "1. Write all your solutions in main.c (or solution.py) located inside C:\\Exam\\<roll>\\.",
            "2. All workspace activity, active windows, and clipboard transfers are monitored by Tide.",
            "3. Any unauthorized websites or external code sources will result in auto-closure and flags.",
            "4. When finished, press the 'Submit' button in the floating Tide HUD bar at the top of your screen."
        ]),
        ("PROBLEM 1: Network Packet Priority Queue (Min-Heap) [25 Marks]", [
            "Implement a priority queue for a router simulator processing incoming IP packets.",
            "Each packet has an integer PacketID, an integer Priority (1 = highest), and arrival Timestamp.",
            "Requirements:",
            "  - InsertPacket(id, priority, timestamp): Insert in O(log N) using a min-heap.",
            "  - DispatchNext(): Remove and print the highest priority packet. Tie-break by lowest timestamp.",
            "Input:  N=4, Packets: (101, 3, 1000), (102, 1, 1005), (103, 2, 1010), (104, 1, 1002)",
            "Output: Dispatched order: 104 (Pri:1, Time:1002), 102 (Pri:1, Time:1005), 103, 101"
        ]),
        ("PROBLEM 2: Binary Search Tree Validation & Range Query [25 Marks]", [
            "Given a binary tree representation, verify whether it satisfies the strict BST property.",
            "If valid, compute the sum of all keys strictly within the range [Low, High].",
            "Requirements:",
            "  - IsValidBST(root): Return true if all left children < root < all right children.",
            "  - RangeSumBST(root, low, high): Return sum in O(K) where K is nodes in range.",
            "Input:  Tree: [15, 10, 20, 8, 12, 17, 25], Low = 10, High = 20",
            "Output: Valid: YES | Range Sum: 62 (10 + 12 + 15 + 17 + 20 = 62)"
        ])
    ]

    generate_pdf(target_dir / "Question_Paper_Set_A.pdf",
                 "CS301 Lab Examination — Fall 2026",
                 "Department of Computer Science & Engineering",
                 "A", set_a_meta, set_a_sections)

    # --- SET B ---
    set_b_meta = ["Course: CS301 Algorithms & Networking Lab", "Assigned: Even Seats (PC-02, PC-04...)", "Duration: 90 Mins", "Max Marks: 50"]
    set_b_sections = [
        ("INSTRUCTIONS TO CANDIDATES", [
            "1. Write all your solutions in main.c (or solution.py) located inside C:\\Exam\\<roll>\\.",
            "2. All workspace activity, active windows, and clipboard transfers are monitored by Tide.",
            "3. Any unauthorized websites or external code sources will result in auto-closure and flags.",
            "4. When finished, press the 'Submit' button in the floating Tide HUD bar at the top of your screen."
        ]),
        ("PROBLEM 1: Circular Ring Buffer for Audio Streaming [25 Marks]", [
            "Implement a fixed-size circular ring buffer for real-time audio packet buffering.",
            "The buffer holds a maximum capacity of K frame samples.",
            "Requirements:",
            "  - Enqueue(sample): Add sample in O(1). If full, overwrite oldest sample & increment drop count.",
            "  - Dequeue(): Retrieve and remove oldest sample in O(1). Return -1 if empty.",
            "  - DrainAll(): Return all available elements in FIFO order and reset buffer state.",
            "Input:  Capacity=3, Enqueue(10), Enqueue(20), Enqueue(30), Enqueue(40), Dequeue()",
            "Output: Overwritten count: 1 (Sample 10 dropped) | Dequeued: 20 | Remaining: [30, 40]"
        ]),
        ("PROBLEM 2: Graph Cycle Detection & Topological Task Scheduling [25 Marks]", [
            "You are given N build tasks with M directed prerequisites (U must finish before V).",
            "Requirements:",
            "  - Detect if deadlock exists (directed cycle). If yes, print 'DEADLOCK DETECTED'.",
            "  - If acyclic, output any valid linear sequence of task completion (Kahn's / DFS).",
            "Input:  N=4, Dependencies: (1->2), (1->3), (3->4), (2->4)",
            "Output: Cycle: NO | Valid Schedule: 1 -> 2 -> 3 -> 4"
        ])
    ]

    generate_pdf(target_dir / "Question_Paper_Set_B.pdf",
                 "CS301 Lab Examination — Fall 2026",
                 "Department of Computer Science & Engineering",
                 "B", set_b_meta, set_b_sections)

    # Also save clean text versions for easy copy/paste or viewing
    (target_dir / "Question_Paper_Set_A.txt").write_text(
        "CS301 Lab Examination — Set A (Odd Seats)\n" + "="*50 + "\n\n" +
        "\n\n".join(f"{h}\n{'-'*len(h)}\n" + "\n".join(lines) for h, lines in set_a_sections)
    )
    (target_dir / "Question_Paper_Set_B.txt").write_text(
        "CS301 Lab Examination — Set B (Even Seats)\n" + "="*50 + "\n\n" +
        "\n\n".join(f"{h}\n{'-'*len(h)}\n" + "\n".join(lines) for h, lines in set_b_sections)
    )
    print("Done generating sample papers.")

if __name__ == "__main__":
    main()
