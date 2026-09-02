"""
Case 01 -- Step 2: load the raw CSVs into SQLite and run the SQL analysis.

Loading real CSVs into a real SQL database (rather than just reading them
with pandas) is deliberate -- it's the same workflow as pulling from a
data warehouse, and the .sql files in ../sql/ are meant to be run and read
on their own.
"""
import sqlite3
from pathlib import Path
import pandas as pd

BASE = Path(__file__).resolve().parents[1]
RAW = BASE / "data" / "raw"
SQL = BASE / "sql"
OUT = BASE / "data" / "processed"
OUT.mkdir(parents=True, exist_ok=True)
DB_PATH = OUT / "case01.db"

DB_PATH.unlink(missing_ok=True)
conn = sqlite3.connect(DB_PATH)

conn.executescript((SQL / "01_schema.sql").read_text())

pd.read_csv(RAW / "skus.csv").to_sql("skus", conn, if_exists="append", index=False)
pd.read_csv(RAW / "orders.csv").to_sql("orders", conn, if_exists="append", index=False)
pd.read_csv(RAW / "inventory_snapshots.csv").to_sql("inventory_snapshots", conn, if_exists="append", index=False)
conn.commit()

queries = {
    "abc_classification": "02_abc_classification.sql",
    "fill_rate_by_tier": "03_fill_rate_by_segment.sql",
    "avg_inventory_by_sku": "04_avg_inventory_by_sku.sql",
}

for out_name, sql_file in queries.items():
    df = pd.read_sql(SQL.joinpath(sql_file).read_text(), conn)
    df.to_csv(OUT / f"{out_name}.csv", index=False)
    print(f"{sql_file:35s} -> {out_name}.csv  ({len(df):,} rows)")

print("\nfill_rate_by_tier:")
print(pd.read_csv(OUT / "fill_rate_by_tier.csv").to_string(index=False))

conn.close()
print(f"\nSQLite DB written to {DB_PATH.relative_to(BASE)}")
