"""
Shared simulation library for Case 03 (Finance & Budgeting).

Simulates 24 months of budget vs. actual performance by region x category
for a mid-size distributor. Budgets are set once at the start of the year
using normal planning assumptions; actuals diverge from budget through two
deliberate, realistic mechanisms -- a supplier cost overrun concentrated
in one import-heavy category/region, and discount creep concentrated in
one price-competitive category -- on top of ordinary month-to-month noise
everywhere else. The point is that the leak is real but *localized*, the
way it actually is in a budget review: most of the business is on plan.
"""
import numpy as np
import pandas as pd

REGIONS = ["Northeast", "Midwest", "South", "West"]
CATEGORIES = {
    # category: (monthly_revenue_range, budget_discount_pct, budget_cogs_pct)
    "Electronics Accessories": ((180_000, 260_000), 0.10, 0.62),
    "Home & Kitchen":          ((140_000, 210_000), 0.12, 0.58),
    "Office Supplies":         ((90_000, 150_000), 0.08, 0.55),
    "Personal Care":           ((110_000, 170_000), 0.11, 0.54),
    "Outdoor & Sporting":      ((80_000, 140_000), 0.13, 0.60),
    "Pet Supplies":            ((85_000, 130_000), 0.09, 0.56),
}
MONTHS = pd.period_range("2024-01", periods=24, freq="M")
SEASONAL = {1:.90,2:.88,3:.95,4:.98,5:1.00,6:1.02,7:1.00,8:1.03,9:1.05,10:1.10,11:1.30,12:1.22}

# The two deliberate leaks -- both stated plainly here so the "solution"
# step is checkable against how the data was built, not a black box.
COGS_OVERRUN = {("Electronics Accessories", "West"): 0.055, ("Electronics Accessories", "Northeast"): 0.035}
DISCOUNT_CREEP = {("Outdoor & Sporting", "South"): 0.065, ("Outdoor & Sporting", "Midwest"): 0.045}


def build_budget(seed: int = 3) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    rows = []
    for region in REGIONS:
        region_factor = rng.uniform(0.85, 1.15)
        for cat, (rev_rng, disc, cogs) in CATEGORIES.items():
            base_rev = rng.uniform(*rev_rng) * region_factor
            for m in MONTHS:
                seasonal = SEASONAL[m.month]
                growth = 1 + 0.008 * (m.ordinal - MONTHS[0].ordinal)  # mild planned growth
                budget_revenue = round(base_rev * seasonal * growth, 2)
                rows.append({
                    "month": str(m), "region": region, "category": cat,
                    "budget_revenue": budget_revenue,
                    "budget_discount_pct": disc,
                    "budget_cogs_pct": cogs,
                })
    return pd.DataFrame(rows)


def simulate_actuals(budget: pd.DataFrame, seed: int = 29) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    df = budget.copy()

    # ordinary noise everywhere
    df["actual_revenue"] = (df["budget_revenue"] * rng.normal(1.0, 0.05, len(df))).round(2)
    df["actual_discount_pct"] = np.clip(df["budget_discount_pct"] + rng.normal(0, 0.01, len(df)), 0.02, 0.5)
    df["actual_cogs_pct"] = np.clip(df["budget_cogs_pct"] + rng.normal(0, 0.008, len(df)), 0.2, 0.9)

    months_sorted = list(MONTHS)
    for (cat, region), overrun in COGS_OVERRUN.items():
        mask = (df.category == cat) & (df.region == region)
        # cost overrun ramps in over the year rather than appearing overnight
        ramp = df.loc[mask, "month"].apply(lambda m: months_sorted.index(pd.Period(m)) / (len(months_sorted) - 1))
        df.loc[mask, "actual_cogs_pct"] = np.clip(
            df.loc[mask, "actual_cogs_pct"] + overrun * (0.3 + 0.7 * ramp) + rng.normal(0, 0.006, mask.sum()),
            0.2, 0.95
        )

    for (cat, region), creep in DISCOUNT_CREEP.items():
        mask = (df.category == cat) & (df.region == region)
        ramp = df.loc[mask, "month"].apply(lambda m: months_sorted.index(pd.Period(m)) / (len(months_sorted) - 1))
        df.loc[mask, "actual_discount_pct"] = np.clip(
            df.loc[mask, "actual_discount_pct"] + creep * (0.4 + 0.6 * ramp) + rng.normal(0, 0.008, mask.sum()),
            0.02, 0.6
        )

    for col in ["budget_discount_pct", "budget_cogs_pct", "actual_discount_pct", "actual_cogs_pct"]:
        df[col] = df[col].round(4)

    # derived P&L
    df["budget_net_revenue"] = (df["budget_revenue"] * (1 - df["budget_discount_pct"])).round(2)
    df["budget_cogs"] = (df["budget_net_revenue"] * df["budget_cogs_pct"]).round(2)
    df["budget_profit"] = (df["budget_net_revenue"] - df["budget_cogs"]).round(2)

    df["actual_net_revenue"] = (df["actual_revenue"] * (1 - df["actual_discount_pct"])).round(2)
    df["actual_cogs"] = (df["actual_net_revenue"] * df["actual_cogs_pct"]).round(2)
    df["actual_profit"] = (df["actual_net_revenue"] - df["actual_cogs"]).round(2)

    df["profit_variance"] = (df["actual_profit"] - df["budget_profit"]).round(2)
    return df
