# Which Knowledge-Base Articles Are Actually Worth Writing? — Meridian Manufacturing (simulated)

**Skills:** Technical writing (two registers) &middot; ticket-data analysis &middot; incident-runbook design &middot; IT service management

## The business problem

Meridian Manufacturing's help desk has no self-service documentation — every issue, however routine, becomes a ticket. Writing KB articles is cheap; writing the *wrong* 5 KB articles wastes the effort and doesn't move the ticket volume at all. The real question isn't "can we write some help articles" — it's which specific issues, out of dozens, are worth the writing effort because they're both high-volume and genuinely self-service-solvable, versus issues that just look similar on the surface (a software access request generates plenty of tickets too, but no KB article can substitute for a manager's approval).

## Environment / data

6 months of simulated help desk tickets (1,814 rows), broken into 13 specific issue types across the 6 categories established in the help desk triage case (IT Case 01), each tagged with a disclosed self-service-eligibility judgment and a resolution time. No real ticketing export is available in this sandbox. Full methodology: [`data/README.md`](data/README.md).

## Method / tools

1. **Ticket-data ranking** (`src/deflection_analysis.py`) — ranks self-service-eligible issues by total technician time consumed (not raw ticket count, since a less-frequent-but-slower issue can matter more than a frequent, 2-minute one), and picks the top 5 as the KB articles worth writing.
2. **5 end-user KB articles** (`reports/kb-01` through `kb-05`) — plain-language, self-contained troubleshooting guides for the 5 highest-impact issues: VPN connection, printer troubleshooting, password reset, email-on-phone setup, and wifi connection. Each ends with a "still stuck? submit a ticket with X, Y, Z" escalation path, so the article speeds up ticket resolution even when it doesn't fully deflect the ticket.
3. **1 technician-facing incident runbook** (`reports/runbook-vpn-gateway-outage.md`) — a structured response procedure for a site-wide VPN gateway outage, written in the other register: checklist steps, target times, an explicit diagnostic order, and escalation contacts, for a technician mid-incident rather than a user troubleshooting alone.

## Analysis

The KB-topic selection is the actual analytical work in this case — the writing follows once the topics are chosen. Ranking by total ticket count alone would have prioritized "forgot network password" (344 tickets) over "can't connect to VPN" (260 tickets), but VPN connection issues take roughly 3x longer to resolve on average, so they actually consume more total technician time (3,467 minutes vs. 1,570 over the same 6 months) — reordering the priority list once time, not just frequency, is the metric. The VPN issue also got the technician-facing runbook in addition to its KB article, because it was independently established in IT Case 01 as the worst-performing SLA category (64.8% compliance) — when the same issue type shows up as a priority from two independent angles (ticket-time analysis here, SLA-compliance analysis there), that's a stronger signal than either alone.

## Key findings

1. **The 5 highest-impact self-service-eligible issues account for 340 technician-hours a year** — VPN connection (116 hrs/yr), printer troubleshooting (75 hrs/yr), password reset (52 hrs/yr), email-on-phone setup (49 hrs/yr), and wifi connection (48 hrs/yr).
2. **Ranking by ticket count alone would have picked a different, worse-performing list** — password reset has the highest raw ticket volume (344/6mo) but VPN connection consumes more total technician time despite fewer tickets (260/6mo), because each VPN ticket takes roughly 3x longer to resolve.
3. **Not every high-volume issue is self-service-eligible, and treating them as if they were would waste the writing effort** — "new software access request" (18/month) and "non-standard software request" (8/month) both generate real ticket volume but require a manager's approval, which no KB article can substitute for.
4. **The VPN issue justified both a KB article and a technician runbook**, because it was flagged as the priority issue independently twice: once here (highest technician-hours among self-service-eligible issues) and once in IT Case 01 (worst SLA-compliance category at 64.8%) — that's the two ends of the same problem, a user-facing self-service angle and a technician-facing incident-response angle.
5. **At a deliberately conservative, disclosed 25% self-service adoption rate**, these 5 articles would deflect an estimated 566 tickets a year and recover 85 technician-hours — real KB deflection rates vary widely by how well articles are promoted, so this is presented as a stated scenario, not a guarantee.

| Metric | Value |
|---|---|
| Addressable ticket volume (5 chosen topics) | 2,266/yr |
| Technician-hours at stake (5 chosen topics) | 340 hrs/yr |
| Stated self-service adoption assumption | 25% (conservative, disclosed) |
| Projected annual impact | $3,824 (85 technician-hours, 566 tickets deflected) |

## Recommendation

1. **Publish the 5 KB articles and link each one directly from its matching category on the ticket-submission form** — a KB article that exists but isn't surfaced at the moment someone is about to file a ticket gets a fraction of the deflection this analysis assumes.
2. **Deploy the VPN gateway outage runbook to the on-call rotation immediately** and walk the team through it once, since its value depends on technicians knowing it exists before the next outage, not discovering it mid-incident.
3. **Re-run the ranking quarterly** as ticket patterns shift — the next-highest-impact topics not selected this round (account-locked resets, standard software requests) are reasonable candidates for a second wave once these 5 are live and measured.
4. **Track actual deflection, not just article views**, once published — the 25% adoption assumption should be replaced with a measured number within the first quarter, and the projected impact revised accordingly.

## Expected impact

At the stated 25% adoption assumption, the 5 KB articles are projected to deflect roughly 566 tickets and recover 85 technician-hours a year (~$3,824 at the portfolio's standard $45/hour technician-cost assumption) — a modest, honestly-scoped number, since the real value of self-service documentation compounds over time as adoption grows past a conservative starting assumption. The VPN gateway outage runbook's impact is harder to put a single number on, since its value shows up as reduced outage duration on the (hopefully rare) occasions it's needed — but Meridian's own data makes the case for writing it: Network & VPN is both the single largest self-service-eligible time sink in routine tickets and the worst-performing SLA category overall.

> **The pitch in one line:** the right 5 KB articles aren't the 5 easiest to write — they're the 5 the ticket data actually says are worth it, and picking them wrong wastes the same writing effort as picking them right.

## Limitations / next analysis

- The self-service-eligibility judgment behind the ranking is a disclosed editorial call made during data generation, not derived from real user behavior — a real KB program would need to validate it against actual self-service portal analytics once articles are live.
- The 25% adoption assumption is stated and deliberately conservative, not measured — a real rollout should treat the first quarter of published-article analytics as the point where this assumption gets replaced with a real number.
- Ticket volumes and resolution times are simulated, not pulled from Meridian's real ticketing system (none is available in this sandbox) — the ranking methodology (total technician-time, not raw ticket count) is the transferable part regardless of the underlying numbers.
- This case only builds 5 end-user articles and 1 technician runbook — a full KB program would eventually cover the full issue catalog, and would need a review/update cadence (software changes, VPN client updates) that this one-time build doesn't address.
- The runbook's target times (10 minutes to first update, 60 minutes to resolution) are stated targets based on general IT incident-response practice, not derived from Meridian's own historical outage data (no historical VPN gateway outage log is available in this sandbox) — a real deployment would calibrate these against actual past incidents once that data exists.

## Repo structure

```
it-knowledge-base-runbooks/
├── README.md                              this file
├── requirements.txt
├── data/
│   ├── README.md                          data model, generation methodology, limitations
│   └── raw/
│       ├── tickets_6mo.csv
│       ├── deflection_summary.csv
│       └── deflection_impact.csv
├── src/
│   ├── generate_data.py                   builds the simulated 6-month ticket dataset
│   └── deflection_analysis.py             ranks issues, picks the top 5, quantifies impact
├── reports/
│   ├── kb-01-vpn-connection.md            end-user KB article
│   ├── kb-02-printer-troubleshooting.md   end-user KB article
│   ├── kb-03-password-reset.md            end-user KB article
│   ├── kb-04-email-on-phone.md            end-user KB article
│   ├── kb-05-wifi-connection.md           end-user KB article
│   └── runbook-vpn-gateway-outage.md      technician-facing incident runbook
└── visuals/
    ├── build_exhibit.py                   builds the HTML exhibit
    └── kb-runbook-exhibit.html            self-contained visual summary (site link)
```
