# Case 01 — Cutting stockouts without carrying more inventory

**Domain:** Operations & Supply Chain · **Tools:** SQL (SQLite) → Python (pandas/numpy) → Dashboard (static HTML, standing in for Power BI)

[Live dashboard](dashboard/index.html) · [Reorder point recommendations](data/processed/reorder_point_recommendations.csv) · [Before/after summary](data/processed/before_after_summary.csv)

## The business problem

A mid-size distributor sets every SKU's reorder point the same way: a flat **3 weeks of average demand**, regardless of how volatile that SKU's demand actually is or how long and unpredictable its supplier's lead time is. The result is a network fill rate stuck at **85.8%**, well below the 95%+ typically targeted for revenue-critical items — and nobody can say *which* SKUs are driving it or what it's costing the business, only that "we're stocking out too much."

## The data

This is a simulated dataset, not a real company's — genuinely detailed, SKU-level order and inventory history is commercially sensitive and essentially never published openly, so the alternative to simulating it was not doing the project at all. It's built to be realistic rather than convenient: **180 SKUs** across 6 categories, **4 regions**, **2 years of weekly order and inventory history** (~74,400 order lines), Pareto-skewed sales volume (a small share of SKUs drives most of the revenue), demand volatility that scales *with* popularity rather than against it (the trap this case study is built around), category-specific supplier lead times, and real holiday seasonality.

## Data preparation

Order and inventory history is generated directly at weekly grain by an actual periodic-review inventory simulation (`scripts/lib_sim.py`), not scraped or cleaned from a messy export — so there are no missing values or duplicates to handle here. The preparation work was calibration instead: demand volatility, category lead times, and seasonality were tuned until the simulation produced a realistic baseline fill rate for an under-managed distributor (mid-80s%), and stockouts/excess inventory were then left to *emerge* from running the current flat-3-week policy against that demand rather than being scripted in directly — so the finding below is a property of the policy, not an assumption baked into the data. The three raw tables (`skus`, `orders`, `inventory_snapshots`) were then loaded as-is into SQLite for the SQL analysis. If you'd rather see this pipeline run against real data, [Kaggle's DataCo Smart Supply Chain dataset](https://www.kaggle.com/datasets/shashwatwork/dataco-smart-supply-chain-for-big-data-analysis) or [UCI's Online Retail II](https://archive.ics.uci.edu/dataset/502/online+retail+ii) are close analogues with a similar schema.

## Analysis

1. **SQL** (`sql/`) — loaded into SQLite, then: `02_abc_classification.sql` ranks all 180 SKUs by trailing revenue and buckets them into the standard A/B/C tiers using window functions; `03_fill_rate_by_segment.sql` measures fill rate and stockout rate by tier; `04_avg_inventory_by_sku.sql` computes average on-hand value and days-of-inventory per SKU under the current policy.
2. **Python** (`scripts/03_safety_stock_recommendation.py`) — for each SKU, computes weekly demand mean/std from its own order history and combines it with its supplier's lead-time mean/std in the standard safety-stock formula:

   ```
   safety_stock  = Z · √( LT_weeks · σ_demand²  +  mean_demand² · σ_LT_weeks² )
   reorder_point = mean_weekly_demand · LT_weeks + safety_stock
   ```

   A first pass targeting a single 95% service level for every SKU was tried and rejected — it improves fill rate, but by more than **doubling** network inventory investment, because the status-quo policy turns out to be broadly under-protected rather than over-protected. The recommendation instead uses **tier-differentiated service targets** (≈97% for A-tier, ≈92% for B, ≈85% for C) — protect the revenue-critical items tightly, accept more risk on the long tail.
3. **Validation, not just formula** — the recommended reorder points are re-run through the same two-year demand simulation (order quantities held constant, so only the trigger point changes) to get an actual before/after comparison rather than a theoretical one.
4. **Dashboard** (`dashboard/index.html`) — the KPIs and charts a stakeholder would see in Power BI, built as a static, dependency-free HTML file since Power BI Desktop isn't available in this build environment.

## Key findings

1. **The flat reorder policy under-protects exactly the SKUs that matter most.** Network fill rate sits at 85.8%, and even A-tier (revenue-critical) SKUs only reach 88.4% — worse than a distributor can afford given how concentrated its revenue is across those items.
2. **The under-protection is concentrated by category, not universal — and so is the fix.** Electronics Accessories (the longest, most variable supplier lead times) runs reorder points **200–280% below** what its own demand volatility calls for, while Office Supplies (short, reliable domestic lead times) sits **20–37% higher** than necessary under the same flat policy.
3. **A uniform, higher target isn't the answer.** Raising every SKU to a single 95% service level closes the gap but more than **doubles** network inventory investment — the real problem isn't "safety stock is too low everywhere," it's that safety stock is misallocated.
4. **Tier-differentiated targets fix it affordably.** Applying ~97%/92%/85% targets by A/B/C tier and re-running the two-year simulation lifts overall fill rate to **98.9%** (A-tier to **99.1%**) without the cost of the uniform-95%-everywhere approach.
5. **The policy also can't absorb known seasonality.** Fill rate dips hardest every **November**, in both years of simulated history — a predictable spike the flat policy doesn't plan for.

| Metric | Before | After |
|---|---|---|
| Overall fill rate | 85.8% | **98.9%** |
| A-tier fill rate | 88.4% | **99.1%** |
| Avg. network inventory value | $609,041 | $1,440,594 |
| Annual carrying cost (@22%) | $133,989 | $316,931 |

## Recommendations

1. **Reset reorder points per SKU using tier-differentiated safety stock** (~97% A / ~92% B / ~85% C), funded in part by simultaneously trimming the now-identified over-protected Office Supplies SKUs.
2. **Roll out Electronics Accessories first** — it's both the most under-protected category and the one with the longest lead times, so it has the most fill-rate gain per dollar of new inventory.
3. **Build a November-specific review cadence or buffer** rather than trying to solve a known seasonal spike with the same year-round formula.

## Expected impact

The reset requires roughly **$832K more in average inventory investment**, at an incremental carrying cost of about **$183K/year**. Against that, it recovers an estimated **$1.90M/year in gross margin currently lost to stockouts** on revenue-critical items — a projected **net annual benefit of ~$1.72M**, before accounting for intangibles like customer trust and reduced expediting costs.

> **The pitch in one line:** this isn't a cost-cutting story, it's a "the current policy is quietly losing $2M/year in sales it could have made" story — and the fix pays for itself roughly 9x over.

## Limitations / next analysis

- The demand and lead-time distributions are simulated, so the exact dollar figures are illustrative, not a real company's — the method (SQL segmentation → per-SKU safety stock → simulate before deploying → weigh cost against margin recovered, not just "hit 95% everywhere") is the transferable part.
- Regional demand splits are drawn from a fixed per-SKU distribution rather than modeled independently by region — a real rollout would want region-level demand modeling for SKUs whose regional patterns genuinely differ.
- The simulation assumes lead-time draws are independent across SKUs, which real supply chains sometimes violate (e.g., a single supplier delay hitting every SKU sourced from them at once) — a correlated-lead-time stress test would be a reasonable next step before committing capital.
- The recommendation is validated by re-simulating the existing order-quantity policy against new trigger points, not by testing against a live population — a phased rollout (start with Electronics Accessories, measure the actual fill-rate lift) would de-risk the full commitment.
- If real point-of-sale or ERP data becomes available, [Kaggle's DataCo Smart Supply Chain dataset](https://www.kaggle.com/datasets/shashwatwork/dataco-smart-supply-chain-for-big-data-analysis) or [UCI's Online Retail II](https://archive.ics.uci.edu/dataset/502/online+retail+ii) are close-schema real-world analogues this same pipeline could be re-pointed at.

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
