"""
Local VPC Flow Log analysis (exploration).
==========================================
Reads a plain-text VPC Flow Log file and produces several security insights:
top attacker IPs, most-targeted ports, port-scan detection, and overall stats.

This is the local/notebook version used to develop the detection logic before
porting the core to AWS Lambda (see src/lambda_function.py).

Usage:
    python flow_analysis.py path/to/logs.log
"""

import sys
from collections import Counter

# VPC Flow Log default format — field positions (0-indexed)
SRCADDR = 3
DSTADDR = 4
DSTPORT = 6
ACTION = 12

PORT_NAMES = {
    "22": "SSH", "23": "Telnet", "80": "HTTP", "443": "HTTPS",
    "3389": "RDP", "445": "SMB", "8080": "HTTP-alt", "8443": "HTTPS-alt",
    "21": "FTP", "10000": "Webmin", "2003": "Carbon/Graphite",
}


def parse_flow(line):
    parts = line.split()
    return {
        "srcaddr": parts[SRCADDR],
        "dstaddr": parts[DSTADDR],
        "dstport": parts[DSTPORT],
        "action": parts[ACTION],
    }


def analyze(path):
    attacker_ips = Counter()
    attacked_ports = Counter()
    ip_ports = {}                 # ip -> set of ports it tried
    unique_attackers = set()
    rejects = accepts = 0

    with open(path, "r") as f:
        for line in f:
            parts = line.split()
            if len(parts) < 14:
                continue
            p = parse_flow(line)
            if p["action"] == "REJECT":
                rejects += 1
                attacker_ips[p["srcaddr"]] += 1
                attacked_ports[p["dstport"]] += 1
                unique_attackers.add(p["srcaddr"])
                ip_ports.setdefault(p["srcaddr"], set()).add(p["dstport"])
            elif p["action"] == "ACCEPT":
                accepts += 1

    # --- report ---
    total = rejects + accepts
    print(f"Total flows: {total}")
    print(f"REJECT (blocked): {rejects}  ({rejects / total * 100:.1f}%)")
    print(f"ACCEPT (allowed): {accepts}")
    print(f"Unique attacker IPs: {len(unique_attackers)}\n")

    print("Top attacker IPs:")
    for ip, n in attacker_ips.most_common(5):
        print(f"  {ip}: {n}")

    print("\nTop targeted ports:")
    for port, n in attacked_ports.most_common(5):
        print(f"  {port} ({PORT_NAMES.get(port, 'Unknown')}): {n}")

    print("\nPort scanners (3+ distinct ports):")
    for ip, ports in ip_ports.items():
        if len(ports) >= 3:
            print(f"  {ip}: {len(ports)} ports {sorted(ports)}")


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "data/logs.log"
    analyze(path)
