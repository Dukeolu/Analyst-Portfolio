# Case 01 — Cutting stockouts without carrying more inventory

**Domain:** Operations & Supply Chain · **Tools:** SQL (SQLite) → Python (pandas/numpy) → Dashboard (static HTML, standing in for Power BI)

[Live dashboard](dashboard/index.html) · [Reorder point recommendations](data/processed/reorder_point_recommendations.csv) · [Before/after summary](data/processed/before_after_summary.csv)

## The business problem

A mid-size distributor sets every SKU's reorder point the same way: a flat **3 weeks of average demand**, regardless of how volatile that SKU's demand actually is or how long and unpredictable its supplier's lead time is. The result is a network fill rate stuck at **85.8%**, well below the 95%+ typically targeted for revenue-critical items — and nobody can say *which* SKUs are driving it or what it's costing the business, only that "we're stocking out too much."

## The data

This is a simulated dataset, not a real company's — genuinely detailed, SKU-level order and inventory history is commercially sensitive and essentially never published openly, so the alternative to simulating it was not doing the project at all. It's built to be realistic rather than convenient: **180 SKUs** across 6 categories, **4 regions**, **2 years of weekly order and inventory history** (~74,400 order lines), Pareto-skewed sales volume (a small share of SKUs drives most of the revenue), demand volatility that scales *with* popularity rather than against it (the trap this case study is built around), category-specific supplier lead times, and real holiday seasonality. Stockouts and excess inventory are not scripted in — they emerge from running an actual periodic-review inventory simulation against that demand. See `scripts/lib_sim.py` for exactly how, and the note in `scripts/01_generate_data.py`. If you'd rather see this pipeline run against real data, [Kaggle's DataCo Smart Supply Chain dataset](https://www.kaggle.com/datasets/shashwatwork/dataco-smart-supply-chain-for-big-data-analysis) or [UCI's Online Retail II](https://archive.ics.uci.edu/dataset/502/online+retail+ii) are close analogues with a similar schema.

## Method

1. **SQL** (`sql/`) — loaded into SQLite, then: `02_abc_classification.sql` ranks all 180 SKUs by trailing revenue and buckets them into the standard A/B/C tiers using window functions; `03_fill_rate_by_segment.sql` measures fill rate and stockout rate by tier; `04_avg_inventory_by_sku.sql` computes average on-hand value and days-of-inventory per SKU under the current policy.
2. **Python** (`scripts/03_safety_stock_recommendation.py`) — for each SKU, computes weekly demand mean/std from its own order history and combines it with its supplier's lead-time mean/std in the standard safety-stock formula:

   ```
   safety_stock  = Z · √( LT_weeks · σ_demand²  +  mean_demand² · σ_LT_weeks² )
   reorder_point = mean_weekly_demand · LT_weeks + safety_stock
   ```

   A first pass targeting a single 95% service level for every SKU was tried and rejected — it improves fill rate, but by more than **doubling** network inventory investment, because the status-quo policy turns out to be broadly under-protected rather than over-protected. The recommendation instead uses **tier-differentiated service targets** (≈97% for A-tier, ≈92% for B, ≈85% for C) — protect the revenue-critical items tightly, accept more risk on the long tail. That's the standard real-world answer once "just raise safety stock everywhere" turns out to be unaffordable.
3. **Validation, not just formula** — the recommended reorder points are re-run through the same two-year demand simulation (order quantities held constant, so only the trigger point changes) to get an actual before/after comparison rather than a theoretical one.
4. **Dashboard** (`dashboard/index.html`) — the KPIs and charts a stakeholder would see in Power BI, built as a static, dependency-free HTML file since Power BI Desktop isn't available in this build environment.

## Findings

| Metric | Before | After |
|---|---|---|
| Overall fill rate | 85.8% | **98.9%** |
| A-tier fill rate | 88.4% | **99.1%** |
| Avg. network inventory value | $609,041 | $1,440,594 |
| Annual carrying cost (@22%) | $133,989 | $316,931 |

The SKUs most under-protected today cluster heavily in **Electronics Accessories** — the category with the longest, most variable supplier lead times, where the flat 3-week policy leaves reorder points 200–280% below what their own demand volatility calls for. The SKUs most over-protected are concentrated in **Office Supplies** — short, reliable domestic lead times mean the same flat policy sits 20–37% higher than necessary. Fill rate also dips hardest every **November**, in both years, when the policy can't absorb the holiday demand spike (see the monthly trend chart).

## The recommendation & business impact

Reset reorder points per SKU using tier-differentiated safety stock, funded by simultaneously trimming the over-protected Office Supplies SKUs. Yes, this requires roughly **$832K more in average inventory investment**, at an incremental carrying cost of about **$183K/year**. But it also recovers an estimated **$1.90M/year in gross margin currently lost to stockouts** on revenue-critical items — a projected **net annual benefit of ~$1.72M**, before accounting for intangibles like customer trust and reduced expediting costs.

> **The pitch in one line:** this isn't a cost-cutting story, it's a "the current policy is quietly losing $2M/year in sales it could have made" story — and the fix pays for itself roughly 9x over.

## Repo structure

```
case-01-operations-supply-chain/
├── data/
│   ├── raw/                  skus.csv, orders.csv, inventory_snapshots.csv
│   └── processed/            SQL + Python outputs, incl. case01.db
├── sql/                      schema + analysis queries
├── scripts/                  01_generate_data → 02_load_and_run_sql → 03_safety_stock_recommendation → 04_build_dashboard
├── dashboard/index.html      static dashboard (open directly in a browser)
└── README.md
```

To reproduce: `cd scripts && python3 01_generate_data.py && python3 02_load_and_run_sql.py && python3 03_safety_stock_recommendation.py && python3 04_build_dashboard.py`

**Limitations, stated plainly:** the demand and lead-time distributions are simulated, so the exact dollar figures are illustrative, not a real company's numbers — the method (SQL segmentation → per-SKU safety stock → simulate before deploying → weigh cost against margin recovered, not just "hit 95% everywhere") is the transferable part. Regional demand splits are drawn from a fixed per-SKU distribution rather than modeled independently, and the simulation assumes lead-time draws are independent across SKUs, which real supply chains sometimes violate (e.g., a single supplier delay hitting many SKUs at once).
