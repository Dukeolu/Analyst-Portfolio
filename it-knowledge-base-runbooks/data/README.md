# Data — Knowledge Base &amp; Runbook Set

Simulated for this portfolio. Meridian Manufacturing's real ticket system isn't available here — a real KB-prioritization project would pull this from the ticketing system's own category/subcategory export.

## Files

### `raw/tickets_6mo.csv` (1,814 rows)

6 months of simulated help desk tickets, one row per ticket, broken down to the specific issue level (finer-grained than the 6 broad categories used in the help desk triage case) with a `self_service_eligible` flag: whether a well-written KB article could plausibly let the user resolve the issue without filing a ticket at all.

| Column | Description |
|---|---|
| `ticket_id` | Ticket ID |
| `month` | Month 1–6 |
| `category` | One of the 6 categories from the help desk triage case (IT Case 01) |
| `issue` | The specific issue within that category |
| `self_service_eligible` | Y/N — whether this specific issue is a candidate for KB deflection |
| `resolution_minutes` | Simulated technician time to resolve |

### `raw/deflection_summary.csv` and `raw/deflection_impact.csv`

Output of `src/deflection_analysis.py` — the top 5 issues by total technician time, and the annualized deflection impact under the stated adoption assumption.

## How it was generated (`src/generate_data.py`)

13 issue types were defined across the 6 established ticket categories, each with a monthly volume and average resolution time chosen to be plausible for a ~650-employee manufacturer, and a manual judgment call on self-service eligibility: a forgotten password or a printer that shows offline is something a KB article can walk a user through; a non-standard software request that needs manager approval is not, no matter how well documented, because it requires another human's decision. That eligibility judgment — not ticket volume alone — is what separates the 5 chosen KB topics from issues that generate just as many tickets but wouldn't actually be deflectable (e.g., "new software access request").

## Limitations

- The self-service-eligibility judgment (which issues a KB article could plausibly resolve) is a disclosed editorial call in the data generation, not derived from real user behavior — a real KB program would validate this against actual self-service portal analytics once articles are live (do users who view the article actually stop short of filing a ticket, or file one anyway?).
- The 25% self-service adoption rate used in the impact calculation is a stated, deliberately conservative assumption, not measured — real KB deflection rates vary widely by how well the articles are promoted (linked directly from the ticket-submission form for that issue type vs. buried in a general KB search).
- Ticket volumes and resolution times are simulated from realistic distributions, not pulled from a real ticketing system export.
