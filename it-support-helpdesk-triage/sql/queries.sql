-- Q1. Overall SLA compliance, and by category -- the number leadership
-- already sees in monthly reporting (92.4% overall), versus what's hiding
-- underneath it once you break it out by category.
SELECT
  category,
  COUNT(*) AS n_tickets,
  ROUND(100.0 * SUM(CASE WHEN sla_breached = 0 THEN 1 ELSE 0 END) / COUNT(*), 1) AS sla_compliance_pct,
  ROUND(AVG(resolution_hours), 2) AS avg_resolution_hours
FROM tickets
GROUP BY category
ORDER BY sla_compliance_pct ASC;

-- Q2. The mechanism: resolution time, SLA breach rate, and reopen rate by
-- whether the assigned technician's specialty matches the ticket's category.
-- This is the query that isolates the real driver behind Q1's ranking.
SELECT
  assignment_type,
  COUNT(*) AS n_tickets,
  ROUND(AVG(resolution_hours), 2) AS avg_resolution_hours,
  ROUND(100.0 * SUM(CASE WHEN sla_breached = 1 THEN 1 ELSE 0 END) / COUNT(*), 1) AS sla_breach_pct,
  ROUND(100.0 * SUM(CASE WHEN reopened = 1 THEN 1 ELSE 0 END) / COUNT(*), 1) AS reopen_pct
FROM tickets
GROUP BY assignment_type;

-- Q3. Same mechanism, broken out by category -- shows the mismatch penalty
-- is present in every category but largest, in absolute hours, in the three
-- most complex ones (Network & VPN, Software Install, Hardware).
SELECT
  category,
  assignment_type,
  COUNT(*) AS n_tickets,
  ROUND(AVG(resolution_hours), 2) AS avg_resolution_hours
FROM tickets
GROUP BY category, assignment_type
ORDER BY category, assignment_type;

-- Q4. SLA breach rate by priority, and by priority x assignment match --
-- shows the priority system's "expedite" effect is real but small next to
-- the mismatch penalty, especially for Critical tickets: a Critical ticket
-- handled off-specialty breaches its 4-hour target far more often than a
-- Low-priority ticket handled by a specialist.
SELECT
  priority,
  assignment_type,
  COUNT(*) AS n_tickets,
  ROUND(100.0 * SUM(CASE WHEN sla_breached = 1 THEN 1 ELSE 0 END) / COUNT(*), 1) AS sla_breach_pct
FROM tickets
GROUP BY priority, assignment_type
ORDER BY
  CASE priority WHEN 'Critical' THEN 1 WHEN 'High' THEN 2 WHEN 'Medium' THEN 3 ELSE 4 END,
  assignment_type;

-- Q5. The cost of the problem, by category: total "wasted hours" for
-- off-specialty tickets, measured against that category's own median
-- specialist-handled resolution time -- ranked to show where a fix
-- matters most, in absolute technician-hours.
WITH matched_median AS (
  SELECT category,
         AVG(resolution_hours) AS avg_matched_hours   -- see note below
  FROM tickets
  WHERE assignment_type = 'Specialist match'
  GROUP BY category
),
mismatched AS (
  SELECT t.category, t.resolution_hours, mm.avg_matched_hours
  FROM tickets t
  JOIN matched_median mm ON mm.category = t.category
  WHERE t.assignment_type = 'Off-specialty'
)
SELECT
  category,
  COUNT(*) AS n_mismatched_tickets,
  ROUND(SUM(MAX(resolution_hours - avg_matched_hours, 0)), 1) AS total_wasted_hours
FROM mismatched
GROUP BY category
ORDER BY total_wasted_hours DESC;
-- Note: this query uses each category's mean specialist-handled resolution
-- time as the "should have taken" baseline (SQLite has no built-in median
-- aggregate); the Python analysis recomputes the same comparison using the
-- median, which is more robust to the right-skewed resolution-time
-- distribution -- see notebooks/ticket_triage_analysis.ipynb.
