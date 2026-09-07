# BA Case 01 — Cutting AP invoice approval time without cutting corners

**Type:** Process improvement / workflow redesign. **Deliverables:** a process improvement charter, a current vs. future-state process map, and the cycle-time workbook behind both.

[Process map exhibit](exhibits/process-map.html) · [Process Improvement Charter](artifacts/process_improvement_charter.docx) · [Cycle-time workbook](artifacts/cycle_time_analysis.xlsx)

## The business problem

Brightpath Distribution (simulated mid-size distributor) has one approval policy for every invoice of $500 or more: department manager, then finance manager, then controller, in sequence, by email, with no backup approver defined for any of the three roles and no way to see where an invoice actually sits without asking around. Finance leadership's complaint was vague — "invoices take too long, and vendors are starting to push back on our payment terms" — which is exactly the kind of unscoped problem a BA is handed before anyone has actually measured anything.

## The data

A one-month sample of 120 invoices, structured as a time-in-stage log: data-entry timestamp, each of the three approval-stage timestamps, and the eventual payment-processing date — the same shape a real discovery exercise would pull from AP system logs and approver email timestamps.

## Data preparation

The invoice sample is generated directly (`scripts/01_generate_sample.py`) rather than pulled from a real AP system, since Brightpath is a fictional company for this portfolio — so there's no missing-value or duplicate cleanup here. The preparation work was constructing a realistic per-invoice time-in-stage log (entry, each approval stage, payment) matching how a real timestamp-and-email-log discovery exercise would be structured, then aggregating that log into the cycle-time workbook that everything else is built on.

## Analysis

1. **Discovery** — pulled AP system timestamps and approver email logs for one month (120 invoices) to build the time-in-stage log described above.
2. **Root-cause analysis** — 5 Whys, working back from "invoices take ~13 days." Traced to a single structural cause: the three-approval policy was written when invoice volume was roughly a third of today's, and was never revisited as the company grew — so a $600 supply order gets the same three gates as a $60,000 purchase.
3. **Future-state design** — tier approvals by invoice amount instead of applying one policy to everyone; add OCR/auto-capture for the ~75% of volume from recurring vendors; replace untracked email routing with a workflow tool that has reminders and defined backup approvers.
4. **Validation** — modeled the future state row-by-row against the same 120-invoice sample, not just as a blended average, so the projection reflects the same population actually observed (see the workbook's Future-State Projection tab).

## Key findings

1. **The 12.8-day average cycle time is four moderate bottlenecks stacked in sequence, not one big one** — nobody had measured them together before this analysis: 1.3 days of manual re-keying, then roughly 4, 3.6, and 4.2 days respectively sitting in three separate inboxes.
2. **The three-approval chain applies to 82% of invoices today** (everything $500+), even though most of that volume doesn't need three gates; under a tiered redesign, **83% of invoices** (Tier 0 and Tier 1, under $10,000) would clear in a single approval instead of three.
3. **The direct, quantifiable cost is forfeited early-payment discounts.** This one-month sample forfeited $10,401 in discounts it was entitled to (an estimated $124,815/year), because approval alone routinely eats the entire 10-day discount window before payment is even scheduled — only 22% of discount-eligible invoices in the sample captured their discount.
4. **Late-fee risk is real but secondary.** No invoice in this sample actually breached the 30-day net terms, though five ran past 20 days — a smaller tail risk than the discount forfeiture, and one the same fix addresses as a side effect.

## Recommendations

1. **Tier approvals by dollar amount** instead of applying one policy to every invoice.
2. **Deploy OCR/auto-capture for the ~75% of volume from recurring vendors**, where the invoice format is predictable enough to automate safely.
3. **Replace untracked email routing with a workflow tool** that has reminders and defined backup approvers — implemented together with the tiering, not piecemeal, since the routing-tool fix does most of the work and tiering is what lets it apply differently by risk.

## Expected impact

Modeled against the same 120-invoice population: average cycle time drops from 12.8 to 4.3 days (a **66% reduction**), recovering an estimated **$124,815/year** in discounts. Against a $49,600 combined cost for the routing tool, OCR tool, and implementation effort, that's a **net benefit of ~$75,000 in year one and ~$97,000 in every year after** — the fix pays for itself in under five months.

> **The pitch in one line:** the invoice isn't slow because of one bad step — it's slow because four ordinary steps were never looked at together, and fixing all four at once pays back in under half a year.

## Limitations / next analysis

- Brightpath, its people, and every figure here are simulated for this portfolio — the invoice sample is generated, not pulled from a real system.
- The future-state model is a projection built on stated, labeled assumptions (queue-time reduction from the routing tool, OCR adoption rate) rather than a piloted result; the implementation plan explicitly includes a pilot phase to validate those assumptions against real data before full rollout.
- One month (120 invoices) is a single snapshot and doesn't capture seasonal variation in invoice volume or mix — a longer sample spanning a peak period would strengthen the baseline before finalizing the business case for the routing tool.
- The tail risk of late-fee breaches (5 invoices past 20 days, 0 breaches) wasn't stress-tested against a larger sample where a breach might actually occur — worth widening the sample before treating late-fee risk as immaterial.

## Repo structure

```
case-01-process-improvement/
├── data/invoice_sample.csv                       raw simulated time-in-stage log
├── scripts/
│   ├── 01_generate_sample.py                      generates the 120-invoice sample
│   ├── 02_build_workbook.py                        builds the Excel model (openpyxl)
│   └── 03_build_charter.js                         builds the charter (docx-js)
├── artifacts/
│   ├── cycle_time_analysis.xlsx                    Invoice Sample → Bottleneck Analysis → Future-State Model → Summary
│   └── process_improvement_charter.docx            the formal BA deliverable
├── exhibits/process-map.html                       current vs. future-state swimlane diagram
└── README.md
```

To reproduce: `cd scripts && python3 01_generate_sample.py && python3 02_build_workbook.py && node 03_build_charter.js`. Verify the workbook with `recalc.py` from the xlsx skill (2,816 formulas, 0 errors).
