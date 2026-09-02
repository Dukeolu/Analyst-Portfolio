"""
Shared simulation library for Case 02 (Sales & Customer Analytics).

Simulates a subscription customer base month-by-month so that churn
emerges from a realistic hazard function (contract type, tenure stage,
engagement, support friction, autopay, price) rather than being assigned
directly -- the same "simulate the mechanism, not the outcome" approach
used in Case 01.
"""
import numpy as np
import pandas as pd

ANALYSIS_DATE = pd.Timestamp("2025-12-31")
REGIONS = ["Northeast", "Midwest", "South", "West"]
CHANNELS = ["Organic", "Paid Search", "Referral", "Sales-Assisted"]
CONTRACTS = ["Month-to-month", "One year", "Two year"]
CONTRACT_PROB = [0.55, 0.30, 0.15]
PLAN_TIERS = {"Basic": 15.0, "Standard": 35.0, "Premium": 65.0}
PLAN_PROB = [0.40, 0.40, 0.20]
ADDON_PRICE = 8.0

BASE_HAZARD = {"Month-to-month": 0.042, "One year": 0.010, "Two year": 0.005}


def build_customer_base(n: int = 6000, seed: int = 5) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    signup_offset_months = rng.integers(1, 30, size=n)  # signed up 1-29 months before analysis date
    signup_month = [ANALYSIS_DATE.to_period("M") - int(m) for m in signup_offset_months]

    contract_type = rng.choice(CONTRACTS, size=n, p=CONTRACT_PROB)
    plan_tier = rng.choice(list(PLAN_TIERS.keys()), size=n, p=PLAN_PROB)
    addon_count = rng.choice([0, 1, 2, 3, 4], size=n, p=[0.35, 0.30, 0.20, 0.10, 0.05])
    base_price = np.array([PLAN_TIERS[t] for t in plan_tier])
    monthly_charge = np.round(base_price + addon_count * ADDON_PRICE + rng.normal(0, 2, n), 2)

    autopay_prob = np.where(contract_type == "Month-to-month", 0.62, 0.80)
    autopay = rng.random(n) < autopay_prob

    signup_channel = rng.choice(CHANNELS, size=n, p=[0.35, 0.30, 0.20, 0.15])
    region = rng.choice(REGIONS, size=n)

    base_engagement = np.clip(rng.normal(65, 18, n), 5, 100)

    return pd.DataFrame({
        "customer_id": [f"CUST-{i:05d}" for i in range(1, n + 1)],
        "signup_month": signup_month,
        "contract_type": contract_type,
        "plan_tier": plan_tier,
        "addon_count": addon_count,
        "monthly_charge": monthly_charge,
        "autopay": autopay,
        "signup_channel": signup_channel,
        "region": region,
        "base_engagement": base_engagement,
    })


def simulate_churn(customers: pd.DataFrame, seed: int = 17) -> pd.DataFrame:
    """
    Month-by-month hazard simulation from signup to ANALYSIS_DATE (or churn,
    whichever comes first). Returns a cross-sectional customer table with
    tenure_months, churned flag, and lifetime engagement/ticket summaries.
    """
    rng = np.random.default_rng(seed)
    rows = []

    for c in customers.itertuples(index=False):
        months_available = (ANALYSIS_DATE.to_period("M") - c.signup_month).n
        base = BASE_HAZARD[c.contract_type]
        engagement_hist, ticket_hist = [], []
        churned = False
        tenure = 0

        for t in range(1, months_available + 1):
            month_engagement = float(np.clip(rng.normal(c.base_engagement, 8), 0, 100))
            monthly_tickets = rng.poisson(max(0.02, (70 - month_engagement) / 70 * 0.6))
            engagement_hist.append(month_engagement)
            ticket_hist.append(monthly_tickets)

            tenure_factor = 1.9 if t <= 3 else (1.0 if t <= 12 else (0.75 if t <= 24 else 0.55))
            renewal_spike = 1.0
            if c.contract_type == "One year" and t % 12 == 0:
                renewal_spike = 3.2
            elif c.contract_type == "Two year" and t % 24 == 0:
                renewal_spike = 3.0

            engagement_factor = 1 + max(0.0, (55 - month_engagement)) / 40
            tickets_factor = 1 + monthly_tickets * 0.18
            autopay_factor = 1.0 if c.autopay else 1.12
            price_factor = 1 + (max(0.0, c.monthly_charge - 45) / 300) * (1.0 if month_engagement < 55 else 0.3)

            hazard = min(0.35, base * tenure_factor * renewal_spike * engagement_factor * tickets_factor * autopay_factor * price_factor)

            tenure = t
            if rng.random() < hazard:
                churned = True
                break

        n_months = len(engagement_hist)
        avg_engagement = float(np.mean(engagement_hist)) if n_months else c.base_engagement
        tickets_last_90d = int(sum(ticket_hist[-3:])) if n_months else 0

        rows.append({
            "customer_id": c.customer_id,
            "signup_month": str(c.signup_month),
            "contract_type": c.contract_type,
            "plan_tier": c.plan_tier,
            "addon_count": c.addon_count,
            "monthly_charge": c.monthly_charge,
            "autopay": "Yes" if c.autopay else "No",
            "signup_channel": c.signup_channel,
            "region": c.region,
            "tenure_months": tenure,
            "months_observable": months_available,
            "avg_engagement_score": round(avg_engagement, 1),
            "support_tickets_90d": tickets_last_90d,
            "churned": "Yes" if churned else "No",
        })

    return pd.DataFrame(rows)
