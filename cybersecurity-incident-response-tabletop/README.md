# A Tabletop Finds the Gaps Before an Attacker Does — Meridian Manufacturing (simulated)

**Skills:** Incident response &middot; NIST SP 800-61 &middot; tabletop exercise design &middot; after-action reporting

## The business problem

A vulnerability scan finds known CVEs. A hardening pass fixes permissive defaults. Neither one answers the question that actually matters during a real incident: when something goes wrong, does the team know what to do, in what order, fast enough? The only way to find out before a real incident forces the answer is to rehearse one. This case runs a structured tabletop exercise against a specific, plausible scenario — a phished VPN account escalating to ransomware — and reports the timing metrics and gaps a real after-action report would lead with.

## Environment / data

A 15-event, 48-hour incident timeline (phishing → stolen VPN credentials → lateral movement via a stale vendor admin account → ransomware staging and exfiltration → detection → containment → eradication → recovery → debrief), scored against standard NIST SP 800-61 incident-response phases. The compromised account and VPN access path are deliberately reused from other cases in this portfolio for narrative and analytical continuity — see [`data/README.md`](data/README.md) for the full methodology and cross-references.

## Method / tools

1. **Scenario design** (`data/raw/tabletop_timeline.csv`) — a 15-event timeline spanning Initial Access, Discovery & Lateral Movement, Detection, Containment, Eradication, Recovery, and Post-Incident phases, with the actor and action logged at each step.
2. **Exercise facilitation** ([`reports/tabletop-exercise-scenario.md`](reports/tabletop-exercise-scenario.md)) — the scenario played out as discussion-based injects with discussion questions at each key decision point, the format used to actually run this kind of exercise with a live team.
3. **Timing analysis** (`src/timeline_analysis.py`) — computes the standard IR phase-transition metrics from the timeline: time-to-detect, time-to-contain, time-to-eradicate, time-to-recover, and a separate active-encryption window.
4. **After-action reporting** (same report file) — what went right, what gaps were identified, and prioritized, owned recommendations — the actual output a tabletop exercise exists to produce.

## Analysis

The timing breakdown makes the story obvious in a way a prose summary alone wouldn't: of the incident's 48 total hours, 26 of them (54%) elapsed before anyone knew anything was wrong, while containment itself took only 1.5 hours once detection happened. That split is the finding — this wasn't a team that responded slowly once alerted; it was a team that didn't get alerted until data was already 26 hours old. Tracing why led to a specific, fixable cause (a two-day gap between the employee noticing something was wrong and that information reaching security), not a vague "improve monitoring" recommendation.

## Key findings

1. **Time to detect (26.0 hours) is 17x longer than time to contain (1.5 hours)** — once the team knew, they moved fast; the entire problem is in the "knowing" step.
2. **The attacker had an 11-hour active-encryption window** (staging began at hour 18, full containment completed at hour 29) — encryption started 8 hours before the detection alert even fired, which is why 2 of 6 shared-drive volumes were already partially encrypted by the time isolation was complete.
3. **Data loss was bounded to 4 hours** thanks to a verified prior-night backup — the recovery step worked exactly as intended, with a known, defensible loss window rather than an open-ended one.
4. **The root cause of the detection gap was a reporting-path failure, not a technology failure** — the employee who was phished reported it two days later, well after an automated alert had already independently fired; the fix identified is a faster, lower-friction reporting path, not a new detection tool.
5. **The privilege-escalation step used a stale vendor support account, active 8 months after its engagement ended** — a standing access-review gap, independent of this specific attack.

| Metric | Result |
|---|---|
| Time to detect | 26.0 hours |
| Time to contain | 1.5 hours |
| Active encryption window | 11.0 hours |
| Data loss | 2 of 6 volumes; 4 hours since last backup |
| Total incident duration | 48.0 hours |

## Recommendation

1. **Ship a one-click, no-blame phishing-report button** with a 30-minute security-team acknowledgment SLA — the single highest-leverage fix, since it targets the 26-hour gap directly rather than the 1.5-hour part that already works.
2. **Run a quarterly vendor/third-party account access review**, with expiration tied to the contracted engagement end date — this gap wasn't specific to the ransomware scenario and would close a real, standing exposure regardless of how the next incident starts.
3. **Write a ransomware-specific IR runbook**, in the same trigger/target-time/decision-order format already proven in the companion Knowledge Base & Runbook Set case's VPN outage runbook — so the next response is executed, not improvised.
4. **Re-run this exact tabletop after the account-takeover detection rule (from the Log Analysis / Intrusion Detection case) is deployed**, to test whether it would catch this pattern at the account-takeover stage — hours earlier than the 26-hour data-exfiltration alert that caught it this time.

## Expected impact

The exercise's clearest, most defensible claim is about where the incident's 48 hours actually went: 26 hours undetected, 1.5 hours to contain once alerted. That split reframes the fix from "respond faster" (already fast) to "detect sooner" (the actual gap), and points to a specific, low-cost intervention — a faster human reporting path — rather than a large new tooling investment. The four recommendations from this exercise carry forward into the companion Risk Register / GRC case, where they're tracked to closure with owners and target dates rather than left as a one-time debrief output.

> **The pitch in one line:** the team's incident response worked once they knew — the exercise's real value was proving that "once they knew" was the whole problem, and pointing at exactly why.

## Limitations & next steps

- This is a discussion-based tabletop, not a live-fire simulation — phase timing reflects the exercise design and the participating team's judgment of realistic durations, not measured telemetry from a real detection system.
- The scenario deliberately reuses an account and VPN theme already established elsewhere in this portfolio for continuity; a real annual tabletop program rotates through several distinct attack vectors rather than replaying one scenario.
- No financial business-impact analysis is attempted for the 4-hour data-loss window or the response effort itself — see the companion cases for cost modeling done elsewhere in this portfolio (e.g., the $45/hour fully-loaded technician cost used across the IT Support cases).
- Recommendation 4 (re-testing after the detection rule ships) is an explicitly open loop, tracked forward into the Risk Register / GRC case.

## Repo structure

```
cybersecurity-incident-response-tabletop/
├── README.md                          this file
├── requirements.txt
├── data/
│   ├── README.md                      data model, methodology, cross-case continuity notes
│   └── raw/
│       ├── tabletop_timeline.csv
│       └── timeline_metrics.csv
├── src/
│   └── timeline_analysis.py           computes IR phase timing metrics from the timeline
├── reports/
│   └── tabletop-exercise-scenario.md  facilitation script + injects + After-Action Report
└── visuals/
    ├── build_exhibit.py                builds the HTML exhibit
    └── tabletop-exhibit.html           self-contained visual summary (site link)
```
