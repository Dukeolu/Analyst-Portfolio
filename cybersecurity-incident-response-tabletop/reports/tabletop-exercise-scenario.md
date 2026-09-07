# Incident Response Tabletop Exercise: Ransomware via Phishing-Compromised VPN Account

**Meridian Manufacturing (simulated) &middot; Exercise date: 2026 Q1 &middot; Facilitator: IT Security**
**Format:** Discussion-based tabletop, 90 minutes &middot; **Participants:** Incident Commander, SOC Analyst, IT Infrastructure Lead, Warehouse Operations Manager, Communications/Legal liaison

---

## Purpose &amp; scope

This exercise tests Meridian's incident response plan against a specific, plausible scenario: an employee's VPN credentials are stolen via phishing, the attacker uses them to move laterally, and the incident escalates to ransomware on a shared file server. The scenario deliberately starts from an account type this organization has already identified as a real compromise vector — see the companion Log Analysis / Intrusion Detection case, where account-takeover activity on a similar low-and-slow credential-stuffing pattern was independently detected. This exercise asks: if that kind of compromise led to ransomware instead of stopping at account takeover, how would the response actually go?

## Scenario narrative (read aloud to participants, one inject at a time)

**Inject 1 (T+0:00):** A Warehouse &amp; Ops supervisor reports receiving what looked like a normal "VPN password expiring" email, and clicked through to what they now realize wasn't the real login page. They mention this in passing to IT two days later, unrelated to any active alert. *(Facilitator note: in the live exercise, this inject was deliberately delayed — it represents a common real-world failure mode where the phishing report doesn't reach the security team until well after initial compromise.)*

> **Discussion question:** Does Meridian have a clear, low-friction path for an employee to report "I think I clicked something bad" — and does that report reach the security team fast enough to matter?

**Inject 2 (T+0:30):** Unbeknownst to the team at this point in the exercise, the attacker has already authenticated to the VPN using the harvested credentials, from an external IP never previously associated with this account.

**Inject 3 (T+2:00 to T+18:00):** The attacker enumerates internal file shares reachable from the Warehouse VLAN, escalates privileges on the general-purpose file server using a cached local admin credential left over from a vendor support visit 8 months earlier, and begins staging a ransomware payload plus exfiltrating a sample of shared-drive files.

> **Discussion question:** Should a vendor support account still have been active and privileged 8 months after the engagement ended? Who owns auditing that?

**Inject 4 (T+26:00):** A SOC alert fires for anomalous after-hours data volume leaving the file server to an unfamiliar external IP.

> **Discussion question:** Walk through triage in real time — what does the analyst check first, and who do they escalate to, and how fast?

**Inject 5 (T+27:30):** The incident commander declares a P1 incident.

> **Discussion question:** What's the actual containment sequence — network isolation first, or account disablement first, or both simultaneously? Who has the authority to pull a production file server's switch port without further approval?

**Inject 6 (T+31:00):** The team discovers ransomware encryption already began on 2 of the file server's 6 shared-drive volumes before containment completed.

> **Discussion question:** What's the recovery plan for those 2 volumes? What's the actual, verified age of the last good backup?

**Inject 7 (T+48:00):** Debrief.

## Full timeline (as played)

See [`data/raw/tabletop_timeline.csv`](../data/raw/tabletop_timeline.csv) for the complete event-by-event log. Key timing results:

| Metric | Result |
|---|---|
| Time to detect (initial access &rarr; detection) | 26.0 hours |
| Time to contain (detection &rarr; containment) | 1.5 hours |
| Time to eradicate (containment &rarr; eradication) | 5.5 hours |
| Time to recover (eradication &rarr; recovery) | 7.0 hours |
| Active encryption window (staging &rarr; full containment) | 11.0 hours |
| Volumes affected / data loss | 2 of 6 volumes; ~4 hours of data since last backup |
| Total incident duration | 48.0 hours |

---

# After-Action Report

## What went right

1. **Once detected, containment was fast** — 1.5 hours from alert to full network isolation and account disablement, well within Meridian's target response window. The automated after-hours data-volume alert did its job.
2. **The backup restore worked cleanly** — the 2 affected volumes were restored from the previous night's backup with a bounded, known data-loss window (4 hours), not an open-ended "we're not sure what we lost."
3. **The decision to rebuild rather than clean the file server in place** was made quickly and correctly — no debate in the exercise about whether a "cleaned" host could be trusted.

## Gaps identified

1. **26 hours from initial compromise to detection is the single biggest problem in this timeline**, and none of it was a technology failure — it was a reporting-path failure. The phishing click happened at T+0, but the employee's own report of "something felt off" didn't reach IT for two days, well after the automated alert already fired independently. **Recommendation: a one-click, no-blame phishing-report button in the email client**, with a target internal SLA for security to acknowledge within 30 minutes — treating "I think I clicked something" as a first-class alert source, not an afterthought.
2. **The privilege-escalation path (a vendor support account, still active and privileged 8 months after the engagement ended) was entirely preventable and wasn't specific to this attack** — it's a standing gap independent of how the attacker got in. **Recommendation: a quarterly access review specifically for third-party/vendor accounts**, with automatic expiration tied to the engagement's contracted end date rather than manual deactivation.
3. **No ransomware-specific incident runbook existed before this exercise** — the team improvised the containment sequence in real time rather than following a rehearsed checklist, which is exactly what a tabletop is supposed to surface before a real incident does. **Recommendation: adapt the VPN gateway outage runbook format (see the companion Knowledge Base &amp; Runbook Set case) into a ransomware-specific runbook**, with the same structure: trigger conditions, target times, a diagnostic/decision order, and named escalation authority for network isolation.
4. **The account used in this scenario (a low-and-slow credential-stuffing pattern) is the same category independently flagged in the Log Analysis / Intrusion Detection case's account-takeover rule** — this exercise assumed that detection layer wasn't yet in place. **Recommendation: re-run this tabletop after that detection rule is deployed**, to test whether it would have caught this compromise at the account-takeover stage, hours before any file-server activity began, rather than 26 hours in via a data-exfiltration alert.

## Recommendations, prioritized

| Priority | Recommendation | Owner | Target |
|---|---|---|---|
| 1 | One-click phishing-report button + 30-minute security acknowledgment SLA | IT Security | Next quarter |
| 2 | Quarterly vendor/third-party account access review, tied to contract end dates | IT Infrastructure | Next quarter |
| 3 | Ransomware-specific IR runbook (same format as the VPN outage runbook) | IT Security | This month |
| 4 | Re-run this tabletop after the account-takeover detection rule is deployed | IT Security | After that rule ships |

## Expected impact

The single largest lever in this scenario is time-to-detect, not time-to-contain — once detected, Meridian's team contained the incident in 1.5 hours, well within a defensible target. But 26 of the incident's 48 total hours elapsed before detection even began, and the exercise traced that specifically to a reporting-path gap, not a technology gap. Closing that gap (a low-friction phishing report path with a fast security-team SLA) has a plausible, disclosed potential to catch the next version of this scenario at Inject 1 rather than Inject 4 — turning a 26-hour blind window into one measured in minutes.

> **The pitch in one line:** the technology response in this exercise worked — the fastest fix isn't a new tool, it's making it easier and faster for a person who suspects they made a mistake to say so.

## Limitations / next analysis

- This is a discussion-based tabletop, not a live-fire simulation — timing estimates for each phase reflect the team's own judgment of how long each step would realistically take, not measured performance under real incident conditions.
- The scenario deliberately reuses an account-compromise pattern already established in the companion Log Analysis / Intrusion Detection case for narrative and analytical continuity — a real tabletop program would rotate through multiple distinct attack vectors (insider threat, supply-chain compromise, physical access) rather than one recurring scenario.
- The financial impact of the 4-hour data-loss window and the incident response effort itself isn't quantified here — a full business-impact analysis would need input from the business units whose data was on the affected volumes, which this exercise didn't attempt to model.
- Recommendation 4 (re-running this tabletop after the detection rule ships) is a genuinely open loop as of this writing — see the Risk Register / GRC case for how these four recommendations are tracked through to closure.
