# Data notes

## What's real, what's simulated

Everything in this case — the company (Meridian Manufacturing), the phishing scenario, the timeline of events, and the specific timing figures — is simulated for this portfolio. No real incident occurred and no real organization named Meridian Manufacturing exists in this context.

The scenario design follows a real, publicly documented incident-response methodology: the phase structure (Preparation, Detection & Analysis, Containment/Eradication/Recovery, Post-Incident Activity) matches NIST Special Publication 800-61 ("Computer Security Incident Handling Guide"), which is the standard reference framework for structuring incident response in both government and private-sector security programs. The specific timing figures computed in this case (time-to-detect, time-to-contain, etc.) are the categories a real post-incident report would lead with, calculated the same way a real one would — first-occurrence timestamp per phase, differenced — but applied to an invented timeline rather than real log data.

## Files

- `raw/tabletop_timeline.csv` — the 15-event incident timeline as played in the exercise: elapsed hours, IR phase, the actor taking the action (Attacker / SOC Analyst / Incident Commander / IT + Security), and a plain-language description of the event.
- `raw/timeline_metrics.csv` — computed by `src/timeline_analysis.py`: time-to-detect, time-to-contain, time-to-eradicate, time-to-recover, total incident duration, active-encryption window, data-loss window, and volumes affected.

## Narrative continuity with the rest of the portfolio

This scenario deliberately reuses two elements already established elsewhere in the portfolio, rather than inventing a disconnected one-off:

1. **The compromised account, "user0147"**, is the same account identified as a confirmed compromise in the companion Log Analysis / Intrusion Detection case's low-and-slow credential-stuffing detection. This tabletop asks: if that account takeover had led to ransomware instead of stopping there, what would the response actually look like?
2. **The VPN gateway** is the same access path that appears in IT Case 01 (support-ticket SLA analysis) and IT Case 04 (the VPN outage runbook), and is the #1 refined-priority finding in the Vulnerability Assessment case (a Citrix VPN gateway RCE). This tabletop is the fourth appearance of the same VPN theme, this time as an attacker's initial-access path rather than a support burden or a scan finding.

## Methodology for the timing figures

Each IR phase's "start time" is the elapsed-hours value of the first event logged under that phase in the timeline CSV. The four core metrics are simple differences between consecutive phase-start times:

- Time to detect = (Detection phase start) − (Initial Access phase start)
- Time to contain = (Containment phase start) − (Detection phase start)
- Time to eradicate = (Eradication phase start) − (Containment phase start)
- Time to recover = (Recovery phase start) − (Eradication phase start)

The "active encryption window" is measured separately, from the specific event where ransomware staging/encryption began (hour 18.0, during Discovery & Lateral Movement — before detection even occurred) to the specific event where all attacker access was fully cut off (hour 29.0, the second containment action). This is a narrower, more specific window than "time to contain" and is reported separately because it's the number that actually explains why 2 of 6 volumes were still encrypted despite a fast 1.5-hour containment response — the attacker had an 11-hour head start that began well before anyone knew to look.

## Limitations

- This is a discussion-based tabletop exercise, not measured telemetry from a real incident or a live-fire red-team exercise — the timing figures reflect the exercise's own scenario design and the participating team's judgment of realistic phase durations, not logged timestamps from an actual detection tool.
- A single scenario (phishing → VPN → lateral movement → ransomware) is played here; a mature tabletop program runs multiple scenarios per year across different attack vectors (insider threat, supply-chain compromise, physical access, denial-of-service) rather than one recurring script.
