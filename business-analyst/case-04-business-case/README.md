# BA Case 04 — Automate or keep hiring? A business case for order entry

**Type:** Business case & cost-benefit analysis. **Deliverables:** a formal business case with a risk register, and the 3-year NPV/payback model behind it.

[Business case exhibit](exhibits/business-case-summary.html) · [Business Case](artifacts/business_case.docx) · [Cost-benefit workbook](artifacts/cost_benefit_analysis.xlsx)

## The business problem

Brightpath Distribution's inbound sales-order team manually keys customer orders from fax, email PDF, and an EDI portal into the ERP. Order volume grows about 15% a year, and the team has already grown from 3 to 7 clerks over four years to keep pace. The request in front of the Operations Director was routine and easy to rubber-stamp: approve two more hires for next year. Nobody had actually put that request up against the alternative — this business case exists to do that comparison properly before the next headcount request gets approved on autopilot.

## The data

A 3-year order-volume projection at the stated 15%/year growth rate, headcount and productivity assumptions for the hire option, and OCR/RPA cost, adoption-ramp, and error-rate-benchmark assumptions for the automation option.

## Data preparation

Volume projections, headcount costs, and automation costs/adoption curves are simulated, stated assumptions for this portfolio rather than pulled from a real vendor quote or real order data — Brightpath is a fictional company. The preparation work was building the assumptions as their own explicit, auditable tab that every downstream number depends on (rather than burying them inside formulas where they're invisible), and modeling automation's error-rate benefit as its own separate line rather than folding it silently into the headcount comparison, so each benefit lever can be checked independently.

## Analysis

1. **Options framing** — three options considered: do nothing (rejected immediately on operational grounds, not worth modeling financially), keep hiring at current productivity, or invest in OCR/RPA automation. Only the latter two got a full financial model, since the first was never a real contender.
2. **3-year cost model** — projected order volume forward at the stated growth rate, then built each option's actual cost: hiring headcount to match volume one-for-one, versus automation absorbing a rising share of volume while headcount stays flat.
3. **Second-order benefit** — added what a pure headcount comparison misses: OCR-validated orders have a meaningfully lower error rate than hand-keyed ones, and order errors are expensive downstream (rework, reshipment, customer-service time). Modeled that as its own line, not folded silently into the headline number.
4. **NPV & payback** — discounted the year-by-year net benefit of automating over hiring at an 8% rate, and computed the payback period from the same cash flows, rather than reporting a 3-year total as if the money arrives evenly.

## Key findings

1. **The pure cost comparison alone is a weak case.** Automation saves only $80,000 over 3 years against continuing to hire — a 5% margin, not the kind of number that reliably survives a budget review on its own.
2. **The error-rate benefit is actually the stronger argument.** OCR-validated orders' lower error rate is worth an estimated $130,725 in avoided rework and customer-service cost over the same 3 years — more than the headcount savings themselves. A business case built only on "fewer people to hire" would have understated its own strongest argument.
3. **Year 1 is a net cost, not a benefit.** The one-time implementation charge outweighs a still-ramping automation share in year one — the 1.62-year payback period is what tells the honest story, not a 3-year total that hides a rough first year.

## Recommendations

1. **Invest in OCR/RPA automation** rather than approving the two additional hires.
2. **Keep headcount flat at 7** rather than growing to 11, redirecting freed capacity to exception handling and order-quality review.
3. **Track the redeployment plan as its own named risk** in the risk register — the savings case depends on freed capacity actually being redeployed, not simply assumed.

## Expected impact

**$210,725 net benefit over 3 years** ($80,000 in avoided hiring costs plus $130,725 in avoided order-error costs), a **3-year NPV of $165,288** at an 8% discount rate, and a **1.62-year payback**. Headcount stays flat at 7 rather than growing to 11.

> **The pitch in one line:** the headcount-only case barely clears the bar, but once the quality benefit is counted honestly, automation isn't a close call — it pays back in under two years.

## Limitations / next analysis

- Brightpath and every figure here are simulated for this portfolio.
- The model holds several real-world uncertainties as fixed assumptions — automation adoption ramping smoothly to 80% by Year 3, a stable 15%/year volume-growth rate, and error costs holding steady — each flagged individually in the risk register rather than smoothed away.
- A real version of this business case would sensitivity-test at least the growth-rate and adoption-rate assumptions before going to budget approval, since the pure-cost case (Finding 1) is thin enough that a slower adoption ramp could tip it negative on its own.
- The redeployment of freed headcount capacity is assumed, not verified — a real rollout should track whether the freed clerks' time was actually redirected to exception handling and quality review, or simply absorbed without a measurable benefit.

## Repo structure

```
case-04-business-case/
├── scripts/
│   ├── 01_build_cost_benefit.py                    builds the cost-benefit workbook (openpyxl)
│   └── 02_build_business_case.js                     builds the business case (docx-js)
├── artifacts/
│   ├── cost_benefit_analysis.xlsx                     Assumptions → Option B/C → NPV & Payback → Summary
│   └── business_case.docx                             the formal BA deliverable
├── exhibits/business-case-summary.html                 cumulative net-benefit / payback visualization
└── README.md
```

To reproduce: `cd scripts && python3 01_build_cost_benefit.py && node 02_build_business_case.js`. Verify the workbook with `recalc.py` from the xlsx skill (98 formulas, 0 errors).
