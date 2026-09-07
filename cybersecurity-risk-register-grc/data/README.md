# Data notes

## What's real, what's simulated

The company (Meridian Manufacturing) and every risk entry in this register are simulated for this portfolio — no real organization, scan, or incident is represented. What's real is the scoring approach (likelihood x impact, inherent vs. residual, tracked to closure by owner and target date) and the framework used to categorize each risk: NIST's Cybersecurity Framework (CSF) 2.0, whose six function names — Govern, Identify, Protect, Detect, Respond, Recover — are the standard, publicly published high-level structure used across government and private-sector security programs. This case uses those function names to categorize risks; it does not reproduce NIST's framework text.

## Files

- `raw/risk_register.csv` — the register itself: 15 risks, each with an inherent likelihood/impact/score, a residual likelihood/impact/score (given current controls), a status, an owner, a target date, and a note tying it back to the specific case it came from.
- `raw/grc_summary.csv` — portfolio-level rollup: total inherent/residual score, overall risk reduction %, and counts by status.
- `raw/csf_coverage.csv` — residual risk grouped by NIST CSF 2.0 function.
- `reports/risk-register.xlsx` — the same register as a live Excel workbook (see below).

## This case is a rollup, not a fresh list

Every risk in this register cites the specific case it was identified in, rather than being invented fresh for this exercise:

- **R01, R02, R12** — from the Vulnerability Assessment (Cyber Case 02): the Log4Shell finding, the Citrix VPN gateway RCE (the refined-priority #1 finding), and the residual backlog of lower-severity findings outside the 8-hour remediation window.
- **R03, R09, R10** — from the Security Hardening project (Cyber Case 03): the disclosed, time-boxed legacy-TLS exception, and the two hardening categories (Access & SSH; Filesystem) that went from largely non-compliant to fully compliant.
- **R04, R05, R06, R08, R11** — from the Incident Response Tabletop (Cyber Case 04): the stale vendor credential that was the actual lateral-movement path in the exercise, the missing ransomware runbook, the 26-hour detection gap and its root cause, the missing recurring vendor-access review, and the backup recovery window.
- **R07** — carried forward from the portfolio's Log Analysis / Intrusion Detection case, where the account-takeover pattern was first flagged.
- **R13, R14** — synthesized at the register level: R13 is the policy-level root cause underneath both R04 and R08 (no deprovisioning trigger tied to contract end dates); R14 notes that the VPN gateway recurs as a theme across four separate cases (IT Case 01's SLA analysis, IT Case 04's outage runbook, Cyber Case 02's RCE finding, and Cyber Case 04's initial-access path) and formalizes the common fix — multi-factor authentication — as a tracked risk rather than leaving the pattern implicit.
- **R15** — from the Knowledge Base & Runbook Set case (IT Case 04): the self-service adoption assumption used in that case's quantification.

## Scoring methodology

Each risk carries two scores:

- **Inherent risk** = likelihood (1-5) x impact (1-5), before any control is applied — what the risk would look like with nothing in place.
- **Residual risk** = likelihood (1-5) x impact (1-5), given the controls actually in place today (a patch, a hardening pass, a partially-built detection rule, or nothing yet, for risks still open).
- **Risk reduction %** = (inherent − residual) / inherent.

For a fully remediated risk (e.g., R01, the patched Log4Shell finding), residual likelihood drops sharply while residual impact may stay high — the theoretical severity of Log4Shell on that server hasn't changed, but the likelihood of it being exploited has, because the vulnerability is patched. For an open risk (e.g., R06, the phishing-reporting gap), inherent and residual scores are identical, because no control has yet been applied — the register is honest about the difference between "identified and tracked" and "actually fixed."

## The Excel workbook

`reports/risk-register.xlsx` is a working spreadsheet, not a static export of the CSV. The `Risk Register` sheet computes inherent score, residual score, and risk-reduction % as live formulas (`=likelihood*impact`, etc.) rather than hardcoded values, with conditional color-scale formatting on residual score. The `GRC Summary` sheet rolls the register up with `SUMIF`/`COUNTIF` formulas referencing the register sheet directly — editing a risk's likelihood, impact, or status on the first sheet updates every summary number on the second sheet automatically. Formula evaluation was verified with a LibreOffice headless recalculation pass, confirming the workbook's live-formula outputs match `src/grc_analysis.py`'s independently computed numbers exactly (169 inherent points, 116 residual, 31.4% overall reduction).

## Limitations

- All likelihood and impact scores are simulated judgment calls consistent with each source case's findings, not the output of a formal quantitative risk model (e.g., FAIR) or an actual risk committee's scoring session.
- A real risk register would be reviewed and re-scored on a cadence (typically quarterly) with a named risk owner signing off on each score — this register represents a single point-in-time snapshot.
- The NIST CSF 2.0 function mapping is a simplification: a real GRC program typically maps risks to CSF Categories and Subcategories (a much finer-grained structure) rather than only the six top-level Functions used here.
