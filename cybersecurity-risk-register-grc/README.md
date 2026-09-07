# Nine Cases, One Risk Register — Meridian Manufacturing (simulated)

**Skills:** GRC &middot; risk register design &middot; NIST CSF 2.0 &middot; Excel formula modeling &middot; prioritization

## The business problem

Every case in this portfolio's IT & Cybersecurity track produced findings: patched CVEs, a hardening exception, gaps a tabletop exercise surfaced, a detection rule still being built. Each one was reported and closed out in its own write-up. None of that is worth anything to a real security program unless it lands somewhere a person can look at all of it at once, see what's actually still open, and know who owns fixing it by when. This case builds that one place: a risk register that rolls up every open thread from the rest of the track, scored consistently and mapped to a standard framework, so nothing that was found gets quietly forgotten once its own case is closed.

## Environment / data

15 risks pulled from six different cases across this portfolio, each scored on a standard inherent-vs-residual likelihood x impact model and mapped to a NIST CSF 2.0 function (Govern, Identify, Protect, Detect, Respond, Recover). Full source mapping and scoring methodology: [`data/README.md`](data/README.md).

## Method / tools

1. **Register construction** (`src/generate_data.py`, `data/raw/risk_register.csv`) — 15 risks, each citing the specific case it was identified in, scored inherent vs. residual.
2. **Portfolio rollup** (`src/grc_analysis.py`) — total risk reduction, status breakdown, and residual risk by CSF function.
3. **A working Excel workbook** (`src/build_workbook.py` &rarr; `reports/risk-register.xlsx`) — the register as a live spreadsheet: likelihood x impact and risk-reduction % are formulas, not hardcoded values, and a `GRC Summary` sheet rolls the register up with `SUMIF`/`COUNTIF` referencing the register sheet directly.
4. **Visual exhibit** (`visuals/build_exhibit.py`) — a residual-risk heat map (every risk plotted by likelihood x impact, colored by status), a CSF-function coverage chart, and a ranked list of the highest-priority open risks.

## Analysis

Scoring every risk on the same inherent-vs-residual model, rather than treating each case's findings as separately-scaled severities, is what makes the rollup actually comparable: a "critical" CVE and a "moderate" process gap can now sit on the same ranked list, and the ranking is defensible rather than a gut call. That ranking surfaces something the individual case write-ups didn't: the two highest-residual-risk items left open aren't from the vulnerability scan at all — they're a detection-and-reporting gap (R06) and a missing MFA rollout (R14), a pattern only visible once everything is on one list scored the same way.

## Key findings

1. **Overall portfolio risk was reduced 31.4%** (169 inherent points &rarr; 116 residual points) across the 15 tracked risks, driven mainly by the 4 fully closed findings from the Vulnerability Assessment and Security Hardening cases.
2. **The two highest-residual-risk items left open are tied at a score of 16**: R06 (the tabletop's phishing-reporting detection gap) and R14 (single-factor VPN authentication) — neither one is a CVE; both are process and configuration gaps that a vulnerability scan alone would never surface.
3. **Protect carries the most residual risk points (43 across 7 risks)**, which is expected — patching and hardening produce the most individually-scored technical findings — but Detect and Govern carry meaningful residual risk too (25 and 18 points) despite having only 2 risks each, meaning those gaps are individually more severe, not just fewer in number.
4. **8 of 15 risks (53%) are still open or in progress** — this register makes that visible and owned, rather than letting "we found it, we wrote it up" quietly stand in for "we fixed it."
5. **Two open risks (R04 and R08) share the same underlying policy gap** — no deprovisioning trigger tied to vendor contract end dates — captured as its own tracked risk (R13) so the register drives one fix instead of two separate ones.

| Metric | Value |
|---|---|
| Total risks tracked | 15 |
| Overall risk reduction | 31.4% (169 &rarr; 116 points) |
| Closed | 4 of 15 |
| Open / in progress | 8 of 15 (89 residual points) |
| Top open risk (tied) | R06 (detection gap) &amp; R14 (VPN single-factor auth), residual 16 each |

## Recommendation

1. **Prioritize R06 and R14 next** — both tied for the highest residual score among open risks, and both are process/configuration fixes rather than a patch cycle, which typically means faster time-to-close than another vulnerability remediation pass.
2. **Fix R13 (the deprovisioning policy gap) to close R04 and R08 in one motion** — a shared root cause is a two-for-one opportunity this register is specifically built to surface.
3. **Re-score this register quarterly**, not just after each new case's findings land — a risk register that's only ever added to and never re-scored stops being a prioritization tool and becomes an archive.
4. **Extend the register to cover the remaining 4 cases in this portfolio's DA and BA tracks** as a next iteration — this case demonstrates the model on the IT & Cybersecurity track; the same rollup approach would apply cleanly to operational and process risk from the rest of the portfolio.

## Expected impact

The register's real value isn't the 31.4% reduction number — it's that R06 and R14, the two highest-priority items left on the list, were never actually named as "the top priority" in any single case's own write-up. The tabletop case's after-action report ranked its own four recommendations by priority, but R14 (VPN MFA) only becomes visible as equally urgent once it's scored on the same scale and placed next to everything else the portfolio has found. That's what a GRC rollup is for: not reporting new findings, but making sure the right ones get worked on next.

> **The pitch in one line:** nine cases produced nine sets of findings — this is the one place all of them get scored the same way, so "what do we fix next" has an actual answer instead of nine separate opinions.

## Limitations & next steps

- All scores are simulated judgment calls consistent with each source case's findings, not output from a formal quantitative model (e.g., FAIR) or a real risk committee's review session — see [`data/README.md`](data/README.md) for the full scoring methodology.
- This is a point-in-time snapshot; a real GRC program re-scores on a recurring cadence with named sign-off, which this single register build doesn't simulate.
- The CSF mapping uses only the six top-level Functions, not the finer-grained Categories/Subcategories a mature program would map to.
- This register covers the IT & Cybersecurity track only; extending the same model to the portfolio's Data Analyst and Business Analyst tracks is noted above as a natural next step, not yet attempted here.

## Repo structure

```
cybersecurity-risk-register-grc/
├── README.md                          this file
├── requirements.txt
├── data/
│   ├── README.md                      data model, source-case mapping, methodology
│   └── raw/
│       ├── risk_register.csv
│       ├── grc_summary.csv
│       └── csf_coverage.csv
├── src/
│   ├── generate_data.py               builds the 15-risk register from source-case findings
│   ├── grc_analysis.py                portfolio rollup: reduction %, status, CSF coverage
│   └── build_workbook.py              builds the live-formula Excel workbook
├── reports/
│   └── risk-register.xlsx             working Excel risk register (live formulas)
└── visuals/
    ├── build_exhibit.py                builds the HTML exhibit
    └── risk-register-exhibit.html      self-contained visual summary (site link)
```
