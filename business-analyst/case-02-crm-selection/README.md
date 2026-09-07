# BA Case 02 — Choosing a CRM the sales team will actually use

**Type:** Requirements gathering & systems selection. **Deliverables:** a business requirements document with a full traceability matrix, and a weighted vendor evaluation.

[Vendor scorecard exhibit](exhibits/vendor-scorecard.html) · [Business Requirements Document](artifacts/business_requirements_document.docx) · [Vendor evaluation matrix](artifacts/vendor_evaluation_matrix.xlsx)

## The business problem

Brightpath Distribution's 40-person sales team runs on a 9-year-old on-premise CRM that most reps have quietly abandoned in favor of personal spreadsheets, because it's slow and unusable from the field. There's no single source of truth for pipeline: the VP Sales' weekly forecast deck is manually rebuilt from four separate regional spreadsheets and is routinely two or more weeks stale by the time it's presented. The ask that started this project was simply "we need a new CRM" — which is a solution looking for a problem statement, not the other way around.

## The data

13 structured interview transcripts across sales reps, regional managers, the VP Sales, IT, Finance/RevOps, and Marketing Ops, plus feature and pricing data for three CRM vendors (Northstar, Vertex, Pinnacle — fictional, but built to be comparable to real mid-market CRM offerings).

## Data preparation

The interview notes and vendor feature/pricing sheets are simulated for this portfolio rather than pulled from a real engagement — real vendor contracts and internal interview notes aren't something a portfolio can ethically reuse, even anonymized. The preparation work was translating unstructured interview findings into a structured, prioritized requirement set (14 functional + 5 non-functional requirements, MoSCoW-tagged) and normalizing three vendors' differently-structured feature and pricing sheets onto the same weighted scoring criteria, so the comparison is apples-to-apples rather than whichever vendor's own materials framed things most favorably.

## Analysis

1. **Discovery** — 13 structured interviews across sales reps, regional managers, the VP Sales, IT, Finance/RevOps, and Marketing Ops, to find out what was actually broken versus what people assumed a "modern CRM" would fix for them.
2. **Requirements gathering** — translated interview findings into 14 functional and 5 non-functional requirements, prioritized with MoSCoW (Must/Should/Could/Won't) rather than treating every request as equally urgent.
3. **BRD** — documented business objectives, scope, stakeholders, requirements, and assumptions in a formal Business Requirements Document, with a traceability matrix linking every requirement back to the business objective it serves.
4. **Vendor evaluation** — scored three vendors against seven weighted criteria (drawn directly from the requirements) in a formula-driven scoring model, rather than a subjective "which one did the demo team like best."

## Key findings

1. **The loudest complaint wasn't the root problem.** "We need a modern CRM" masked the real issue: reps had stopped trusting the current system enough to enter data into it at all, which meant any replacement's success would hinge less on features and more on mobile usability and how little friction it added to a rep's day.
2. **That reframed the requirement weighting.** Pipeline management and reporting scored highest by weight (38% combined) because they're the reason the project exists, but mobile usability and low-friction data entry were elevated to design non-negotiables rather than nice-to-haves, because the current system's failure mode was exactly "nobody uses it."
3. **Northstar wins on both fit and cost.** Northstar CRM scored 4.22/5 (weighted) against Vertex Sales Suite (4.01) and Pinnacle Sales Cloud (3.57) — and is also the cheapest of the three at $206,560 over 3 years for 40 seats, so this isn't a case of paying a premium for the top score.
4. **Northstar's real gap is integration.** Both the ERP and marketing-automation connections need a middleware connector rather than a native one — the one area the runner-up (Vertex) is genuinely stronger in.

## Recommendations

1. **Select Northstar CRM** — the highest-scoring option and the lowest-cost one.
2. **Scope and cost the middleware integration work explicitly during implementation planning** (flagged in BRD Section 9), rather than letting it surface as a rollout surprise.
3. **Weight future vendor evaluations toward mobile usability and low-friction entry** specifically when the underlying problem is adoption, not feature parity — a lesson from how this evaluation's own weighting had to be corrected after discovery.

## Expected impact

Northstar CRM selected — highest weighted score (4.22/5) *and* lowest 3-year TCO ($206,560) of the three candidates, meaning the decision doesn't trade cost for fit. Naming the integration gap up front, rather than discovering it mid-rollout, protects that TCO advantage from being eroded by an unplanned middleware project later.

## Limitations / next analysis

- Brightpath, its stakeholders, and the three vendors are simulated for this portfolio — vendor names are fictional and the scores are illustrative, not a real product comparison.
- The scoring weights and 1–5 ratings reflect a stated, documented panel judgment (Sales Ops, IT, two Sales Managers) rather than an objective ground truth.
- A real evaluation would supplement this with reference calls to each vendor's existing customers before finalizing a recommendation.
- The integration gap (middleware vs. native) is flagged but not itself costed in this model — a next step before signing would be getting an actual implementation-partner quote for the middleware work, to confirm it doesn't erode Northstar's TCO advantage.

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
