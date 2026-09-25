-- ============================================================
-- POWER BI ANALYTICS VIEWS
-- Global Energy Market Engine
-- ============================================================

-- 1. Daily WTI prices
CREATE OR REPLACE VIEW vw_wti_daily AS
SELECT
    date,
    commodity,
    price,
    unit,
    source
FROM market_prices
WHERE commodity = 'WTI Crude Oil';


-- 2. Monthly WTI summary
CREATE OR REPLACE VIEW vw_wti_monthly AS
SELECT
    DATE_TRUNC('month', date)::DATE AS month,
    COUNT(*) AS trading_days,
    ROUND(AVG(price), 2) AS average_price,
    ROUND(MIN(price), 2) AS minimum_price,
    ROUND(MAX(price), 2) AS maximum_price
FROM market_prices
WHERE commodity = 'WTI Crude Oil'
GROUP BY DATE_TRUNC('month', date)
ORDER BY month;


-- 3. WTI forecast data
CREATE OR REPLACE VIEW vw_wti_forecasts AS
SELECT
    forecast_date,
    commodity,
    predicted_price,
    model
FROM forecasts
WHERE commodity = 'WTI Crude Oil'
ORDER BY forecast_date;


-- 4. Combined actual + forecast dataset
CREATE OR REPLACE VIEW vw_wti_actual_forecast AS
SELECT
    date,
    price AS actual_price,
    NULL::NUMERIC AS predicted_price,
    'Actual' AS data_type
FROM market_prices
WHERE commodity = 'WTI Crude Oil'

UNION ALL

SELECT
    forecast_date AS date,
    NULL::NUMERIC AS actual_price,
    predicted_price,
    'Forecast' AS data_type
FROM forecasts
WHERE commodity = 'WTI Crude Oil'

ORDER BY date;


-- 5. WTI market statistics
CREATE OR REPLACE VIEW vw_wti_statistics AS
SELECT
    COUNT(*) AS total_records,
    MIN(date) AS start_date,
    MAX(date) AS end_date,
    ROUND(AVG(price), 2) AS average_price,
    ROUND(MIN(price), 2) AS minimum_price,
    ROUND(MAX(price), 2) AS maximum_price,
    COUNT(*) FILTER (WHERE price < 0) AS negative_price_days
FROM market_prices
WHERE commodity = 'WTI Crude Oil';
