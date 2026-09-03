# BA Case 02 — Choosing a CRM the sales team will actually use

**Type:** Requirements gathering & systems selection. **Deliverables:** a business requirements document with a full traceability matrix, and a weighted vendor evaluation.

[Vendor scorecard exhibit](exhibits/vendor-scorecard.html) · [Business Requirements Document](artifacts/business_requirements_document.docx) · [Vendor evaluation matrix](artifacts/vendor_evaluation_matrix.xlsx)

## The problem

Brightpath Distribution's 40-person sales team runs on a 9-year-old on-premise CRM that most reps have quietly abandoned in favor of personal spreadsheets, because it's slow and unusable from the field. There's no single source of truth for pipeline: the VP Sales' weekly forecast deck is manually rebuilt from four separate regional spreadsheets and is routinely two or more weeks stale by the time it's presented. The ask that started this project was simply "we need a new CRM" — which is a solution looking for a problem statement, not the other way around.

## Method

1. **Discovery** — 13 structured interviews across sales reps, regional managers, the VP Sales, IT, Finance/RevOps, and Marketing Ops, to find out what was actually broken versus what people assumed a "modern CRM" would fix for them.
2. **Requirements gathering** — translated interview findings into 14 functional and 5 non-functional requirements, prioritized with MoSCoW (Must/Should/Could/Won't) rather than treating every request as equally urgent.
3. **BRD** — documented business objectives, scope, stakeholders, requirements, and assumptions in a formal Business Requirements Document, with a traceability matrix linking every requirement back to the business objective it serves.
4. **Vendor evaluation** — scored three vendors against seven weighted criteria (drawn directly from the requirements) in a formula-driven scoring model, rather than a subjective "which one did the demo team like best."

## Key finding

The loudest complaint ("we need a modern CRM") wasn't actually the root problem — the interviews surfaced that reps had stopped trusting the *current* system enough to enter data into it at all, which meant any replacement's success would hinge less on features and more on mobile usability and how little friction it added to a rep's day. That reframed the requirement set: pipeline management and reporting scored highest by weight (38% combined) because they're the reason the project exists, but mobile usability and low-friction data entry were elevated as design non-negotiables rather than nice-to-haves, because the current system's failure mode was exactly "nobody uses it."

## Recommendation & business impact

**Northstar CRM**, scoring 4.22 of 5 (weighted) against Vertex Sales Suite (4.01) and Pinnacle Sales Cloud (3.57) — and, notably, also the cheapest of the three at $206,560 over 3 years for 40 seats, so this isn't a case of paying a premium for the top score. Northstar's real gap is integration: both the ERP and marketing-automation connections need a middleware connector rather than a native one, which is the one area the runner-up is genuinely stronger in. That's flagged explicitly in the BRD (Section 9) as an implementation-planning item to scope and cost up front, not a surprise to discover mid-rollout — a vendor recommendation that hides its own recommended vendor's weak spot isn't a useful one.

## Repo structure

```
case-02-crm-selection/
├── scripts/
│   ├── 01_build_vendor_matrix.py                  builds the scoring workbook (openpyxl)
│   └── 02_build_brd.js                             builds the BRD (docx-js)
├── artifacts/
│   ├── vendor_evaluation_matrix.xlsx               Scoring + TCO Detail, formula-driven
│   └── business_requirements_document.docx         the formal BA deliverable
├── exhibits/vendor-scorecard.html                   visual vendor comparison
└── README.md
```

To reproduce: `cd scripts && python3 01_build_vendor_matrix.py && node 02_build_brd.js`. Verify the workbook with `recalc.py` from the xlsx skill (19 formulas, 0 errors).

**Limitations, stated plainly:** Brightpath, its stakeholders, and the three vendors are simulated for this portfolio — vendor names are fictional and the scores are illustrative, not a real product comparison. The scoring weights and 1–5 ratings reflect a stated, documented panel judgment (Sales Ops, IT, two Sales Managers) rather than an objective ground truth; a real evaluation would supplement this with reference calls to each vendor's existing customers before finalizing a recommendation.
