import pandas as pd
from sklearn.ensemble import IsolationForest
import matplotlib.pyplot as plt


records = []

try:
    with open("firewall_big.log", "r") as file:
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


df = pd.DataFrame(records)
df["is_blocked"] = df["action"] != "ACCEPT"


group = df.groupby("src_ip").agg(
    total = ("action", "count"),
    unique_ports = ("dpt", "nunique"),
    blocked = ("is_blocked", "sum"),
)
group["blocked_ratio"] = group["blocked"] / group["total"]
group

X = group[["total", "unique_ports", "blocked", "blocked_ratio"]]


model = IsolationForest(contamination=0.2, random_state=42)

group["anomaly"] = model.fit_predict(X)

plt.scatter(group["total"], group["unique_ports"], c = group["anomaly"])
plt.xlabel("Number of actions")
plt.ylabel("Number of different ports")
plt.title("Anomalies detection based on firewall logs")
for ip, row in group.iterrows():
    if row["anomaly"] == -1:
        plt.text(row.total, row.unique_ports, ip)
plt.show()

print("===Detected anomalies===")
print(group[group["anomaly"] == -1])




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



 
