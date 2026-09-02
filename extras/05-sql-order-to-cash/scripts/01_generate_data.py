"""Extra 05 -- Step 1: generate the simulated order-to-cash dataset."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))
from lib_o2c_sim import build_customers, build_orders_invoices_payments

BASE = Path(__file__).resolve().parents[1]
RAW = BASE / "data" / "raw"
RAW.mkdir(parents=True, exist_ok=True)

customers = build_customers()
orders, invoices, payments = build_orders_invoices_payments(customers)

customers.to_csv(RAW / "customers.csv", index=False)
orders.to_csv(RAW / "orders.csv", index=False)
invoices.to_csv(RAW / "invoices.csv", index=False)
payments.to_csv(RAW / "payments.csv", index=False)

print(f"customers:  {len(customers):,}")
print(f"orders:     {len(orders):,}")
print(f"invoices:   {len(invoices):,}")
print(f"payments:   {len(payments):,}")
print(f"\nrisk tier by segment:")
print(customers.groupby(["segment", "risk_tier"]).size().unstack(fill_value=0))
