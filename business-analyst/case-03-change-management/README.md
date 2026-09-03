# BA Case 03 — Integrating two warehouse teams without it reading as a takeover

**Type:** Change management / stakeholder alignment. **Deliverables:** a stakeholder analysis (power/interest grid + RACI matrix) and a full change management plan.

[Stakeholder map exhibit](exhibits/stakeholder-map.html) · [Change Management Plan](artifacts/change_management_plan.docx) · [Stakeholder analysis workbook](artifacts/stakeholder_analysis.xlsx)

## The problem

Brightpath Distribution acquired Colton Regional Supply, a smaller regional distributor with two warehouse sites and about 85 employees. The two companies' warehouse operations need to integrate onto one WMS, one shift/scheduling policy, and one reporting structure within four months — without disrupting order fulfillment for either customer base. The technical side of this (a systems migration, a new org chart) is the easy part. The hard part, and the reason this is a change-management problem rather than a project-management one, is that every Colton employee's live worry is whether this is a partnership or a takeover, and the answer depends entirely on how the integration is run, not on what gets decided.

## Method

1. **Stakeholder analysis** — mapped 12 stakeholders (or stakeholder groups) by power to influence the integration and interest in its outcome, to decide who gets managed closely versus simply kept informed, rather than treating "communicate with everyone the same way" as a plan.
2. **RACI matrix** — assigned Responsible/Accountable/Consulted/Informed across the nine key integration activities, deliberately mirroring Colton and Brightpath roles at each level (e.g., both companies' warehouse ops managers hold the same Responsible role for shift-policy design) — checked programmatically to confirm every activity has exactly one accountable owner, not zero or several.
3. **Change impact assessment** — six areas of change (systems, reporting lines, scheduling, safety procedures, payroll, brand/identity), each rated for impact severity and current staff readiness, since "high impact + low readiness" areas are where a change plan actually needs to concentrate effort.
4. **Communication, training, and resistance planning** — a phased communication plan, an audience-specific training plan, and a resistance risk register built from what stakeholder interviews actually surfaced as fears, not a generic template.

## Key finding

The interviews surfaced one dominant resistance risk, named explicitly by multiple Colton employees: the fear of being folded into "how Brightpath already does things" with no real input. That reframed the entire plan — the RACI matrix mirrors Colton and Brightpath roles at every activity where both are plausible owners (both sites' ops managers are jointly Responsible for scheduling-policy design, for instance, rather than Brightpath designing and Colton reviewing), and the communication plan opens with a listening phase before any design work starts, specifically so the design sessions can start from "what already works at each site" instead of a Brightpath template with Colton's name added.

Of the 12 stakeholders mapped, the highest-power, highest-interest group (Manage Closely: the COO, both companies' operational leads, and HR) is where the two-way ownership actually gets enforced; the two warehouse-staff groups (Keep Informed, the highest-anxiety group, per the readiness ratings) get the most frequent, most concrete communication rather than the least, which is the opposite of how communication effort often gets allocated by default (loudest to the people with the most power to ask for it, not the people who need it most).

## Recommendation & business impact

Run the integration in six phases over roughly sixteen weeks — announcement, discovery/listening, co-designed process changes, pre-go-live training, go-live with on-floor support, and a two-week reinforcement period — with adoption tracked explicitly (WMS daily-use rate, unresolved question backlog, fulfillment accuracy during cutover) rather than assuming a completed system migration equals a completed integration. The resistance risk register names Colton-staff attrition before cutover as the highest-likelihood, highest-impact risk, with a concrete mitigation (named-individual retention conversations before the announcement goes wide) rather than a generic "communicate change well" mitigation.

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

**Limitations, stated plainly:** Brightpath, Colton, and every stakeholder here are simulated for this portfolio. Power and interest ratings are a single analyst's judgment call rather than a scored group exercise, which a real engagement would normally run as a workshop with the actual sponsors in the room, since the ratings materially change who gets prioritized.
