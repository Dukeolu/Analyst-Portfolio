import sqlite3
import pandas as pd
from pathlib import Path

DB_PATH = Path("data/security.db")
DB_PATH.parent.mkdir(exist_ok=True)
if DB_PATH.exists():
    DB_PATH.unlink()

conn = sqlite3.connect(DB_PATH)

auth = pd.read_csv("data/raw/auth_events.csv")
fw = pd.read_csv("data/raw/firewall_events.csv")

auth.to_sql("auth_events", conn, index=False)
fw.to_sql("firewall_events", conn, index=False)

conn.execute("CREATE INDEX idx_auth_ip ON auth_events(source_ip)")
conn.execute("CREATE INDEX idx_auth_user ON auth_events(username)")
conn.execute("CREATE INDEX idx_auth_type ON auth_events(event_type)")
conn.execute("CREATE INDEX idx_fw_ip ON firewall_events(source_ip)")
conn.commit()

print(f"Built {DB_PATH} with {len(auth)} auth events and {len(fw)} firewall log rows.")
conn.close()
