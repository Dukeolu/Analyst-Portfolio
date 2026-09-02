# Extra 05 — Order-to-cash: segment is a red herring, risk tier is the real driver

**Tool:** SQL (SQLite) — complex joins and window functions, no dashboard, no Python analysis beyond the reproducible data generation.

[Schema + view](sql/01_schema.sql) · [Late-payment drivers](data/processed/late_payment_drivers.csv) · [AR aging snapshot](data/processed/ar_aging_snapshot.csv)

## The setup

A finance team pulling a segment-level DSO report would naturally suspect Enterprise accounts (Net 60 terms, the biggest invoices) as the slow payers. This dataset is built so that assumption is wrong: **payment delay is driven by a customer's risk tier, not their segment** — and risk tier happens to be concentrated in SMB, which is exactly the kind of pattern a segment-only cut hides. The point of this project is the SQL surfacing that on its own, the way a real AR analysis would have to.

**150 customers**, **1,887 orders → 1,887 invoices**, **1,998 payments** (15% of invoices are paid in two installments), **$36.6M** invoiced over 2024–2025. See `scripts/lib_o2c_sim.py` — the mechanism (risk-tier-driven delay, risk tier concentrated in SMB) is stated directly in the code.

## The queries

1. **Schema + view** (`01_schema.sql`) — `customers → orders → invoices → payments`, plus an `invoice_payment_status` view (a left join against a per-invoice payment aggregate) that every other query builds on: paid amount, outstanding balance, status, and — once fully paid — days to pay from both invoice date and due date.
2. **DSO by segment, by quarter** (`02_dso_by_segment_trend.sql`) — dollar-weighted DSO per segment per quarter, with a 2-quarter trailing average via a window function to smooth the trend.
3. **AR aging snapshot** (`03_ar_aging_snapshot.sql`) — every invoice still outstanding as of 2025-12-31, bucketed into the standard 0-30/31-60/61-90/90+ aging buckets by segment and risk tier, with each bucket's share of total outstanding AR computed via a window function.
4. **Late-payment drivers** (`04_late_payment_drivers.sql`) — the core comparison: dollar-weighted average days late, ranked with `RANK()`, cut by segment and separately by risk tier, unioned into one result set.
5. **SMB × High-risk concentration** (`05_smb_high_risk_concentration.sql`) — isolates the specific intersection a segment-only or risk-only view each individually hide.
6. **Cumulative collections vs. target** (`06_cumulative_collections_vs_target.sql`) — a running `SUM() OVER` of cash collected by month against a flat monthly target, the kind of tracker that catches a collections slowdown early rather than waiting for month-end.

## Findings

The segment-level view looks almost boring: SMB pays latest, but only by **4.4 days** on average past due, against Mid-Market's 2.3 and Enterprise's 0.3 — not much of a story. The risk-tier view tells a completely different one: **High-risk accounts pay 24.1 days late on average, against Medium's 8.5 and Low's -1.0 (early)**. A segment-level KPI dilutes this roughly 5x, because High-risk accounts are only ~20% of SMB and nearly absent from Mid-Market and Enterprise. Sharper still: **27.4% of High-risk invoices run more than 30 days late, versus 0% for Medium- or Low-risk** — this isn't a shift in the average, it's a genuinely different population of payers.

The AR aging snapshot tells a *third*, unrelated story worth keeping separate: of the **$939,152** outstanding across 39 past-due invoices at the snapshot date, **$871,508 of it sits in the 90+ day bucket** — but that's dollar-dominated by a handful of large, fully-unpaid Enterprise invoices (a dispute/write-off pattern, not a late-payment pattern), simply because Enterprise invoices are large enough that a few stalled ones swamp the aging report in dollar terms. That's the actual lesson: a dollar-weighted aging report and a volume-weighted late-payment-driver report catch two different problems, and you need both.

## Repo structure

```
05-sql-order-to-cash/
├── data/
│   ├── raw/                  customers.csv, orders.csv, invoices.csv, payments.csv
│   └── processed/            query outputs + o2c.db
├── sql/                       schema/view + 5 analysis queries (see above)
├── scripts/                   01_generate_data → 02_load_and_run_sql
└── README.md
```

To reproduce: `cd scripts && python3 01_generate_data.py && python3 02_load_and_run_sql.py`

**Limitations, stated plainly:** the dataset is simulated, so exact figures are illustrative — the method (build the reusable status view first, then cut the same underlying facts two different ways before trusting either one alone) is the transferable part. The "fully unpaid" invoices are seeded as a flat 2% across all segments/risk tiers with no cause modeled (real write-offs usually have a reason — bankruptcy, dispute, fraud — that this dataset doesn't attempt to simulate).
