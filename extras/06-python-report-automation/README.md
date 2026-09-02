# Extra 06 — An automated weekly ops report, pull to export

**Tool:** Python — a script that pulls a raw source export, cleans it, and renders a formatted report end to end. No dashboard, no manual spreadsheet work.

[This week's report](report/index.html) · [Cleaned log](data/processed/cleaned_shipping_log.csv)

## The point of this one

Most of the other projects in this portfolio end in a dashboard someone has to go open. This one ends in something that lands in an inbox: a single script that would, in production, run every Monday morning against a live warehouse system, clean whatever mess that system exports, and email out a short report — no analyst re-running a pivot table by hand.

## The data

A simulated **10 weeks of raw warehouse shipping-log exports** (10,093 rows) — deliberately messy in the way a real source-system export usually is, not analysis-ready: status values arrive in inconsistent casing (`Shipped` / `shipped` / `SHIPPED`), dates come from two upstream systems in two different formats, ~2% of rows are exact duplicates from a logging bug, ~1% are missing the warehouse field, and a handful have a nonsensical negative unit count. The final week also has a **seeded, real operational problem**: warehouse West-3's on-time rate collapses that week — the kind of thing a weekly automated check should catch on day one, not at the next quarterly review. See `scripts/lib_ops_log_sim.py`.

## Method

1. **Pull** — read the raw export as-is (`scripts/02_weekly_report.py`, `load_and_clean()`).
2. **Clean** — deduplicate exact repeated rows, drop rows missing a required field (rather than silently guessing a warehouse), coerce and drop invalid unit counts, normalize status casing to a fixed vocabulary, and parse both date formats into one consistent type. Every step is counted, not just applied silently — the report states exactly how many rows were pulled, removed, and why.
3. **Compute** — this week's KPIs (orders, on-time rate, delayed count, open backlog) against the prior week, plus an on-time rate broken out by warehouse. On-time rate is computed over *completed* shipments regardless of their status label — a `Delayed`-labeled order that has in fact shipped counts as a late completion, not an open item, which turned out to matter: a first pass that computed on-time rate only over `Shipped`-labeled rows was wrong by construction, since that label is only ever assigned to orders that shipped on or before their promise date.
4. **Export** — a single self-contained HTML report, auto-flagging any warehouse whose on-time rate drops below 80% this week.

## What this run caught

For the week ending 2026-08-30: 1,018 total orders, 91% on-time (down 5 points from 96% the week before), 157 delayed, 75 still open. Broken out by warehouse, three are steady at 94-96% — and **West-3 is at 76%, down from 98% the week before**. The report's auto-flag catches exactly this: a same-day-visible problem that a monthly or quarterly ops review would only surface weeks after it started.

## Repo structure

```
06-python-report-automation/
├── data/
│   ├── raw/                  raw_shipping_log.csv (the messy "source export")
│   └── processed/            cleaned_shipping_log.csv, weekly_kpi_summary.csv
├── scripts/                  01_generate_data → 02_weekly_report
├── report/index.html         the rendered report for the latest week (open directly in a browser)
└── README.md
```

To reproduce: `cd scripts && python3 01_generate_data.py && python3 02_weekly_report.py`. Re-running `02_weekly_report.py` is safe — cleaning is idempotent (dedup, not increment) and the report always regenerates from the full cleaned log for whatever the latest complete week is.

**Limitations, stated plainly:** the log is simulated, so the exact figures are illustrative — the method (pull raw → clean with every step counted, not hidden → compute over what actually happened, not over a status label that only tells half the story → auto-flag rather than require someone to notice) is the transferable part. A real deployment would need alerting beyond a static HTML file (email/Slack delivery, a threshold history to avoid alert fatigue) and would need to handle a source system whose messiness changes over time, not just the fixed set of issues simulated here.
