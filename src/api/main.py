from datetime import date
from typing import Optional

from fastapi import FastAPI, Query
from sqlalchemy import text

from src.database.db import get_engine


app = FastAPI(
    title="Global Energy Market Engine",
    description="API for WTI crude oil market data and analytics",
    version="1.0.0",
)


@app.get("/")
def root():
    return {
        "message": "Global Energy Market Engine API",
        "status": "running",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
    }


@app.get("/api/v1/wti")
def get_wti_data(
    start_date: Optional[date] = Query(
        default=None,
        description="Start date in YYYY-MM-DD format",
    ),
    end_date: Optional[date] = Query(
        default=None,
        description="End date in YYYY-MM-DD format",
    ),
    limit: int = Query(
        default=100,
        ge=1,
        le=1000,
        description="Maximum number of records",
    ),
):
    query = """
        SELECT
            date,
            commodity,
            description,
            price,
            unit,
            source
        FROM market_prices
        WHERE commodity = 'WTI Crude Oil'
    """

    params = {}

    if start_date:
        query += " AND date >= :start_date"
        params["start_date"] = start_date

    if end_date:
        query += " AND date <= :end_date"
        params["end_date"] = end_date

    query += """
        ORDER BY date DESC
        LIMIT :limit
    """

    params["limit"] = limit

    engine = get_engine()

    with engine.connect() as connection:
        result = connection.execute(
            text(query),
            params,
        )

        rows = result.mappings().all()

    return {
        "count": len(rows),
        "data": [dict(row) for row in rows],
    }

@app.get("/api/v1/wti/summary")
def get_wti_summary():
    query = """
        SELECT
            COUNT(*) AS total_records,
            MIN(date) AS first_date,
            MAX(date) AS last_date,
            ROUND(AVG(price), 2) AS average_price,
            MIN(price) AS minimum_price,
            MAX(price) AS maximum_price
        FROM market_prices
        WHERE commodity = 'WTI Crude Oil'
    """

    engine = get_engine()

    with engine.connect() as connection:
        result = connection.execute(text(query))
        row = result.mappings().one()

    return {
        "commodity": "WTI Crude Oil",
        "total_records": row["total_records"],
        "first_date": row["first_date"],
        "last_date": row["last_date"],
        "average_price": float(row["average_price"]),
        "minimum_price": float(row["minimum_price"]),
        "maximum_price": float(row["maximum_price"]),
    }

@app.get("/api/v1/wti/yearly")
def get_wti_yearly():
    query = """
        SELECT
            EXTRACT(YEAR FROM date)::INTEGER AS year,
            COUNT(*) AS trading_days,
            ROUND(AVG(price), 2) AS average_price,
            MIN(price) AS minimum_price,
            MAX(price) AS maximum_price
        FROM market_prices
        WHERE commodity = 'WTI Crude Oil'
        GROUP BY EXTRACT(YEAR FROM date)
        ORDER BY year;
    """

    engine = get_engine()

    with engine.connect() as connection:
        result = connection.execute(text(query))
        rows = result.mappings().all()

    return {
        "commodity": "WTI Crude Oil",
        "count": len(rows),
        "data": [dict(row) for row in rows],
    }

@app.get("/api/v1/wti/monthly")
def get_wti_monthly():
    query = """
        SELECT
            DATE_TRUNC('month', date)::DATE AS month,
            COUNT(*) AS trading_days,
            ROUND(AVG(price), 2) AS average_price
        FROM market_prices
        WHERE commodity = 'WTI Crude Oil'
        GROUP BY DATE_TRUNC('month', date)
        ORDER BY month;
    """

    engine = get_engine()

    with engine.connect() as connection:
        result = connection.execute(text(query))
        rows = result.mappings().all()

    return {
        "commodity": "WTI Crude Oil",
        "count": len(rows),
        "data": [dict(row) for row in rows],
    }


@app.get("/api/v1/wti/stats")
def get_wti_stats():

    query = """
        SELECT
            COUNT(*) AS total_records,
            MIN(date) AS first_date,
            MAX(date) AS last_date,
            ROUND(AVG(price), 2) AS average_price,
            MIN(price) AS minimum_price,
            MAX(price) AS maximum_price
        FROM market_prices
        WHERE commodity = 'WTI Crude Oil';
    """

    engine = get_engine()

    with engine.connect() as connection:
        result = connection.execute(text(query))
        row = result.mappings().one()

    return {
        "commodity": "WTI Crude Oil",
        "statistics": dict(row),
    }


@app.get("/api/v1/wti/negative")
def get_negative_wti_prices():
    query = """
        SELECT
            date,
            commodity,
            price,
            unit,
            source
        FROM market_prices
        WHERE commodity = 'WTI Crude Oil'
          AND price < 0
        ORDER BY date;
    """

    engine = get_engine()

    with engine.connect() as connection:
        result = connection.execute(text(query))
        rows = result.mappings().all()

    return {
        "commodity": "WTI Crude Oil",
        "count": len(rows),
        "data": [dict(row) for row in rows],
    }

@app.get("/api/v1/wti/extremes")
def get_wti_extremes():
    query = """
        SELECT
            date,
            commodity,
            price,
            unit,
            source
        FROM market_prices
        WHERE commodity = 'WTI Crude Oil'
          AND price = (
              SELECT MAX(price)
              FROM market_prices
              WHERE commodity = 'WTI Crude Oil'
          )

        UNION ALL

        SELECT
            date,
            commodity,
            price,
            unit,
            source
        FROM market_prices
        WHERE commodity = 'WTI Crude Oil'
          AND price = (
              SELECT MIN(price)
              FROM market_prices
              WHERE commodity = 'WTI Crude Oil'
          )

        ORDER BY price DESC;
    """

    engine = get_engine()

    with engine.connect() as connection:
        result = connection.execute(text(query))
        rows = result.mappings().all()

    return {
        "commodity": "WTI Crude Oil",
        "count": len(rows),
        "data": [dict(row) for row in rows],
    }

# ============================================================
# FORECAST ENDPOINTS
# ============================================================

@app.get("/api/v1/forecast")
def get_forecasts(
    limit: int = Query(default=30, ge=1, le=365)
):
    """
    Return future WTI price forecasts.
    """

    query = """
        SELECT
            forecast_date,
            commodity,
            predicted_price,
            model
        FROM forecasts
        WHERE commodity = 'WTI Crude Oil'
        ORDER BY forecast_date ASC
        LIMIT :limit;
    """

    engine = get_engine()

    with engine.connect() as connection:
        result = connection.execute(
            text(query),
            {"limit": limit}
        )

        rows = result.mappings().all()

    return {
        "count": len(rows),
        "data": [dict(row) for row in rows],
    }


@app.get("/api/v1/forecast/latest")
def get_latest_forecast():
    """
    Return the latest available WTI forecast.
    """

    query = """
        SELECT
            forecast_date,
            commodity,
            predicted_price,
            model
        FROM forecasts
        WHERE commodity = 'WTI Crude Oil'
        ORDER BY forecast_date DESC
        LIMIT 1;
    """

    engine = get_engine()

    with engine.connect() as connection:
        result = connection.execute(text(query))
        row = result.mappings().first()

    if row is None:
        return {
            "message": "No forecast data available"
        }

    return dict(row)


@app.get("/api/v1/forecast/evaluation")
def get_forecast_evaluation():
    """
    Return forecast model evaluation metrics.
    """

    return {
        "model": "RandomForest-v1",
        "metrics": {
            "MAE": 1.44,
            "RMSE": 2.40
        },
        "baseline_comparison": {
            "Naive": {
                "MAE": 13.81,
                "RMSE": 18.25
            },
            "30-Day Moving Average": {
                "MAE": 13.81,
                "RMSE": 18.23
            }
        }
    }