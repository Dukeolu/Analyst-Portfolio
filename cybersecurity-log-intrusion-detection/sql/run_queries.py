import re
import sqlite3
import pandas as pd

conn = sqlite3.connect("data/security.db")

with open("sql/queries.sql") as f:
    sql_text = f.read()

# Split on "-- Q<n>." labelled comment blocks
blocks = re.split(r"(?=-- Q\d+\.)", sql_text)
for block in blocks:
    block = block.strip()
    if not block:
        continue
    header_match = re.match(r"-- (Q\d+\..*?)(?:\n-- |\n\n|$)", block, re.DOTALL)
    label = block.split("\n")[0].lstrip("-- ").strip()
    # Grab the actual SQL statement (strip leading comment lines)
    lines = block.split("\n")
    sql_lines = [l for l in lines if not l.strip().startswith("--")]
    query = "\n".join(sql_lines).strip()
    if not query:
        continue
    print(f"\n=== {label} ===")
    try:
        df = pd.read_sql(query, conn)
        print(df.to_string(index=False))
    except Exception as e:
        print(f"(skipped: {e})")

conn.close()
