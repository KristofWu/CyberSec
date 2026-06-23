
import time
import sqlite3
import pandas as pd
from sklearn.ensemble import IsolationForest
import matplotlib.pyplot as plt


class FirewallAnalyser:
    

    def __init__(self, filepath):
        self.filepath = filepath
        self.records = []
        self.results = None

    # ----- parsing -------------------------------------------------------

    def parse_to_lines(self, lines): 
        for line in lines:
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

    def parse(self):
        with open(self.filepath) as file:
            self.parse_to_lines(file)

    # ----- analysis ------------------------------------------------------

    def analyze(self):
        df = pd.DataFrame(self.records)
        df["is_blocked"] = df["action"] != "ACCEPT"

        group = df.groupby("src_ip").agg(
            total=("action", "count"),
            unique_ports=("dpt", "nunique"),
            blocked=("is_blocked", "sum"),
        )
        group["blocked_ratio"] = group["blocked"] / group["total"]

        X = group[["total", "unique_ports", "blocked", "blocked_ratio"]]
        model = IsolationForest(contamination=0.2, random_state=42)
        group["anomaly"] = model.fit_predict(X)   # 1 = normal, -1 = anomaly

        self.results = group

    def run(self):
        self.parse()
        self.analyze()

    # ----- output --------------------------------------------------------

    def report(self):
        print(self.results[self.results["anomaly"] == -1])

    def save_report(self):
        anomalies = self.results[self.results["anomaly"] == -1]
        anomalies = anomalies.reset_index()
        anomalies.to_json("report.json", orient="records", indent=2)

    def save_to_db(self):
        conn = sqlite3.connect("firewall.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM threats")

        anomalies = self.results[self.results["anomaly"] == -1]
        anomalies = anomalies.reset_index()   # turn src_ip index into a column
        anomalies.to_sql("threats", conn, if_exists="append", index=False)

        conn.commit()
        conn.close()

    def plot(self):
        plt.scatter(self.results["total"], self.results["unique_ports"],
                    c=self.results["anomaly"])
        plt.xlabel("Number of actions")
        plt.ylabel("Number of different ports")
        plt.title("Anomalies detection based on firewall logs")
        for ip, row in self.results.iterrows():
            if row["anomaly"] == -1:
                plt.text(row.total, row.unique_ports, ip)
        plt.show()

    # ----- streaming -----------------------------------------------------

    def stream(self):
        buffer = []
        with open(self.filepath, "r") as file:
            for line in file:
                buffer.append(line)

                if len(buffer) >= 50:
                    self.parse_to_lines(buffer)   # add chunk to self.records
                    self.analyze()                # analyse everything so far
                    self.save_to_db()
                    buffer = []                   # clear buffer (records stay)

                time.sleep(0.05)

            if buffer:
                self.parse_to_lines(buffer)
                self.analyze()
                self.save_to_db()


def init_db():
    """Create the 'threats' table if it doesn't exist yet."""
    conn = sqlite3.connect("firewall.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS threats (
            src_ip TEXT,
            total INTEGER,
            unique_ports INTEGER,
            blocked INTEGER,
            blocked_ratio REAL,
            anomaly INTEGER
        )
    """)
    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_db()   # make sure the table exists

    analyzer = FirewallAnalyser("firewall_big.log")

    # Batch mode:
    analyzer.run()
    analyzer.report()
    analyzer.save_report()
    analyzer.save_to_db()
    analyzer.plot()

    # Streaming mode (uncomment to run the simulated live stream instead):
    # streamer = FirewallAnalyser("firewall_big.log")
    # streamer.stream()
