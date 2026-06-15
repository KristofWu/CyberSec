
def show_recs():
    for r in records:
        print(r)

records = []

try:
    with open("firewall.log", "r") as file:
        for line in file:
            source = None
            action = None
            dpt = None
            protocol = None
            cleaned_line = line.split()
            for part in cleaned_line:
                if part.startswith("SRC="):
                    source = part.split("=", 1)[1]    
                elif part.startswith("ACTION="):
                    action = part.split("=", 1)[1]
                elif part.startswith("DPT="):
                    dpt = part.split("=", 1)[1]
                elif part.startswith("PROTO="):
                    protocol = part.split("=", 1)[1]
            record = {
                "src_ip": source,
                "action": action,
                "dpt": dpt,
                "protocol": protocol
            }

            records.append(record)     
                
except FileNotFoundError:
  print("File does not exist")  

show_recs()





#def ip_counting():
#    for ip, count in ip_counts.items():
#        print(f"Address IP: {ip}, has been detected {count} times")

#def action_counting():
#    for actions, count in action_counts.items():
#        print(f"Action: {actions} has been detected {count} times")

#ip_counts = {}
#action_counts = {}


# Collecting SRC IPs and ACTIONS without unnecessary characters

#try:
#    with open("firewall.log", "r") as file:
#        for line in file:
#            cleaned_line = line.split()
#            for part in cleaned_line:
#                if part.startswith("SRC="):
#                    cleaned = part.split("=", 1)[1] #divide text if you see "=", 1 - 1 divide max and stop after the first char, [1] means first element after "=", [0] would be the char before "="
#                    if cleaned in ip_counts:
#                        ip_counts[cleaned] = ip_counts[cleaned] + 1
#                    else:
#                        ip_counts[cleaned] = 1  
#                elif part.startswith("ACTION="):
#                    cleaned = part.split("=", 1)[1]
#                    if cleaned in action_counts:
#                        action_counts[cleaned] = action_counts[cleaned] + 1
#                    else:
#                        action_counts[cleaned] = 1                                               
#except FileNotFoundError:
#    print("File does not exist")

#ip_counting()
#action_counting() 



 
