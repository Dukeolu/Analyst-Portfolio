"""Extra 08 -- Step 1: generate the simulated weekly demand series."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))
from lib_demand_sim import build_demand

BASE = Path(__file__).resolve().parents[1]
RAW = BASE / "data" / "raw"
RAW.mkdir(parents=True, exist_ok=True)

df = build_demand()
df.to_csv(RAW / "weekly_demand.csv", index=False)
print(f"weeks: {len(df)}  |  range: {df['week_start'].min().date()} to {df['week_start'].max().date()}")
print(f"units_sold: min={df['units_sold'].min()} max={df['units_sold'].max()} mean={df['units_sold'].mean():.0f}")
