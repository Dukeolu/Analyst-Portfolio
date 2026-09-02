-- The point of this file: show that segment is a red herring and risk_tier
-- is the real driver. Two ranked breakdowns side by side (via UNION ALL so
-- they land in one result set), each ranked independently with RANK().

WITH paid AS (
    SELECT c.segment, c.risk_tier, s.invoice_amount, s.days_late_vs_due
    FROM invoice_payment_status s
    JOIN customers c ON c.customer_id = s.customer_id
    WHERE s.status = 'Paid'
),
by_segment AS (
    SELECT
        'by segment'                                                      AS cut,
        segment                                                           AS group_label,
        COUNT(*)                                                          AS invoices_paid,
        ROUND(SUM(invoice_amount * days_late_vs_due) / SUM(invoice_amount), 1) AS avg_days_late_weighted,
        RANK() OVER (ORDER BY SUM(invoice_amount * days_late_vs_due) / SUM(invoice_amount) DESC) AS rank_worst
    FROM paid
    GROUP BY segment
),
by_risk AS (
    SELECT
        'by risk tier'                                                    AS cut,
        risk_tier                                                         AS group_label,
        COUNT(*)                                                          AS invoices_paid,
        ROUND(SUM(invoice_amount * days_late_vs_due) / SUM(invoice_amount), 1) AS avg_days_late_weighted,
        RANK() OVER (ORDER BY SUM(invoice_amount * days_late_vs_due) / SUM(invoice_amount) DESC) AS rank_worst
    FROM paid
    GROUP BY risk_tier
)
SELECT * FROM by_segment
UNION ALL
SELECT * FROM by_risk
ORDER BY cut, rank_worst;

-- Follow-up, in the same file: how much of ALL outstanding AR at snapshot
-- is sitting specifically in SMB x High-risk -- the intersection the
-- segment-only view above would never surface.
-- (run separately -- see 05_smb_high_risk_concentration.sql)
