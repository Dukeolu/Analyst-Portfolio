import sqlite3
import pandas as pd
from pathlib import Path

DB_PATH = Path("data/helpdesk.db")
DB_PATH.parent.mkdir(exist_ok=True)
if DB_PATH.exists():
    DB_PATH.unlink()

conn = sqlite3.connect(DB_PATH)

tickets = pd.read_csv("data/raw/tickets.csv")
technicians = pd.read_csv("data/raw/technicians.csv")

# Precompute the specialty-match flag here (in Python, from the technicians
# table) rather than re-deriving it inside every SQL query -- the same join
# a real analyst would do once and reuse, rather than repeating fragile
# string-parsing logic in five different queries.
spec_map = {r.tech_id: set(r.specialty_categories.split(";")) for r in technicians.itertuples()}
tickets["assignment_type"] = tickets.apply(
    lambda r: "Specialist match" if r.category in spec_map[r.assigned_tech_id] else "Off-specialty",
    axis=1,
)

tickets.to_sql("tickets", conn, index=False)
technicians.to_sql("technicians", conn, index=False)

conn.execute("CREATE INDEX idx_tickets_category ON tickets(category)")
conn.execute("CREATE INDEX idx_tickets_tech ON tickets(assigned_tech_id)")
conn.execute("CREATE INDEX idx_tickets_priority ON tickets(priority)")
conn.execute("CREATE INDEX idx_tickets_assignment_type ON tickets(assignment_type)")
conn.commit()

print(f"Built {DB_PATH} with {len(tickets)} tickets and {len(technicians)} technicians.")
print(tickets["assignment_type"].value_counts())
conn.close()
