CREATE TABLE IF NOT EXISTS market_prices (
    id BIGSERIAL PRIMARY KEY,
    date DATE NOT NULL,
    commodity VARCHAR(100) NOT NULL,
    description TEXT,
    price NUMERIC(12, 4) NOT NULL,
    unit VARCHAR(50),
    source VARCHAR(50) NOT NULL DEFAULT 'EIA',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT unique_market_price
        UNIQUE (date, commodity)
);

CREATE INDEX IF NOT EXISTS idx_market_prices_date
    ON market_prices(date);

CREATE INDEX IF NOT EXISTS idx_market_prices_commodity
    ON market_prices(commodity);


CREATE TABLE IF NOT EXISTS forecasts (
    id BIGSERIAL PRIMARY KEY,
    forecast_date DATE NOT NULL,
    commodity VARCHAR(100) NOT NULL,
    predicted_price NUMERIC(12, 4) NOT NULL,
    model VARCHAR(100) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_forecasts_date
    ON forecasts(forecast_date);

CREATE INDEX IF NOT EXISTS idx_forecasts_commodity
    ON forecasts(commodity);


CREATE TABLE IF NOT EXISTS data_quality_logs (
    id BIGSERIAL PRIMARY KEY,
    run_timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    commodity VARCHAR(100) NOT NULL,
    records_received INTEGER NOT NULL,
    missing_values INTEGER NOT NULL DEFAULT 0,
    duplicate_records INTEGER NOT NULL DEFAULT 0,
    negative_prices INTEGER NOT NULL DEFAULT 0,
    status VARCHAR(20) NOT NULL
);