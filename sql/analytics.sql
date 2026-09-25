-- ============================================================
-- GLOBAL ENERGY MARKET ENGINE
-- WTI MARKET ANALYTICS
-- ============================================================


-- 1. Overall statistics
SELECT
    COUNT(*) AS total_records,
    MIN(date) AS first_date,
    MAX(date) AS last_date,
    ROUND(AVG(price), 2) AS average_price,
    ROUND(MIN(price), 2) AS minimum_price,
    ROUND(MAX(price), 2) AS maximum_price
FROM market_prices
WHERE commodity = 'WTI Crude Oil';


-- 2. Yearly average price
SELECT
    EXTRACT(YEAR FROM date)::INT AS year,
    COUNT(*) AS trading_days,
    ROUND(AVG(price), 2) AS average_price,
    ROUND(MIN(price), 2) AS minimum_price,
    ROUND(MAX(price), 2) AS maximum_price
FROM market_prices
WHERE commodity = 'WTI Crude Oil'
GROUP BY EXTRACT(YEAR FROM date)
ORDER BY year;


-- 3. Monthly average price
SELECT
    DATE_TRUNC('month', date)::DATE AS month,
    COUNT(*) AS trading_days,
    ROUND(AVG(price), 2) AS average_price
FROM market_prices
WHERE commodity = 'WTI Crude Oil'
GROUP BY DATE_TRUNC('month', date)
ORDER BY month;


-- 4. Highest 10 WTI prices
SELECT
    date,
    price,
    unit
FROM market_prices
WHERE commodity = 'WTI Crude Oil'
ORDER BY price DESC
LIMIT 10;


-- 5. Lowest 10 WTI prices
SELECT
    date,
    price,
    unit
FROM market_prices
WHERE commodity = 'WTI Crude Oil'
ORDER BY price ASC
LIMIT 10;


-- 6. Negative-price observations
SELECT
    date,
    price,
    unit
FROM market_prices
WHERE commodity = 'WTI Crude Oil'
  AND price < 0
ORDER BY date;


-- 7. Number of observations by year
SELECT
    EXTRACT(YEAR FROM date)::INT AS year,
    COUNT(*) AS observations
FROM market_prices
WHERE commodity = 'WTI Crude Oil'
GROUP BY EXTRACT(YEAR FROM date)
ORDER BY year;