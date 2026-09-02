"""Extra 06 -- Step 1: generate the messy raw weekly shipping log (the 'source system export')."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))
from lib_ops_log_sim import build_raw_log

BASE = Path(__file__).resolve().parents[1]
RAW = BASE / "data" / "raw"
RAW.mkdir(parents=True, exist_ok=True)

log = build_raw_log()
log.to_csv(RAW / "raw_shipping_log.csv", index=False)

print(f"raw rows written: {len(log):,}")
print(f"duplicate rows present: {log.duplicated().sum():,}")
print(f"missing warehouse: {(log['warehouse'] == '').sum():,}")
print(f"negative units: {(log['units'] < 0).sum():,}")
print(f"status value variants: {sorted(log['status'].unique())}")
