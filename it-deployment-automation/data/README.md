# Data — New-Hire Onboarding Automation

Simulated for this portfolio. Meridian Manufacturing's actual HR system and AD environment aren't available here — a real onboarding timing log would come from ticket-system timestamps, which aren't something this sandbox has access to.

## Files

### `raw/new_hires.csv` (148 rows)

One simulated year of new-hire volume for a ~650-employee manufacturer, across 7 departments, with a `remote_eligible` flag driving whether VPN provisioning applies.

### `raw/manual_onboarding_log.csv` (148 rows)

Per-hire hands-on technician time (minutes) for each of 7 manual onboarding steps, plus two completion flags: whether every required security group was assigned on the first try, and whether VPN access was ready on day 1 for remote-eligible hires.

### `raw/automated_onboarding_log.csv` (148 rows)

The same 148 hires run through the automated process: hands-on time is just launching the script and reviewing its completion report (provisioning itself runs unattended against AD/Exchange). Both completion flags are always "Y" by construction, since the script reads group requirements from one lookup table instead of a technician's memory.

### `raw/onboarding_comparison_summary.csv`

Output of `src/onboarding_analysis.py` — the headline comparison numbers.

## How it was generated (`src/generate_data.py`)

Manual per-step times were drawn from realistic distributions (account creation ~5 min, group assignment ~8 min, mailbox ~6 min, etc.), with two deliberately seeded error modes calibrated to be plausible for a manual, memory-driven process rather than picked to hit a target number: an 18.9% chance of missing at least one required security group, and a 40.5% chance of a remote-eligible hire not having VPN access ready on day 1. The automated log models the same hire population running through a lookup-table-driven script, where those two error modes go to 0% structurally (the script can't forget a group the table has correctly listed) rather than because the script is "smarter" than a person.

## Limitations

- The 148-hires/year volume and the $45/hour fully-loaded technician cost are stated, disclosed assumptions (the same technician cost used in the help desk triage case, for consistency across the portfolio) — a real deployment would validate both against actual HR headcount-growth plans and payroll data.
- Manual-process timing is simulated from a realistic distribution, not pulled from real ticket timestamps — the actual step-by-step breakdown at a real company would need to come from time-tracking data if this were re-run for real.
- The automated script's timing (script launch + report review) assumes a technician runs it once per hire or in a small daily batch — a larger batch run would amortize the hands-on time further, which this analysis doesn't model.
