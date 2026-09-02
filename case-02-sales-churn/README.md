# Case 02 — Finding the customers about to churn, and why

**Domain:** Sales & Customer Analytics · **Tools:** SQL (SQLite) → Python (pandas + scikit-learn) → Dashboard (static HTML, standing in for Tableau)

[Live dashboard](dashboard/index.html) · [Driver ranking](data/processed/driver_ranking.csv) · [Retention offer ROI](data/processed/retention_offer_roi.csv)

## The business problem

A subscription business is losing customers steadily — **36.6%** of the observed base has churned — but retention spend is either untargeted (contact everyone, most of whom were never leaving) or based on a hunch ("it's probably the month-to-month customers"). Nobody has actually ranked *which* factors predict churn once you control for the others, or sized what a targeted campaign would be worth.

## The data

Simulated, not a real company's — customer-level churn data at this granularity is commercially sensitive and rarely published with the full field set a real retention team would have. **6,000 customers**, signed up over the trailing ~29 months, simulated **month-by-month** with a churn hazard that depends on contract type, tenure stage (elevated risk in the first 3 months, sharp spikes at annual/biennial renewal dates), engagement, support-ticket load, autopay status, and price — so churn *emerges* from the mechanism rather than being assigned directly. See `scripts/lib_churn_sim.py`. A close real-world analogue with a similar schema is [IBM's Telco Customer Churn dataset on Kaggle](https://www.kaggle.com/datasets/blastchar/telco-customer-churn), which this pipeline could be re-pointed at.

## Method

1. **SQL** (`sql/`) — `02_churn_by_segment.sql` breaks churn rate and monthly recurring revenue (MRR) at risk out by contract type, signup channel, and region; `03_high_risk_segments.sql` cross-tabs contract type against support-ticket load to surface intersectional risk pockets a single-dimension breakdown would hide.
2. **Python — cohort retention curves** (`scripts/03_churn_drivers_and_retention.py`) — for each contract type, the share of the cohort still active at 1/3/6/12/18/24 months, restricted to customers old enough to be observed at that horizon.
3. **Python — driver ranking** — a logistic regression (test AUC **0.71** on a held-out 25% of customers) trained on contract type, plan/add-ons, price, autopay, engagement, support tickets, channel, and region. The point isn't the AUC — it's the **standardized coefficients**, which rank what actually moves churn risk *holding the others constant*.
4. **Python — the targeted offer** — every currently-active customer gets a predicted churn probability; the riskiest 20% become the campaign's target list, sized against an assumed contact cost, an industry-benchmark save rate, and a discount cost per retained customer.

## Findings

Contract type dominates everything else — two-year customers are dramatically stickier than month-to-month, and it's not close (retention curve: 31% of month-to-month customers are still active at 24 months, vs. 74% for one-year and ~93% for two-year). Engagement score is the next real driver. Everything past that — channel, region, monthly charge — is small enough to be noise rather than a story worth acting on.

**The one worth calling out specifically:** support-ticket volume *looks* like a meaningful risk factor in the single-variable SQL breakdown, but once engagement score is in the multivariate model, its effect nearly disappears. Tickets are a symptom of low engagement, not an independent cause — a good example of why a segment-by-segment SQL pass and a multivariate model can disagree, and why the second step matters before recommending anything based on the first.

| Metric | Value |
|---|---|
| Overall churn rate | 36.6% |
| Model test AUC | 0.71 (1,500 held-out customers) |
| Active customers | 3,801 |
| High-risk segment targeted (top 20% by predicted risk) | 761 customers, avg. predicted risk 58% |
| Annual revenue at risk in that segment | $419,358 |

## The recommendation & business impact

Don't contact all 3,801 active customers — target the 761 riskiest, concentrated in month-to-month contracts across every acquisition channel. Assuming a $12/customer outreach cost, a 28% campaign save rate (mid-range for proactive retention benchmarks), and a discount cost equivalent to ~0.6 months of their own charge per customer actually saved:

- Expected revenue protected: **$67,637/year**
- Campaign cost: **$12,514/year**
- **Net annual benefit: ~$55,123/year**, roughly **4.4x** the campaign spend

> **The pitch in one line:** stop trying to save everyone — the model identifies the 20% of active customers actually worth the outreach budget, and the campaign pays for itself more than four times over.

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

**Limitations, stated plainly:** the churn hazard and its drivers are simulated, so exact dollar figures are illustrative, not a real company's — the method (segment in SQL → rank drivers with a held-out test set → target a costed, sized segment rather than "everyone" or "a hunch") is the transferable part. The save rate and discount-cost assumptions are industry-benchmark estimates, not derived from this data, and would need validating against an actual pilot campaign before being taken as fact. The 0.71 AUC is a realistic, not exceptional, score — deliberately not overfit to look impressive.
