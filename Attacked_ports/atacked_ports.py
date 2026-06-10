
def blocked_dpts():
    for port, count in blocked_ports.items():
        print(f"Port: {port} was attacked: {count} times")

blocked_ports = {}

try:
    with open("firewall.log", "r") as file:
        for line in file:
            dpt = None
            act = None
            parts = line.strip().split()
            for part in parts:
                if part.startswith("DPT="):
                    dpt = part.split("=", 1)[1]
                elif part.startswith("ACTION="):
                    act = part.split("=", 1)[1]
            if act == "DROP" or act == "REJECT":
                if dpt in blocked_ports:
                    blocked_ports[dpt] = blocked_ports[dpt] + 1
                else:
                    blocked_ports[dpt] = 1
                    
                    
except FileNotFoundError:
    print("File does not exist")

blocked_dpts()