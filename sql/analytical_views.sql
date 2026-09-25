-- ============================================================
-- GLOBAL ENERGY MARKET ENGINE
-- Analytical Views
-- ============================================================

-- ------------------------------------------------------------
-- 1. Daily WTI price series
-- ------------------------------------------------------------

CREATE OR REPLACE VIEW wti_daily AS
SELECT
    date,
    price,
    unit,
    commodity
FROM market_prices
WHERE commodity = 'WTI Crude Oil'
ORDER BY date;


-- ------------------------------------------------------------
-- 2. Daily returns
-- ------------------------------------------------------------

CREATE OR REPLACE VIEW wti_returns AS
SELECT
    date,
    price,
    LAG(price) OVER (ORDER BY date) AS previous_price,

    CASE
        WHEN LAG(price) OVER (ORDER BY date) IS NULL THEN NULL
        WHEN LAG(price) OVER (ORDER BY date) = 0 THEN NULL
        ELSE
            (price - LAG(price) OVER (ORDER BY date))
            / LAG(price) OVER (ORDER BY date) * 100
    END AS daily_return_pct,

    CASE
        WHEN LAG(price) OVER (ORDER BY date) IS NULL THEN NULL
        WHEN price <= 0 OR LAG(price) OVER (ORDER BY date) <= 0 THEN NULL
        ELSE
            LN(
                price / LAG(price) OVER (ORDER BY date)
            )
    END AS log_return

FROM wti_daily
ORDER BY date;


-- ------------------------------------------------------------
-- 3. Rolling statistics
-- ------------------------------------------------------------

CREATE OR REPLACE VIEW wti_rolling_stats AS
SELECT
    date,
    price,

    AVG(price) OVER (
        ORDER BY date
        ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
    ) AS moving_avg_30d,

    AVG(price) OVER (
        ORDER BY date
        ROWS BETWEEN 89 PRECEDING AND CURRENT ROW
    ) AS moving_avg_90d,

    STDDEV_SAMP(price) OVER (
        ORDER BY date
        ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
    ) AS volatility_30d,

    STDDEV_SAMP(price) OVER (
        ORDER BY date
        ROWS BETWEEN 89 PRECEDING AND CURRENT ROW
    ) AS volatility_90d

FROM wti_daily
ORDER BY date;


-- ------------------------------------------------------------
-- 4. Monthly WTI statistics
-- ------------------------------------------------------------

CREATE OR REPLACE VIEW wti_monthly AS
SELECT
    DATE_TRUNC('month', date)::DATE AS month,
    COUNT(*) AS trading_days,
    ROUND(AVG(price), 2) AS average_price,
    ROUND(MIN(price), 2) AS minimum_price,
    ROUND(MAX(price), 2) AS maximum_price,
    ROUND(STDDEV_SAMP(price), 2) AS price_volatility
FROM wti_daily
GROUP BY DATE_TRUNC('month', date)
ORDER BY month;


-- ------------------------------------------------------------
-- 5. Yearly WTI statistics
-- ------------------------------------------------------------

CREATE OR REPLACE VIEW wti_yearly AS
SELECT
    EXTRACT(YEAR FROM date)::INTEGER AS year,
    COUNT(*) AS trading_days,
    ROUND(AVG(price), 2) AS average_price,
    ROUND(MIN(price), 2) AS minimum_price,
    ROUND(MAX(price), 2) AS maximum_price,
    ROUND(STDDEV_SAMP(price), 2) AS price_volatility
FROM wti_daily
GROUP BY EXTRACT(YEAR FROM date)
ORDER BY year;
