"""Load the raw CSVs into a SQLite database for the SQL analysis step."""
import sqlite3
import pandas as pd

conn = sqlite3.connect("data/energy.db")

sites = pd.read_csv("data/raw/sites.csv")
generation = pd.read_csv("data/raw/generation.csv", parse_dates=["timestamp"])
market = pd.read_csv("data/raw/market.csv", parse_dates=["timestamp"])

sites.to_sql("sites", conn, if_exists="replace", index=False)
generation.to_sql("generation", conn, if_exists="replace", index=False)
market.to_sql("market", conn, if_exists="replace", index=False)

conn.execute("CREATE INDEX IF NOT EXISTS idx_gen_ts ON generation(timestamp);")
conn.execute("CREATE INDEX IF NOT EXISTS idx_gen_site ON generation(site_id);")
conn.execute("CREATE INDEX IF NOT EXISTS idx_mkt_ts ON market(timestamp);")
conn.commit()

print("Tables loaded:", conn.execute(
    "SELECT name FROM sqlite_master WHERE type='table'"
).fetchall())
for t in ["sites", "generation", "market"]:
    n = conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
    print(f"  {t}: {n:,} rows")
conn.close()
