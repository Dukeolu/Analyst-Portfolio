"""
Order-to-cash simulation.

The setup a finance team usually assumes: Enterprise accounts (long Net-60
terms, big invoices) are the DSO problem. The mechanism actually seeded here
says otherwise -- payment delay is driven by risk_tier, not segment, and
"High" risk accounts are disproportionately concentrated in the SMB segment
(short Net-15 terms, small invoices, but paid very late). The SQL in this
project is meant to surface that on its own.
"""
import numpy as np
import pandas as pd

RNG_SEED = 71
START_DATE = pd.Timestamp("2024-01-01")
END_DATE = pd.Timestamp("2025-12-31")
SNAPSHOT_DATE = pd.Timestamp("2025-12-31")  # for AR aging

SEGMENTS = ["SMB", "Mid-Market", "Enterprise"]
SEGMENT_WEIGHTS = [0.60, 0.30, 0.10]
SEGMENT_TERMS = {"SMB": 15, "Mid-Market": 30, "Enterprise": 60}
SEGMENT_ORDER_AMOUNT = {  # (lognormal mean, sigma) in dollars
    "SMB": (7.8, 0.5),          # ~ $2,400 median
    "Mid-Market": (9.3, 0.45),  # ~ $10,900 median
    "Enterprise": (10.8, 0.4),  # ~ $49,000 median
}
SEGMENT_ORDERS_PER_YEAR = {"SMB": 4, "Mid-Market": 8, "Enterprise": 14}

REGIONS = ["Northeast", "South", "Midwest", "West"]

# Risk tier is concentrated differently by segment -- this is the seeded mechanism.
RISK_TIER_BY_SEGMENT = {
    "SMB": {"Low": 0.55, "Medium": 0.25, "High": 0.20},
    "Mid-Market": {"Low": 0.70, "Medium": 0.25, "High": 0.05},
    "Enterprise": {"Low": 0.80, "Medium": 0.18, "High": 0.02},
}

# Days paid AFTER due date, by risk tier (can be negative = early). This is
# what actually drives DSO -- independent of segment/terms.
DELAY_BY_RISK = {"Low": (-2, 4), "Medium": (8, 6), "High": (25, 12)}

PARTIAL_PAYMENT_RATE = 0.15  # share of invoices paid in two installments
UNPAID_RATE = 0.02  # share of invoices still fully outstanding at snapshot


def build_customers(n=150, seed=RNG_SEED):
    rng = np.random.default_rng(seed)
    segment = rng.choice(SEGMENTS, size=n, p=SEGMENT_WEIGHTS)
    risk_tier = np.array([
        rng.choice(list(RISK_TIER_BY_SEGMENT[s].keys()), p=list(RISK_TIER_BY_SEGMENT[s].values()))
        for s in segment
    ])
    region = rng.choice(REGIONS, size=n)
    df = pd.DataFrame({
        "customer_id": [f"C{1000+i}" for i in range(n)],
        "customer_name": [f"{seg} Customer {i:03d}" for i, seg in enumerate(segment)],
        "segment": segment,
        "region": region,
        "payment_terms_days": [SEGMENT_TERMS[s] for s in segment],
        "risk_tier": risk_tier,
    })
    return df


def build_orders_invoices_payments(customers, seed=RNG_SEED + 1):
    rng = np.random.default_rng(seed)
    order_rows, invoice_rows, payment_rows = [], [], []
    order_seq, invoice_seq, payment_seq = 1, 1, 1
    span_years = (END_DATE - START_DATE).days / 365.25

    for cust in customers.itertuples():
        n_orders = rng.poisson(SEGMENT_ORDERS_PER_YEAR[cust.segment] * span_years)
        if n_orders == 0:
            continue
        order_days = np.sort(rng.integers(0, (END_DATE - START_DATE).days, size=n_orders))
        mu, sigma = SEGMENT_ORDER_AMOUNT[cust.segment]

        for od in order_days:
            order_date = START_DATE + pd.Timedelta(days=int(od))
            amount = round(float(rng.lognormal(mu, sigma)), 2)
            order_id = f"O{order_seq:06d}"; order_seq += 1
            order_rows.append({
                "order_id": order_id, "customer_id": cust.customer_id,
                "order_date": order_date.date(), "order_amount": amount,
            })

            invoice_date = order_date + pd.Timedelta(days=int(rng.integers(0, 3)))
            due_date = invoice_date + pd.Timedelta(days=cust.payment_terms_days)
            invoice_id = f"INV{invoice_seq:06d}"; invoice_seq += 1
            invoice_rows.append({
                "invoice_id": invoice_id, "order_id": order_id, "customer_id": cust.customer_id,
                "invoice_date": invoice_date.date(), "due_date": due_date.date(),
                "invoice_amount": amount,
            })

            # skip payment generation for invoices too close to the snapshot
            # to still be due -- otherwise "unpaid" is indistinguishable from "not due yet"
            if due_date > SNAPSHOT_DATE:
                continue

            roll = rng.random()
            if roll < UNPAID_RATE:
                continue  # no payment rows at all -- fully outstanding at snapshot

            lo, hi = DELAY_BY_RISK[cust.risk_tier]
            delay = int(np.clip(rng.normal(lo, hi), -10, 180))
            pay_date = due_date + pd.Timedelta(days=delay)
            if pay_date > SNAPSHOT_DATE:
                pay_date = SNAPSHOT_DATE  # can't observe a payment in the future

            if roll < UNPAID_RATE + PARTIAL_PAYMENT_RATE:
                # two installments: a partial payment near the due date, remainder later
                first_amt = round(amount * float(rng.uniform(0.4, 0.75)), 2)
                first_date = due_date + pd.Timedelta(days=int(np.clip(rng.normal(lo * 0.5, hi * 0.5), -10, 90)))
                first_date = min(first_date, SNAPSHOT_DATE)
                payment_rows.append({
                    "payment_id": f"P{payment_seq:06d}", "invoice_id": invoice_id,
                    "payment_date": first_date.date(), "payment_amount": first_amt,
                })
                payment_seq += 1
                second_date = max(pay_date, first_date + pd.Timedelta(days=3))
                second_date = min(second_date, SNAPSHOT_DATE)
                payment_rows.append({
                    "payment_id": f"P{payment_seq:06d}", "invoice_id": invoice_id,
                    "payment_date": second_date.date(), "payment_amount": round(amount - first_amt, 2),
                })
                payment_seq += 1
            else:
                payment_rows.append({
                    "payment_id": f"P{payment_seq:06d}", "invoice_id": invoice_id,
                    "payment_date": pay_date.date(), "payment_amount": amount,
                })
                payment_seq += 1

    return (pd.DataFrame(order_rows), pd.DataFrame(invoice_rows), pd.DataFrame(payment_rows))
