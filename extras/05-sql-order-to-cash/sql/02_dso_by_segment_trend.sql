-- DSO by segment, by quarter -- and the naive read a finance team would
-- take from this alone: Enterprise (Net 60) looks like it drags DSO up
-- simply because its terms are longest. A 2-quarter trailing average
-- (window function) smooths quarter-to-quarter noise so the trend is
-- readable rather than jagged.

WITH quarterly AS (
    SELECT
        c.segment,
        c.payment_terms_days,
        strftime('%Y', i.invoice_date) || '-Q' ||
            ((CAST(strftime('%m', i.invoice_date) AS INTEGER) - 1) / 3 + 1) AS quarter,
        -- a sortable key so the trailing-average window orders correctly
        strftime('%Y', i.invoice_date) * 10 +
            ((CAST(strftime('%m', i.invoice_date) AS INTEGER) - 1) / 3 + 1) AS quarter_key,
        i.invoice_amount,
        s.days_to_pay_in_full
    FROM invoice_payment_status s
    JOIN invoices  i ON i.invoice_id = s.invoice_id
    JOIN customers c ON c.customer_id = s.customer_id
    WHERE s.status = 'Paid'   -- only invoices we can measure a completed cycle for
),
agg AS (
    SELECT
        segment,
        payment_terms_days,
        quarter,
        quarter_key,
        COUNT(*)                                                      AS invoices_paid,
        ROUND(SUM(invoice_amount * days_to_pay_in_full) / SUM(invoice_amount), 1) AS dso_weighted_days
    FROM quarterly
    GROUP BY segment, quarter, quarter_key
)
SELECT
    segment,
    payment_terms_days,
    quarter,
    invoices_paid,
    dso_weighted_days,
    dso_weighted_days - payment_terms_days AS days_beyond_terms,
    -- 2-quarter trailing average per segment, to show the underlying trend
    ROUND(AVG(dso_weighted_days) OVER (
        PARTITION BY segment ORDER BY quarter_key
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ), 1) AS dso_3q_trailing_avg
FROM agg
ORDER BY segment, quarter_key;
