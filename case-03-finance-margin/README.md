# Case 03 — Finding where margin is quietly leaking

**Domain:** Finance & Budgeting · **Tools:** Excel (live-formula workbook) → SQL (SQLite) → Python (pandas) → Dashboard (static HTML, standing in for Power BI)

[Live dashboard](dashboard/index.html) · [Excel workbook](excel/case03_margin_analysis.xlsx) · [Ranked variance table](data/processed/variance_ranked.csv)

## The business problem

The business is profitable overall, but budget-to-actual reviews keep coming in over on cost-to-serve in specific regions and categories — and until now, nobody had broken out *where*. Over the trailing 24 months, actual profit came in **$332,657 below budget**. Small relative to $35.5M in budgeted profit (-0.9%), but the finance team's instinct that "something's off in a couple of areas" turns out to be exactly right.

## The data

Simulated, not a real company's — granular budget-vs-actual P&L by region and category is about as commercially sensitive as data gets. **576 rows** (4 regions × 6 categories × 24 months), with two deliberate variance drivers seeded into an otherwise on-plan business: a **ramping supplier cost overrun** in Electronics Accessories (import-heavy — echoing the long, variable lead times from Case 01's same category), and **discount creep** in Outdoor & Sporting in two competitive regions. Everything else moves with ordinary month-to-month noise around budget, so the leak has to be found, not assumed. See `scripts/lib_finance_sim.py` — both variance drivers are stated in the code, so the "finding" below is checkable against how the data was built.

## Method

1. **Excel** (`excel/case03_margin_analysis.xlsx`) — the primary analytical workbook, built with live formulas throughout (6,517 formulas, zero errors on recalculation):
   - **Monthly Detail**: all 576 rows with formula-derived net revenue, COGS, and profit for both budget and actual, plus a three-part **profit-variance bridge** (Volume effect, Discount effect, COGS effect) computed per row. A `Check` column proves the three effects sum exactly to the total variance on every single row — not just in aggregate.
   - **Region × Category Summary**: a flat SUMIFS table pivoted into a heatmap matrix (conditional formatting) that makes the two leak clusters visually obvious.
   - **Margin Bridge**: the network-wide version of the same bridge, with a chart.
   - **Top Variance Drivers**: worst 8 combos ranked with `SMALL()` + `INDEX`/`MATCH` — no manual sorting, so it stays live if the underlying data changes.
2. **SQL** (`sql/`) — `02_variance_ranked.sql` ranks all 24 region×category combos by total variance using window functions, with a running cumulative-share-of-total-leak calculation; `03_monthly_trend_worst_combos.sql` pulls the month-by-month trend for the four worst combos.
3. **Python** (`scripts/03_variance_decomposition_and_recommendation.py`) — reproduces the same volume/discount/COGS decomposition (cross-checked against the Excel bridge to the dollar) and then runs the actual recommendation as a counterfactual: *if the four worst combos had simply held their budgeted discount% and COGS% — same volume, no change in effort — how much profit comes back?*

## Findings

The shortfall is **not a demand problem** — the volume/revenue effect is actually slightly positive (+$38,622). It's almost entirely a discount and cost-discipline story: discount effect -$68,137, COGS effect -$303,142. And it's sharply concentrated: **4 of the 24 region×category combos account for 84% of the entire leak** — Electronics Accessories in the West (-$203K) and Northeast (-$108K), and Outdoor & Sporting in the South (-$59K) and Midwest (-$31K). The Electronics Accessories/West trend shows the COGS overrun **ramping through the year**, not a one-month blip — a cost problem that was still getting worse as of the most recent month in the data.

| Metric | Value |
|---|---|
| Actual profit (24mo) | $35,170,757 |
| Budget profit (24mo) | $35,503,414 |
| Total variance | -$332,657 (-0.9%) |
| Leak concentration | 84% of shortfall in 4 of 24 combos |

## The recommendation & business impact

Don't launch a network-wide cost-cutting initiative — that's solving a problem four combos actually have. Fix the four: renegotiate or re-source the Electronics Accessories supply chain driving the West/Northeast cost overrun, and reinstate discount discipline (approval thresholds, rep-level reporting) in Outdoor & Sporting in the South/Midwest.

- Counterfactual profit if those 4 combos had held budgeted rates: **$35,555,035** (24mo)
- Profit recovered: **$384,278** over 24 months → **~$192,139/year annualized**

> **The pitch in one line:** the business isn't leaking money everywhere — it's leaking from four specific taps, and turning those off recovers roughly $192K a year without touching anything that's actually working.

## Repo structure

```
case-03-finance-margin/
├── data/
│   ├── raw/                       budget_vs_actual.csv
│   └── processed/                 SQL + Python outputs, incl. case03.db
├── excel/case03_margin_analysis.xlsx   live-formula workbook (see Method above)
├── sql/                           schema + analysis queries
├── scripts/                       01_generate_data → 02_load_and_run_sql → 03_variance_decomposition_and_recommendation → 04_build_dashboard → 05_build_excel_workbook
├── dashboard/index.html           static dashboard (open directly in a browser)
└── README.md
```

To reproduce: `cd scripts && python3 01_generate_data.py && python3 02_load_and_run_sql.py && python3 03_variance_decomposition_and_recommendation.py && python3 04_build_dashboard.py && python3 05_build_excel_workbook.py`

**Limitations, stated plainly:** the budget and actuals are simulated, so exact dollar figures are illustrative, not a real company's — the method (decompose variance into named, additive effects → rank and concentrate the fix rather than spreading it thin → cost out the counterfactual) is the transferable part. The counterfactual assumes fixing discount/COGS discipline doesn't change volume, which is a reasonable first-pass assumption but not guaranteed — a real rollout would need to watch for volume effects (e.g. if the "discount creep" was partly defending against a real competitive threat) before declaring the full amount recovered.
