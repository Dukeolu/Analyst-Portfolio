# BA Case 01 — Cutting AP invoice approval time without cutting corners

**Type:** Process improvement / workflow redesign. **Deliverables:** a process improvement charter, a current vs. future-state process map, and the cycle-time workbook behind both.

[Process map exhibit](exhibits/process-map.html) · [Process Improvement Charter](artifacts/process_improvement_charter.docx) · [Cycle-time workbook](artifacts/cycle_time_analysis.xlsx)

## The problem

Brightpath Distribution (simulated mid-size distributor) has one approval policy for every invoice of $500 or more: department manager, then finance manager, then controller, in sequence, by email, with no backup approver defined for any of the three roles and no way to see where an invoice actually sits without asking around. Finance leadership's complaint was vague — "invoices take too long, and vendors are starting to push back on our payment terms" — which is exactly the kind of unscoped problem a BA is handed before anyone has actually measured anything.

## Method

1. **Discovery** — pulled AP system timestamps and approver email logs for one month (120 invoices) to build a time-in-stage log: data entry, each approval stage, payment processing.
2. **Root-cause analysis** — 5 Whys, working back from "invoices take ~13 days." Traced to a single structural cause: the three-approval policy was written when invoice volume was roughly a third of today's, and was never revisited as the company grew — so a $600 supply order gets the same three gates as a $60,000 purchase.
3. **Future-state design** — tier approvals by invoice amount instead of applying one policy to everyone; add OCR/auto-capture for the ~75% of volume from recurring vendors; replace untracked email routing with a workflow tool that has reminders and defined backup approvers.
4. **Validation** — modeled the future state row-by-row against the same 120-invoice sample, not just as a blended average, so the projection reflects the same population actually observed (see the workbook's Future-State Projection tab).

## Key finding

The current 12.8-day average cycle time isn't one big bottleneck — it's four moderate ones stacked in sequence, none of which anyone had measured together before this analysis: 1.3 days of manual re-keying, then roughly 4, 3.6, and 4.2 days respectively sitting in three separate inboxes. The three-approval chain applies to 82% of invoices today (everything $500+); under the tiered redesign, 83% of invoices (Tier 0 and Tier 1, under $10,000) clear in a single approval instead of three, and the two- and three-gate chains are reserved for the invoices actually large enough to justify them.

The direct cost: this one-month sample forfeited $10,401 in early-payment discounts it was entitled to (an estimated $124,815/year), because approval alone routinely eats the entire 10-day discount window before payment is even scheduled. Only 22% of discount-eligible invoices in the sample captured their discount.

## Recommendation & business impact

Tier approvals by dollar amount, deploy OCR for recurring vendors, and replace email routing with a workflow tool that has visibility and backup approvers — implemented together, not piecemeal, since the routing-tool fix does most of the work and the tiering is what lets it apply differently by risk. Modeled against the same invoice population: average cycle time drops from 12.8 to 4.3 days (a 66% reduction), recovering an estimated $124,815/year in discounts. Against a $49,600 combined cost for the routing tool, OCR tool, and implementation effort, that's a **net benefit of ~$75,000 in year one and ~$97,000 in every year after** — the fix pays for itself in under five months.

No invoice in this particular month's sample actually breached the 30-day net terms and triggered a late fee, though five ran past 20 days — a real but smaller tail risk than the discount forfeiture, and one the same fix addresses as a side effect.

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

**Limitations, stated plainly:** Brightpath, its people, and every figure here are simulated for this portfolio — the invoice sample is generated, not pulled from a real system. The future-state model is a projection built on stated, labeled assumptions (queue-time reduction from the routing tool, OCR adoption rate) rather than a piloted result; the implementation plan explicitly includes a pilot phase to validate those assumptions against real data before full rollout, which is the honest way to treat a projection like this one.
