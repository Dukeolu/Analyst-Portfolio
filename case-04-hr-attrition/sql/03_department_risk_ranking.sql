-- Department-level attrition rate, ranked, with the average of the two
-- strongest structural risk factors (overtime and manager span) alongside
-- it -- so a reviewer can see *why* a department ranks where it does, not
-- just that it does.

WITH dept_stats AS (
    SELECT
        department,
        COUNT(*) AS employees,
        SUM(CASE WHEN terminated_voluntary = 'Yes' THEN 1 ELSE 0 END) AS voluntary_terms,
        ROUND(100.0 * SUM(CASE WHEN terminated_voluntary = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 2) AS term_rate_pct,
        ROUND(AVG(overtime_hours_monthly), 1) AS avg_overtime_hours,
        ROUND(AVG(manager_span), 1) AS avg_manager_span,
        ROUND(AVG(comp_ratio), 3) AS avg_comp_ratio
    FROM employees
    GROUP BY department
)
SELECT
    *,
    RANK() OVER (ORDER BY term_rate_pct DESC) AS risk_rank
FROM dept_stats
ORDER BY risk_rank;
