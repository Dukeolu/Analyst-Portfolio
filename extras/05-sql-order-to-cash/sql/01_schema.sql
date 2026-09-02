-- Order-to-cash schema: customers -> orders -> invoices -> payments.
-- One order becomes one invoice; one invoice can receive one or more
-- payments (partial payments are common enough in this dataset to matter).

CREATE TABLE customers (
    customer_id         TEXT PRIMARY KEY,
    customer_name       TEXT NOT NULL,
    segment             TEXT NOT NULL CHECK (segment IN ('SMB','Mid-Market','Enterprise')),
    region              TEXT NOT NULL,
    payment_terms_days  INTEGER NOT NULL,
    risk_tier           TEXT NOT NULL CHECK (risk_tier IN ('Low','Medium','High'))
);

CREATE TABLE orders (
    order_id      TEXT PRIMARY KEY,
    customer_id   TEXT NOT NULL REFERENCES customers(customer_id),
    order_date    DATE NOT NULL,
    order_amount  REAL NOT NULL
);

CREATE TABLE invoices (
    invoice_id      TEXT PRIMARY KEY,
    order_id        TEXT NOT NULL REFERENCES orders(order_id),
    customer_id     TEXT NOT NULL REFERENCES customers(customer_id),
    invoice_date    DATE NOT NULL,
    due_date        DATE NOT NULL,
    invoice_amount  REAL NOT NULL
);

CREATE TABLE payments (
    payment_id      TEXT PRIMARY KEY,
    invoice_id      TEXT NOT NULL REFERENCES invoices(invoice_id),
    payment_date    DATE NOT NULL,
    payment_amount  REAL NOT NULL
);

CREATE INDEX idx_orders_customer ON orders(customer_id);
CREATE INDEX idx_invoices_customer ON invoices(customer_id);
CREATE INDEX idx_invoices_order ON invoices(order_id);
CREATE INDEX idx_payments_invoice ON payments(invoice_id);

-- The view every other query builds on: one row per invoice, its total
-- paid-to-date, outstanding balance, and (once fully paid) how many days
-- it took from invoice date and from due date.
CREATE VIEW invoice_payment_status AS
SELECT
    i.invoice_id,
    i.order_id,
    i.customer_id,
    i.invoice_date,
    i.due_date,
    i.invoice_amount,
    COALESCE(p.paid_amount, 0)                              AS paid_amount,
    i.invoice_amount - COALESCE(p.paid_amount, 0)           AS outstanding_balance,
    p.last_payment_date,
    CASE
        WHEN COALESCE(p.paid_amount, 0) >= i.invoice_amount THEN 'Paid'
        WHEN COALESCE(p.paid_amount, 0) > 0                 THEN 'Partially Paid'
        ELSE 'Unpaid'
    END                                                      AS status,
    CASE WHEN COALESCE(p.paid_amount, 0) >= i.invoice_amount
         THEN julianday(p.last_payment_date) - julianday(i.invoice_date) END AS days_to_pay_in_full,
    CASE WHEN COALESCE(p.paid_amount, 0) >= i.invoice_amount
         THEN julianday(p.last_payment_date) - julianday(i.due_date) END     AS days_late_vs_due
FROM invoices i
LEFT JOIN (
    SELECT invoice_id, SUM(payment_amount) AS paid_amount, MAX(payment_date) AS last_payment_date
    FROM payments
    GROUP BY invoice_id
) p ON p.invoice_id = i.invoice_id;
