-- Show table schema 
\d+ retail;

-- Show first 10 rows
SELECT * FROM retail limit 10;

-- Check # of records
SELECT count(*) FROM retail;

-- Number of clients (e.g. unique client ID)
SELECT count(DISTINCT customer_id) FROM retail;

-- Invoice data range (e.g man/min dates)
SELECT max(invoice_date), min(invoice_date) FROM retail;

-- Number of SKU/merchants (e.g unique stock code)
SELECT count(DISTINCT stock_code) FROM retail;

-- Calculate average invoice amount excluding invoices with a negative amount
SELECT AVG(invoice_amount) AS avg
FROM (
  SELECT
    invoice_no,
    SUM(quantity * unit_price) AS invoice_amount
  FROM retail
  GROUP BY invoice_no
  HAVING SUM(quantity * unit_price) > 0
) t;

-- Calculate total revenue
SELECT SUM(unit_price*quantity) FROM retail;

-- Calculate total revenue by YYYYMM
SELECT
  CAST(concat(yyyy, lpad(mm :: int :: text, 2, '0')) AS INTEGER) as yyyymm,
  SUM(unit_price * quantity) AS sum
FROM
  (
    SELECT
      EXTRACT(YEAR FROM invoice_date) AS yyyy,
      EXTRACT(MONTH FROM invoice_date) AS mm,
      unit_price,
      quantity
    FROM
      retail
  ) t
GROUP BY
  yyyymm
ORDER BY
  yyyymm;
