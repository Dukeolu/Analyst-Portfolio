# Extra 07 — An interactive budget workbook with a live scenario toggle

**Tool:** Excel — a 24-month scenario budget model. No SQL, no Python, no dashboard: the point of this one is what Excel itself can do.

[The workbook](excel/budget_scenario_model.xlsx)

## What it does

A 24-month (2026–2027) budget model for a small growing business, with a scenario toggle: pick **Conservative / Base / Aggressive** from a dropdown on the Assumptions tab, and every number on the Budget Model tab — revenue, headcount, opex, EBITDA — recalculates instantly, no copy-pasting between versions of the file. A third tab, Scenario Comparison, shows all three scenarios side by side at once (independent of the toggle), so you don't have to flip through one at a time to see the spread between them.

## How it's built

- **The toggle:** a data-validation dropdown (`Conservative` / `Base` / `Aggressive`) on the Assumptions tab. A small "Scenario Definitions" table holds each scenario's monthly growth rate, gross margin, headcount additions per quarter, and cost per head — and an "Active Scenario Drivers" block pulls whichever row matches the dropdown via `INDEX`/`MATCH`. The Budget Model tab only ever references the *active* drivers, never the scenario table directly, so it doesn't need to know which scenario is selected.
- **The 24-month grid:** headcount steps up at the start of each quarter (`ROUNDUP` on the month number), revenue compounds month over month from a starting base, COGS and opex derive from the active margin and headcount assumptions, and EBITDA and EBITDA margin fall out of those — every formula generated from one consistent template across all 24 months, not hand-typed per column.
- **The comparison tab:** rather than triplicate the full 24-month grid three times, each scenario's quarterly revenue and EBITDA are computed with a closed-form compound-growth formula (`starting revenue × (1 + growth)^periods`) that references that scenario's row in the Assumptions table *directly* — bypassing the toggle entirely, so all three stay visible at once. A line chart plots quarterly revenue for all three scenarios together.
- Verified with `recalc.py` (LibreOffice): **236 formulas, zero errors**, and cross-checked by hand — the Scenario Comparison tab's Base-scenario Q8 (month-24) revenue matches the Budget Model tab's month-24 revenue exactly, confirming the two independently-built views agree.

## The scenarios, for reference

| | Monthly growth | Gross margin | Headcount adds/qtr | Year-2 EBITDA margin |
|---|---|---|---|---|
| Conservative | 1.0% | 62% | 0 | 19.0% |
| Base | 2.5% | 65% | +1 | 25.0% |
| Aggressive | 4.5% | 68% | +3 | 30.3% |

Margin *improves* with the more aggressive growth case here — faster revenue growth outpaces the added headcount cost, given the gross-margin assumptions attached to each scenario. That's a modeling choice worth being honest about: it's not a law of nature that growth improves margin, it's a consequence of the specific assumptions typed into this table, and a real version of this model should stress-test that relationship rather than assume it.

## Repo structure

```
07-excel-budget-workbook/
├── scripts/01_build_workbook.py    generates the workbook (openpyxl)
├── excel/budget_scenario_model.xlsx
└── README.md
```

To reproduce: `cd scripts && python3 01_build_workbook.py` (writes `../excel/budget_scenario_model.xlsx`). Verify with `recalc.py` from the xlsx skill if you have LibreOffice installed.

**Limitations, stated plainly:** the assumptions (starting revenue, margins, headcount cost) are illustrative placeholder numbers set to produce a plausible, positive-EBITDA business — not derived from any real company. The headcount-cost and opex structure is deliberately simple (one blended "cost per head" and one fixed opex line) rather than modeling department-level hiring plans or opex categories, which is what a production version of this model would need next.
