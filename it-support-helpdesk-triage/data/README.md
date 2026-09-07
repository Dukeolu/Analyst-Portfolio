# Data — Help Desk Ticket Triage & SLA Analysis

Simulated for this portfolio. Meridian Manufacturing, its employees, and every ticket in this dataset are fictional — a real company's help desk ticket export would be far too identifying (usernames, device names, issue descriptions) to publish even anonymized, so this project builds a realistic dataset from scratch instead.

## Files

### `raw/technicians.csv` (8 rows)

| Column | Description |
|---|---|
| `tech_id` | Technician ID (T01–T08) |
| `tech_name` | Technician name (fictional) |
| `specialty_categories` | Semicolon-separated list of the categories this technician specializes in (1–2 each) |

### `raw/tickets.csv` (877 rows)

| Column | Description |
|---|---|
| `ticket_id` | Ticket ID (HD-00001, …) |
| `created_at` | Ticket creation timestamp |
| `category` | One of 6 categories: Password Reset, Account Access, Email & Calendar, Hardware, Software Install, Network & VPN |
| `priority` | Low / Medium / High / Critical |
| `assigned_tech_id` | The technician assigned — chosen uniformly at random among all 8, simulating a "next available technician" round-robin policy that ignores specialty |
| `resolved_at` | Ticket resolution timestamp |
| `resolution_hours` | Elapsed hours from creation to resolution |
| `sla_target_hours` | The flat SLA target for this ticket's priority (Low 48h / Medium 24h / High 8h / Critical 4h) |
| `sla_breached` | Whether `resolution_hours` exceeded `sla_target_hours` |
| `reopened` | Whether the ticket was reopened after being marked resolved |

## How it was generated (`src/generate_data.py`)

877 tickets over 26 weeks (weekdays only, roughly 6 months), built to reproduce a specific, realistic help-desk dynamic rather than random noise:

- Each category has a **base resolution time** for a specialist-matched technician (0.4h for Password Reset up to 7.5h for Network & VPN — genuinely different complexity levels).
- The assigned technician is chosen **uniformly at random** among all 8, regardless of category — simulating the stated "next available" routing policy. Only 26.2% of tickets land with a matching specialist by chance.
- An **off-specialty ticket takes ~2.15x longer** to resolve than the same category handled by a matching specialist — the core mechanism this case investigates.
- **Priority gives a modest, real speed-up** (Critical tickets resolve ~30% faster, High ~15% faster) when technicians try to expedite — small next to the mismatch penalty.
- A **Monday effect** (+15% resolution time) reflects weekend backlog.
- **Reopen rate** is elevated for off-specialty tickets (12% vs. 4.5% baseline), reflecting a lower first-time-fix rate when the wrong person handles a ticket.
- Multiplicative log-normal noise on top of all of the above, for a realistic right-skewed resolution-time distribution.

## Limitations

- This is simulated data with seeded, deliberate patterns — real help desk data would have messier, less clean-cut relationships, and other real-world drivers (technician tenure, ticket complexity within a category, time-of-day staffing levels) that this simulation doesn't model.
- `resolution_hours` is elapsed **wall-clock** time from creation to resolution, not business-hours-adjusted (a ticket created Friday evening isn't credited with "paused" weekend hours) — a stated simplification. A real analysis would normally adjust for business hours and on-call coverage.
- Technician capacity (used in the routing counterfactual, see the main README) is a stated assumption (6 hours/week/specialist available for reactive ticket work), not measured from timesheets or actual project-allocation data.
