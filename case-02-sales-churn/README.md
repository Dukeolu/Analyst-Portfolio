# Case 02 — Finding the customers about to churn, and why

**Domain:** Sales & Customer Analytics · **Tools:** SQL (SQLite) → Python (pandas + scikit-learn) → Dashboard (static HTML, standing in for Tableau)

[Live dashboard](dashboard/index.html) · [Driver ranking](data/processed/driver_ranking.csv) · [Retention offer ROI](data/processed/retention_offer_roi.csv)

## The business problem

A subscription business is losing customers steadily — **36.6%** of the observed base has churned — but retention spend is either untargeted (contact everyone, most of whom were never leaving) or based on a hunch ("it's probably the month-to-month customers"). Nobody has actually ranked *which* factors predict churn once you control for the others, or sized what a targeted campaign would be worth.

## The data

Simulated, not a real company's — customer-level churn data at this granularity is commercially sensitive and rarely published with the full field set a real retention team would have. **6,000 customers**, signed up over the trailing ~29 months, simulated **month-by-month** with a churn hazard that depends on contract type, tenure stage (elevated risk in the first 3 months, sharp spikes at annual/biennial renewal dates), engagement, support-ticket load, autopay status, and price. A close real-world analogue with a similar schema is [IBM's Telco Customer Churn dataset on Kaggle](https://www.kaggle.com/datasets/blastchar/telco-customer-churn), which this pipeline could be re-pointed at.

## Data preparation

Customer-month histories are generated directly by a hazard-based churn simulation (`scripts/lib_churn_sim.py`) rather than cleaned from a raw export, so this is calibration work, not scrubbing: churn hazard multipliers for contract type, tenure stage, engagement, ticket load, autopay, and price were tuned until the resulting retention curves matched the shape reported in real subscription-business benchmarks (steep early-tenure risk, sharp spikes at renewal dates) — so churn *emerges* from the mechanism rather than being assigned directly. The resulting customer-month panel has no missing values or duplicates by construction and was loaded as-is into SQLite for the SQL analysis.

## Analysis

1. **SQL** (`sql/`) — `02_churn_by_segment.sql` breaks churn rate and monthly recurring revenue (MRR) at risk out by contract type, signup channel, and region; `03_high_risk_segments.sql` cross-tabs contract type against support-ticket load to surface intersectional risk pockets a single-dimension breakdown would hide.
2. **Python — cohort retention curves** (`scripts/03_churn_drivers_and_retention.py`) — for each contract type, the share of the cohort still active at 1/3/6/12/18/24 months, restricted to customers old enough to be observed at that horizon.
3. **Python — driver ranking** — a logistic regression (test AUC **0.71** on a held-out 25% of customers) trained on contract type, plan/add-ons, price, autopay, engagement, support tickets, channel, and region. The point isn't the AUC — it's the **standardized coefficients**, which rank what actually moves churn risk *holding the others constant*.
4. **Python — the targeted offer** — every currently-active customer gets a predicted churn probability; the riskiest 20% become the campaign's target list, sized against an assumed contact cost, an industry-benchmark save rate, and a discount cost per retained customer.

## Key findings

1. **Contract type dominates everything else.** Two-year customers are dramatically stickier than month-to-month, and it's not close: 31% of month-to-month customers are still active at 24 months, vs. 74% for one-year and ~93% for two-year.
2. **Engagement score is the next real driver.** Past contract type and engagement, everything else — channel, region, monthly charge — is small enough to be noise rather than a story worth acting on.
3. **Support-ticket volume is a false lead worth naming.** It looks like a meaningful risk factor in the single-variable SQL breakdown, but once engagement score enters the multivariate model, its effect nearly disappears — tickets are a symptom of low engagement, not an independent cause. A segment-by-segment SQL pass alone would have pointed at the wrong lever.
4. **The model is honest, not impressive-looking.** Test AUC of 0.71 is a realistic score for this kind of churn model, deliberately not overfit to look better than it is.
5. **The targetable segment is small and specific.** The riskiest 20% of active customers (761 people, avg. predicted risk 58%) account for $419,358 in annual revenue at risk — a concrete, costed target list rather than "everyone."

| Metric | Value |
|---|---|
| Overall churn rate | 36.6% |
| Model test AUC | 0.71 (1,500 held-out customers) |
| Active customers | 3,801 |
| High-risk segment targeted (top 20% by predicted risk) | 761 customers, avg. predicted risk 58% |
| Annual revenue at risk in that segment | $419,358 |

## Recommendations

1. **Target the 761 highest-risk active customers**, not all 3,801 — they're concentrated in month-to-month contracts across every acquisition channel.
2. **Don't build a retention lever around ticket volume.** Address the underlying engagement driver instead; ticket volume is downstream of it, not an independent cause.
3. **Re-run the risk model on a regular cadence** (e.g., quarterly) as contract mix shifts — since contract type is the dominant driver, marketing and sales campaigns that change the mix will move the churn baseline even if nothing else changes.

## Expected impact

Assuming a $12/customer outreach cost, a 28% campaign save rate (mid-range for proactive retention benchmarks), and a discount cost equivalent to ~0.6 months of a customer's own charge per customer actually saved:

- Expected revenue protected: **$67,637/year**
- Campaign cost: **$12,514/year**
- **Net annual benefit: ~$55,123/year**, roughly **4.4x** the campaign spend

> **The pitch in one line:** stop trying to save everyone — the model identifies the 20% of active customers actually worth the outreach budget, and the campaign pays for itself more than four times over.

## Limitations / next analysis

- The churn hazard and its drivers are simulated, so exact dollar figures are illustrative, not a real company's — the method (segment in SQL → rank drivers with a held-out test set → target a costed, sized segment rather than "everyone" or "a hunch") is the transferable part.
- The 28% save rate and discount-cost assumptions are industry-benchmark estimates, not derived from this data, and would need validating against an actual pilot campaign before being taken as fact.
- The 0.71 AUC is realistic but modest — a richer feature set (usage frequency, NPS or survey data, competitor pricing) could likely sharpen it, at the cost of needing more sensitive data sources than this simulation includes.
- The risk model is a snapshot; contract mix and price sensitivity shift over time, so the target list should be refreshed on a regular cadence rather than generated once and reused indefinitely.
- If a real dataset becomes available, [IBM's Telco Customer Churn dataset on Kaggle](https://www.kaggle.com/datasets/blastchar/telco-customer-churn) is a close-schema analogue this pipeline could be re-pointed at.

## Repo structure

```
case-02-sales-churn/
├── data/
│   ├── raw/                  customers.csv
│   └── processed/            SQL + Python outputs, incl. case02.db
├── sql/                      schema + analysis queries
├── scripts/                  01_generate_data → 02_load_and_run_sql → 03_churn_drivers_and_retention → 04_build_dashboard
├── dashboard/index.html      static dashboard (open directly in a browser)
└── README.md
```

To reproduce: `cd scripts && python3 01_generate_data.py && python3 02_load_and_run_sql.py && python3 03_churn_drivers_and_retention.py && python3 04_build_dashboard.py`
