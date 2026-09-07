# Case 04 — Where the hiring funnel — and headcount — leaks

**Domain:** HR & People Operations · **Tools:** SQL (SQLite) → Python (pandas, scikit-learn) → Excel (live-formula workbook) → Dashboard (static HTML, standing in for Power BI)

[Live dashboard](dashboard/index.html) · [Excel workbook](excel/case04_hr_analysis.xlsx) · [Department risk ranking](data/processed/department_risk_ranking.csv)

## The business problem

Voluntary attrition has been running high enough that HR leadership wants to know two things: which departments are actually the problem, and — since recruiting and retention are usually treated as separate teams with separate budgets — whether the *source* of a hire has anything to do with how long they stay. Over the trailing period, **23.6% of the 1,230-employee cohort** left voluntarily. That's the headline number everyone already has. The question this case answers is what's underneath it.

## The data

Simulated, not a real company's — individual employee records are about as sensitive as HR data gets, and this dataset deliberately excludes demographic attributes (age, gender, etc.) entirely, using only structural and business factors (department, hiring channel, level, compensation ratio, manager span, overtime, engagement score). **720 funnel rows** (6,525 applications → 1,230 hires) and **1,230 employee records** with month-by-month simulated tenure and voluntary-termination outcomes.

## Data preparation

Employee and funnel records are generated directly (`scripts/lib_hr_sim.py`) with two deliberate mechanisms seeded in — **channel-driven early attrition** (Job Board hires are cheap to source but leave early at a materially higher rate than Employee Referral hires) and a **recruiting-funnel screening bottleneck** specific to Warehouse & Ops' Job Board pipeline — with demographic attributes excluded by design rather than by data-cleaning necessity. Because it's generated rather than scraped, there's no missing-value or duplicate cleanup; the preparation work was building the funnel and headcount roll-forward with formula-driven, auditable outputs (the Excel workbook's 645 formulas, zero errors on recalculation) before running any driver analysis, and deliberately **excluding tenure from the driver model** since a terminated employee's tenure *is* how long until they left — including it would make the model tautological rather than predictive.

## Analysis

1. **SQL** (`sql/`) — `02_attrition_by_tenure_band.sql` cuts termination rate by tenure band and channel to show attrition isn't uniform over time; `03_department_risk_ranking.sql` ranks departments by termination rate using `RANK()`, alongside the average overtime and manager-span load that might explain the ranking.
2. **Python** (`scripts/04_driver_ranking_and_recommendation.py`) — a logistic regression ranks what structurally predicts voluntary attrition (tenure excluded, see Data preparation). The script also reproduces, independently in Python, the two dollar scenarios the Excel workbook builds: the cost of Job Board's early attrition versus Employee Referral's, and the wasted recruiter effort behind Warehouse & Ops' screening bottleneck.
3. **Excel** (`excel/case04_hr_analysis.xlsx`) — 645 live formulas, zero errors on recalculation:
   - **Headcount & Attrition**: a 144-row monthly roll-forward (6 departments × 24 months) with formula-driven beginning/ending headcount and an annualized attrition rate per department per month.
   - **Recruiting Funnel**: the full 720-row funnel with a channel-level SUMIFS conversion-rate summary (conditional-formatting heatmap) and a spotlight comparison isolating Warehouse & Ops' Job Board conversion against the Job Board network average.
   - **Cost of the Leak**: early-attrition cost by channel and the sourcing-mix scenario calculation, with a chart.
4. **Dashboard** (`scripts/05_build_dashboard.py`) — the funnel-stage comparison, early-attrition-by-channel ranking, driver ranking, and department risk table, all cross-checked against the same processed CSVs the Excel workbook and Python script write.

## Key findings

1. **The department-level ranking is a mixed signal.** Marketing (28.2%) and Warehouse & Ops (28.1%) both run highest, but only one has a structural explanation in this data: Warehouse & Ops carries the highest overtime load (14.0 hrs/mo vs. 5–6 across the rest of the business) and the widest average manager span (8.7). Marketing's elevated rate doesn't line up with any measured factor and would need more digging before acting on it.
2. **The channel finding is sharper and fully actionable.** Job Board hires leave within their first 90 days at **21.3%**, versus **6.8%** for Employee Referral — more than 3x.
3. **Warehouse & Ops has a second, independent problem.** Job Board is its dominant sourcing channel, and its pipeline there shows screening throughput matching the network average (~38%) but conversion from screened to interviewed collapsing to **30.1%**, versus **47.7%** network-wide — a pure bottleneck, not a candidate-quality issue, since the applicant pool composition is the same channel.
4. **The driver model corroborates both findings independently.** Job Board hires carry a higher standardized coefficient toward attrition (+0.15) than Employee Referral (-0.19), and Warehouse & Ops itself carries a mild positive coefficient (+0.14) even after controlling for channel, compensation, overtime, and manager span.
5. **The model is honest by design, not by accident.** Test AUC of 0.586 is modest once the dominant but circular tenure signal is removed — and manager span, despite being built into the simulation as a mild risk factor, doesn't come through reliably at this sample size and is reported as noise, not a finding.

| Metric | Value |
|---|---|
| Overall voluntary attrition | 23.6% (1,230 hires observed) |
| Job Board early (≤3mo) attrition | 21.3% vs. 6.8% for Employee Referral |
| Warehouse & Ops × Job Board interview rate | 30.1% vs. 47.7% network-wide |
| Driver model | test AUC 0.586 (tenure excluded — see Data preparation) |

## Recommendations

1. **Shift sourcing mix away from Job Board** toward Employee Referral where volume allows — the early-attrition gap is large and consistent across the model and the raw cohort curves.
2. **Clear the Warehouse & Ops screening backlog** specifically — this is a process/staffing fix for that one pipeline, not a company-wide hiring-mix change.
3. **Investigate Marketing's elevated attrition separately.** Since it doesn't correlate with any measured structural factor, it likely needs a qualitative follow-up (exit interviews, manager check-ins) rather than another cut of this dataset.

## Expected impact

At Employee Referral's early-attrition rate, Job Board's 310 hires over 24 months would have produced **~45 fewer early departures**, avoiding roughly $9,000 in replacement cost each — a **net annual savings of $201,886** from the sourcing-mix shift alone. Separately, clearing the Warehouse & Ops screening backlog should recover roughly **34 missed interviews a year** of otherwise-viable candidates who never got a shot — a compounding pipeline benefit not separately dollarized here.

> **The pitch in one line:** the attrition problem isn't spread evenly across the business — it's concentrated in one hiring channel and one department's broken pipeline, and fixing those two things (not a company-wide retention program) recovers roughly $200K a year.

## Limitations / next analysis

- The workforce and funnel are simulated, so exact figures are illustrative, not a real company's — the method (separate the recruiting problem from the retention problem, rank drivers while excluding tautological features, cost out a channel-mix counterfactual) is the transferable part.
- Demographic attributes are excluded by design, which means the model can't rule out that unmeasured factors correlated with channel or department explain some of the effect attributed to them here — a real rollout would want a controlled pilot (shift mix for a subset of requisitions, measure the actual early-attrition delta) before locking in the full projected savings.
- Marketing's elevated attrition rate has no structural explanation in this dataset — the next step is qualitative (exit interviews) rather than a further quantitative cut of the same data.
- The driver model's AUC (0.586) reflects a small, honest signal once tenure is excluded — a larger sample or richer feature set (manager tenure, compensation history, team size) might sharpen it, at the cost of needing more sensitive HR data than this design intentionally avoids.

## Repo structure

```
case-04-hr-attrition/
├── data/
│   ├── raw/                       recruiting_funnel.csv, employees.csv
│   └── processed/                 SQL + Python outputs, incl. case04.db
├── excel/case04_hr_analysis.xlsx  live-formula workbook (see Analysis above)
├── sql/                           schema + analysis queries
├── scripts/                       01_generate_data → 02_prepare_headcount → 03_load_and_run_sql → 04_driver_ranking_and_recommendation → 05_build_dashboard → 06_build_excel_workbook
├── dashboard/index.html           static dashboard (open directly in a browser)
└── README.md
```

To reproduce: `cd scripts && python3 01_generate_data.py && python3 02_prepare_headcount.py && python3 03_load_and_run_sql.py && python3 04_driver_ranking_and_recommendation.py && python3 05_build_dashboard.py && python3 06_build_excel_workbook.py`
