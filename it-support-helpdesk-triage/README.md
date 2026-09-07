# Why Doesn't the Help Desk's Own SLA Number Match User Complaints? — Meridian Manufacturing (simulated)

**Skills:** SQL &middot; Python &middot; data simulation &middot; capacity-constrained modeling &middot; IT service management (SLA/routing analysis)

## The business problem

Meridian Manufacturing (simulated, ~650-employee mid-size manufacturer) runs a central IT help desk with one flat SLA target per priority level (Low 48h, Medium 24h, High 8h, Critical 4h) and a "next available technician" assignment policy — whoever's free next gets the ticket, regardless of what they're actually good at. Monthly reporting shows **92.4% overall SLA compliance**, which reads as healthy. But user complaints keep coming in about slow VPN and software-install tickets specifically, and nobody could explain the gap between the reported number and what people are actually experiencing — because nobody had broken the aggregate number apart.

## The data

877 simulated help desk tickets over 26 weeks (~6 months), across 6 categories (Password Reset, Account Access, Email & Calendar, Hardware, Software Install, Network & VPN) and 8 technicians, each with 1–2 specialty categories. Full schema and generation methodology: [`data/README.md`](data/README.md).

## Data preparation

Ticket and technician records are generated directly (`src/generate_data.py`) rather than pulled from a real ticketing system — a real company's ticket export would be too identifying to publish even anonymized. Because it's generated rather than scraped, there's no missing-value or duplicate cleanup here; the preparation work was calibrating each category's base resolution time against realistic IT-support complexity levels (a password reset takes minutes; a VPN issue can take most of a day) and simulating technician assignment as genuinely uniform-random across all 8 technicians, to faithfully represent a policy that doesn't consider specialty at all. The two raw tables (`tickets`, `technicians`) were then loaded into SQLite, with a `assignment_type` (specialist-match vs. off-specialty) flag precomputed once in Python and reused across every SQL query, rather than re-deriving it five separate times.

## Analysis

1. **SQL** (`sql/queries.sql`, run via `sql/run_queries.py`) — SLA compliance by category, the specialty-match mechanism overall and by category, SLA breach rate by priority × specialty-match, and a ranking of "wasted technician-hours" by category (off-specialty resolution time minus that category's own median specialist-handled time).
2. **Python / notebook** (`notebooks/ticket_triage_analysis.ipynb`) — reproduces and extends the SQL findings with the median-based (more robust) version of the wasted-hours calculation, then runs a **capacity-constrained routing simulation** (`src/routing_model.py`): what would a specialist-first routing policy actually recover, given that specialists only have so many hours in a week — not an idealized "always match" ceiling.

## Key findings

1. **The aggregate SLA number is hiding a concentrated, specific problem.** 92.4% overall compliance looks fine, but Network & VPN tickets breach SLA **35.2%** of the time (64.8% compliance) and Software Install breaches **16.4%** of the time (83.6% compliance) — the other four categories are all above 93%.
2. **The driver is routing, not category complexity alone.** Only **26.2%** of tickets land with a technician whose specialty matches the ticket's category, because assignment is "next available," not skill-based. Off-specialty tickets take roughly **2.15x longer to resolve** than the same category handled by a matching specialist (aggregate median 3.96 vs. 1.86 hours) — the pattern holds in every category, worst in absolute hours for the three most complex ones (Network & VPN, Software Install, Hardware).
3. **Even Critical-priority tickets aren't protected from the mismatch.** The priority system does give a modest real speed-up (Critical tickets resolve ~30% faster when technicians try to expedite), but it's small next to the mismatch penalty: a Critical ticket breaches its 4-hour target **37.3%** of the time when handled off-specialty, versus **5.3%** when a specialist handles it — a 7x gap on the tickets the business can least afford to be slow on.
4. **Off-specialty tickets are also reopened more than twice as often** (11.3% vs. 4.3%) — a lower first-time-fix rate, not just a slower one.
5. **A realistic (not idealized) fix recovers about half the opportunity without hiring anyone.** A capacity-constrained simulation of specialist-first routing — using each category's *actual* specialist headcount and a stated, disclosed capacity assumption of 6 hours/week/specialist for reactive ticket work — fully resolves the mismatch in 3 of 6 categories (Account Access, Email & Calendar, Password Reset) but leaves Network & VPN still constrained (only 18.8% of its mismatched tickets convert), because it simply doesn't have enough specialist capacity today to absorb its own demand.

| Metric | Value |
|---|---|
| Overall SLA compliance | 92.4% |
| Network & VPN SLA compliance | 64.8% (worst) |
| Off-specialty assignment rate | 73.8% |
| Off-specialty vs. specialist-match resolution time | 2.15x longer (median) |
| Off-specialty vs. specialist-match reopen rate | 11.3% vs. 4.3% |

## Recommendations

1. **Switch to specialist-first routing**: route each ticket to an available specialist for its category first, and only fall back to "next available" when no specialist is free — a policy change, not a tooling purchase.
2. **Prioritize Network & VPN and Software Install for closer monitoring after rollout** — the simulation shows these two remain capacity-constrained even under specialist-first routing, so they're the ones to watch for whether the fix is actually landing.
3. **Add specialist capacity in Network & VPN specifically** (cross-train an additional technician, or adjust an existing generalist's specialty) — it's the only category where routing alone doesn't close the gap, because current specialist headcount (2 technicians) doesn't cover its own ticket volume even under ideal routing.
4. **Re-run this analysis quarterly** as ticket volume and technician specialties shift, since the recommendation depends on today's specific headcount and demand mix.

## Expected impact

Specialist-first routing, modeled against actual specialist capacity rather than an idealized ceiling, recovers an estimated **$91,754/year** in technician time (2,039 hours/year saved at a stated $45/hour fully-loaded technician cost) and lifts overall SLA compliance from 92.4% to **93.8%** — with **zero capital cost**, since it's a scheduling/routing policy change rather than a new tool or hire. This captures roughly **46%** of the full theoretical opportunity (~$200,781/year if every category had unlimited specialist capacity); the remainder requires adding specialist capacity specifically in Network & VPN, Hardware, and Software Install.

> **The pitch in one line:** the help desk doesn't have an SLA problem on paper — it has a routing problem that happens to be large enough to look like one in three specific categories, and fixing the routing (not buying a new tool) recovers most of it for free.

## Limitations / next analysis

- The ticket and technician data are simulated, so exact dollar figures are illustrative, not a real company's — the method (break an aggregate SLA number apart by category → isolate the mechanism (routing, not complexity) → model a realistic, capacity-constrained fix rather than an idealized one) is the transferable part.
- The $45/hour technician cost and the 6-hours/week/specialist reactive-ticket-capacity assumption are stated, disclosed inputs, not derived from this data or a real payroll/timesheet system — a real rollout would want to validate both against actual technician time-tracking before committing to the projected savings.
- Resolution time is elapsed wall-clock time, not business-hours-adjusted (see [`data/README.md`](data/README.md)) — a real analysis would normally exclude weekends/after-hours from the clock, which would tighten every resolution-time figure somewhat without changing the relative finding (mismatch still dominates).
- The routing simulation assumes specialists can be perfectly scheduled up to their stated capacity with no coordination overhead — a real specialist-first queue would need actual scheduling software and would likely capture somewhat less than this estimate in year one, before the process matures.
- This dataset only covers 26 weeks (about 6 months) — not long enough to see whether ticket-category mix shifts seasonally (e.g., a hardware refresh cycle, a security-driven VPN policy change) in a way that would change which category needs the most specialist capacity next year.

## Repo structure

```
it-support-helpdesk-triage/
├── README.md                      this file
├── requirements.txt
├── data/
│   ├── README.md                  data model, generation methodology, limitations
│   └── raw/
│       ├── tickets.csv
│       └── technicians.csv
├── src/
│   ├── generate_data.py           builds the simulated ticket dataset
│   └── routing_model.py           capacity-constrained specialist-first routing simulation
├── sql/
│   ├── build_db.py                loads the CSVs into SQLite (precomputes specialty-match flag)
│   ├── queries.sql                the 5 labelled analysis queries
│   └── run_queries.py             runs and prints all 5
├── notebooks/
│   ├── build_notebook.py          builds the notebook programmatically
│   └── ticket_triage_analysis.ipynb   the executed analysis notebook
└── visuals/
    ├── sla_compliance_by_category.png
    ├── resolution_time_by_match.png
    ├── wasted_hours_by_category.png
    ├── build_exhibit.py
    └── ticket-triage-exhibit.html     self-contained visual summary (site link)
```
