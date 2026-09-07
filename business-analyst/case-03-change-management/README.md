# BA Case 03 — Integrating two warehouse teams without it reading as a takeover

**Type:** Change management / stakeholder alignment. **Deliverables:** a stakeholder analysis (power/interest grid + RACI matrix) and a full change management plan.

[Stakeholder map exhibit](exhibits/stakeholder-map.html) · [Change Management Plan](artifacts/change_management_plan.docx) · [Stakeholder analysis workbook](artifacts/stakeholder_analysis.xlsx)

## The business problem

Brightpath Distribution acquired Colton Regional Supply, a smaller regional distributor with two warehouse sites and about 85 employees. The two companies' warehouse operations need to integrate onto one WMS, one shift/scheduling policy, and one reporting structure within four months — without disrupting order fulfillment for either customer base. The technical side of this (a systems migration, a new org chart) is the easy part. The hard part, and the reason this is a change-management problem rather than a project-management one, is that every Colton employee's live worry is whether this is a partnership or a takeover, and the answer depends entirely on how the integration is run, not on what gets decided.

## The data

12 stakeholders (or stakeholder groups) across both companies, mapped by power and interest via simulated stakeholder interviews, plus six areas of change (systems, reporting lines, scheduling, safety procedures, payroll, brand/identity) each rated for impact severity and current staff readiness.

## Data preparation

Stakeholder interview findings and change-impact ratings are simulated for this portfolio rather than pulled from a real acquisition — both Brightpath and Colton are fictional companies. The preparation work was structuring interview findings into power/interest scores and impact-severity/readiness ratings per change area, and building the RACI matrix with a programmatic check that every one of the nine key activities has exactly one Accountable owner — a real risk in any RACI exercise built by hand, and one worth catching before the matrix goes into the change plan.

## Analysis

1. **Stakeholder analysis** — mapped 12 stakeholders (or stakeholder groups) by power to influence the integration and interest in its outcome, to decide who gets managed closely versus simply kept informed, rather than treating "communicate with everyone the same way" as a plan.
2. **RACI matrix** — assigned Responsible/Accountable/Consulted/Informed across the nine key integration activities, deliberately mirroring Colton and Brightpath roles at each level (e.g., both companies' warehouse ops managers hold the same Responsible role for shift-policy design) — checked programmatically to confirm every activity has exactly one accountable owner, not zero or several.
3. **Change impact assessment** — six areas of change, each rated for impact severity and current staff readiness, since "high impact + low readiness" areas are where a change plan actually needs to concentrate effort.
4. **Communication, training, and resistance planning** — a phased communication plan, an audience-specific training plan, and a resistance risk register built from what stakeholder interviews actually surfaced as fears, not a generic template.

## Key findings

1. **One resistance risk dominates, and it's specific.** Multiple Colton employees named the same fear directly: being folded into "how Brightpath already does things" with no real input.
2. **That reframed the RACI ownership itself.** The matrix mirrors Colton and Brightpath roles at every activity where both are plausible owners — both sites' ops managers are jointly Responsible for scheduling-policy design, for instance, rather than Brightpath designing and Colton reviewing.
3. **The communication plan opens with listening, not announcing.** A dedicated listening phase runs before any design work starts, specifically so design sessions can start from "what already works at each site" instead of a Brightpath template with Colton's name added.
4. **Communication effort is allocated by need, not by power.** The highest-power, highest-interest group (Manage Closely: the COO, both companies' operational leads, and HR) is where two-way ownership gets enforced, but the two warehouse-staff groups — the highest-anxiety group per the readiness ratings — get the most frequent, most concrete communication, which is the opposite of how communication effort often gets allocated by default.

## Recommendations

1. **Run the integration in six phases over roughly sixteen weeks**: announcement, discovery/listening, co-designed process changes, pre-go-live training, go-live with on-floor support, and a two-week reinforcement period.
2. **Track adoption explicitly** — WMS daily-use rate, unresolved question backlog, fulfillment accuracy during cutover — rather than assuming a completed system migration equals a completed integration.
3. **Run named-individual retention conversations with at-risk Colton staff before the announcement goes wide** — the resistance risk register's highest-likelihood, highest-impact risk, addressed with a concrete mitigation rather than a generic "communicate change well" plan.

## Expected impact

12 stakeholders mapped and RACI-validated, with every one of the nine key activities carrying exactly one Accountable owner. The resistance risk register names Colton-staff attrition before cutover as the top risk, paired with a concrete, targeted mitigation — the appropriate measure of "impact" for a change-management engagement, where success shows up in adoption and retention rather than a single dollar figure.

## Limitations / next analysis

- Brightpath, Colton, and every stakeholder here are simulated for this portfolio.
- Power and interest ratings are a single analyst's judgment call rather than a scored group exercise — a real engagement would normally run this as a workshop with the actual sponsors in the room, since the ratings materially change who gets prioritized.
- No dollar figure is attached to the change-management outcome itself, unlike the other three BA cases — a real engagement could still quantify avoided-attrition cost (replacement cost per departure, the same approach used in DA Case 04) once real headcount and attrition-risk figures exist.
- The RACI and change-impact ratings are a point-in-time assessment; a real 16-week integration would want to re-survey stakeholder sentiment partway through to catch a shift the initial mapping didn't anticipate.

## Repo structure

```
case-03-change-management/
├── scripts/
│   ├── 01_build_stakeholder_workbook.py            builds the stakeholder workbook (openpyxl)
│   └── 02_build_change_plan.js                      builds the change management plan (docx-js)
├── artifacts/
│   ├── stakeholder_analysis.xlsx                     Power-Interest Grid + RACI Matrix, formula-validated
│   └── change_management_plan.docx                   the formal BA deliverable
├── exhibits/stakeholder-map.html                      power/interest quadrant visualization
└── README.md
```

To reproduce: `cd scripts && python3 01_build_stakeholder_workbook.py && node 02_build_change_plan.js`. Verify the workbook with `recalc.py` from the xlsx skill (26 formulas, 0 errors) — including a formula check that every RACI activity has exactly one Accountable owner.
