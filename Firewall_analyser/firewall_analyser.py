import pandas as pd
from sklearn.ensemble import IsolationForest
import matplotlib.pyplot as plt

class FirewallAnalyser:
    def __init__(self, filepath):
        self.filepath = filepath
        self.records = []
        self.results = None
    
    def parse(self):
        with open(self.filepath) as file:
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

                self.records.append(record) 
    
    def analyze(self):
        df = pd.DataFrame(self.records)
        df["is_blocked"] = df["action"] != "ACCEPT"

        group = df.groupby("src_ip").agg(
            total = ("action", "count"),
            unique_ports = ("dpt", "nunique"),
            blocked = ("is_blocked", "sum"),
        )

        group["blocked_ratio"] = group["blocked"] / group["total"]

        X = group[["total", "unique_ports", "blocked", "blocked_ratio"]]

        model = IsolationForest(contamination=0.2, random_state=42)

        group["anomaly"] = model.fit_predict(X)

        self.results = group
    
    def run(self):
        self.parse()
        self.analyze()

    def report(self):
        print(self.results[self.results["anomaly"] == -1])

    def save_report(self):
        anomalies = self.results[self.results["anomaly"] == -1]
        anomalies = anomalies.reset_index()
        anomalies.to_json("report.json", orient = "records", indent = 2)

    def plot(self):

        plt.scatter(self.results["total"], self.results["unique_ports"], c = self.results["anomaly"])
        plt.xlabel("Number of actions")
        plt.ylabel("Number of different ports")
        plt.title("Anomalies detection based on firewall logs")
        for ip, row in self.results.iterrows():
            if row["anomaly"] == -1:
                plt.text(row.total, row.unique_ports, ip)
        plt.show()

        
analyzer = FirewallAnalyser("firewall_big.log")
analyzer.run()
analyzer.report()
analyzer.save_report()
analyzer.plot()
pd.DataFrame(analyzer.records).info()