# Automating New-Hire Account Setup — Meridian Manufacturing (simulated)

**Skills:** PowerShell scripting &middot; Active Directory / Exchange administration &middot; process automation &middot; data analysis

## The business problem

Meridian Manufacturing's IT team provisions every new hire by hand: create the AD account, assign the right department security groups, create a home directory, stand up a mailbox, and — for remote-eligible roles — add VPN access. At ~148 hires a year, that's a recurring, repetitive task, and it was failing in a specific, fixable way: nearly 1 in 5 new hires didn't get every required security group on the first try, and 2 in 5 remote-eligible hires didn't have VPN access ready on day 1. Neither of those numbers is a training problem — it's what happens when the list of "which groups does this department need" lives in a technician's memory or a printed cheat-sheet instead of a system.

## Environment / data

A simulated year of new-hire volume (148 hires across 7 departments) run through two parallel logs: the historical manual process's per-step hands-on time and completion accuracy, and the same hire population run through the new automated script. No real AD/HR system is available in this sandbox, so both logs are constructed from realistic, disclosed assumptions rather than exported from a live environment. Full methodology: [`data/README.md`](data/README.md).

## Method / tools

1. **The automation script** (`src/onboarding_automation.ps1`) — a PowerShell script built to run against a real Active Directory + Exchange Online environment: reads a CSV of new hires, creates each AD account, assigns security groups from a single lookup table (`$DepartmentGroupMap`) keyed by department, adds the VPN group automatically when a hire is remote-eligible, provisions a home directory with the right ACL, and creates the Exchange mailbox — logging every action to a completion report. Supports `-WhatIf` for a dry-run preview before any change is made.
2. **Data generation** (`src/generate_data.py`) — builds the simulated new-hire population and both the manual and automated timing/accuracy logs.
3. **Comparison analysis** (`src/onboarding_analysis.py`) — computes hands-on technician time and error rates for both processes across the same 148 hires, and translates the difference into annual hours and dollars using a stated $45/hour technician-cost assumption.

## Analysis

The manual process was timed and audited step by step rather than treated as one lump "onboarding takes about half an hour" number, because the goal was to find which specific step was driving the error rate — not just to measure total time. Group assignment turned out to be both the slowest manual step (~8 minutes) and the least reliable one (18.9% miss rate), and VPN setup for remote-eligible hires was worse still (40.5% miss rate on day 1) despite taking under 2 minutes — confirming this wasn't a time-pressure problem, it was a "recalling the right list" problem. The automated script's design follows directly from that: it doesn't try to make the technician faster at recalling groups, it removes recall from the process entirely by reading from one table every time.

## Key findings

1. **Hands-on technician time per hire drops 90%** — from 28.3 minutes (manual) to 2.8 minutes (automated, which is just launching the script and reviewing its completion report; actual provisioning runs unattended).
2. **The manual process missed at least one required security group on 18.9% of hires** (28 of 148) — not because technicians were careless, but because group requirements lived in memory rather than a system.
3. **VPN access was missed on day 1 for 40.5% of remote-eligible hires** (15 of 37) under the manual process — the single worst accuracy number in the whole process, on the step that blocks a new remote employee from doing their job at all on day one.
4. **The automated script's error rate on both measures is 0%, by construction** — not because it's a smarter process, but because $DepartmentGroupMap is the same lookup table every single run, with no memory step involved.
5. **43 rework incidents a year are eliminated** — every missed group or missed VPN setup previously generated a follow-up access-request ticket, adding technician time and a delay for the new employee on top of the original task.

| Metric | Value |
|---|---|
| Hands-on technician time per hire | 28.3 min &rarr; 2.8 min (90.3% reduction) |
| Manual group-assignment miss rate | 18.9% (28 of 148 hires) |
| Manual VPN day-1 miss rate (remote-eligible) | 40.5% (15 of 37 hires) |
| Automated error rate (both measures) | 0%, by construction |
| Annual rework incidents eliminated | 43 |

## Recommendation

1. **Deploy `onboarding_automation.ps1` as the standard new-hire process**, replacing manual account setup entirely rather than using it as an optional speed-up — the accuracy gain matters as much as the time gain here.
2. **Treat `$DepartmentGroupMap` as a change-controlled artifact**, not a one-time setup — it's now the single source of truth for group assignment, so a new group or a department reorg needs the table updated before the next hire in that department runs through the script.
3. **Run every batch with `-WhatIf` first** when onboarding a large cohort (e.g., a seasonal warehouse hiring wave) to catch a bad CSV row (a misspelled department name, for instance) before it creates 20 improperly configured accounts instead of one.
4. **Extend the same lookup-table pattern to offboarding** — a termination process has the mirror-image error mode (missing a group *removal* is a security risk, not just an inconvenience), and the same structural fix applies.

## Expected impact

At Meridian's disclosed volume of 148 hires/year and a $45/hour fully-loaded technician cost, automating onboarding saves an estimated **$3,485/year** — 63.1 hours/year in reduced hands-on time plus 14.3 hours/year in rework avoided (43 incidents at 20 minutes each). The dollar figure is modest by design: the honest primary benefit here is accuracy, not raw time savings. A 40.5% VPN-day-1 miss rate for remote-eligible new hires is an onboarding-experience and productivity problem regardless of the minutes attached to fixing it, and eliminating it structurally — not by asking technicians to be more careful — is the actual deliverable.

> **The pitch in one line:** the manual process wasn't slow because people were bad at their jobs — it was error-prone because the list of what each department needs lived in someone's head, and a script that reads from a table instead doesn't have that problem.

## Limitations / next analysis

- The 148-hires/year volume and $45/hour technician cost are stated, disclosed assumptions, not pulled from real HR/payroll data — a real deployment would true both up before committing to the projected savings.
- Manual-process timing and error rates are simulated from realistic distributions, not measured from real ticket timestamps — a real analysis would instrument the actual manual process for a few weeks before building the automated replacement, to calibrate against real numbers rather than disclosed assumptions.
- The script is written and structured to run against a real AD + Exchange Online environment but was not executed against live infrastructure in this portfolio (none is available in this sandbox) — a real deployment would need a staging AD environment to validate it before production use, especially the SAM-account-name collision handling and ACL assignment logic.
- The script's error handling (a department not found in `$DepartmentGroupMap`) logs a warning and continues rather than halting the whole batch — that's a deliberate choice (one bad row shouldn't block 19 good ones) but means a real deployment needs someone reviewing the completion report for warnings, not just checking that the script exited successfully.
- This analysis doesn't cover offboarding, role changes, or department transfers — all of which have their own manual-process error modes that a fuller automation project would need to address separately.

## Repo structure

```
it-deployment-automation/
├── README.md                          this file
├── requirements.txt
├── data/
│   ├── README.md                      data model, generation methodology, limitations
│   └── raw/
│       ├── new_hires.csv
│       ├── manual_onboarding_log.csv
│       ├── automated_onboarding_log.csv
│       └── onboarding_comparison_summary.csv
├── src/
│   ├── generate_data.py               builds the simulated new-hire population + both logs
│   ├── onboarding_analysis.py         manual vs. automated comparison + dollar impact
│   └── onboarding_automation.ps1      the automation script (the credibility artifact)
└── visuals/
    ├── build_exhibit.py               builds the HTML exhibit
    └── onboarding-automation-exhibit.html   self-contained visual summary (site link)
```
