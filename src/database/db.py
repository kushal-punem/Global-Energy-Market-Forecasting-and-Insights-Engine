import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, text


load_dotenv()


def get_database_url() -> str:
    """Build the PostgreSQL connection URL."""

    host = os.getenv("DB_HOST")
    port = os.getenv("DB_PORT")
    database = os.getenv("DB_NAME")
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")

    required = {
        "DB_HOST": host,
        "DB_PORT": port,
        "DB_NAME": database,
        "DB_USER": user,
        "DB_PASSWORD": password,
    }

    missing = [
        key for key, value in required.items()
        if not value
    ]

    if missing:
        raise ValueError(
            f"Missing database environment variables: {missing}"
        )

    return (
        f"postgresql+psycopg2://"
        f"{user}:{password}@{host}:{port}/{database}"
    )


def get_engine():
    """Create and return a SQLAlchemy engine."""

    database_url = get_database_url()

    return create_engine(
        database_url,
        pool_pre_ping=True,
    )


def test_connection() -> None:
    """Test the PostgreSQL connection."""

    engine = get_engine()

    with engine.connect() as connection:
        result = connection.execute(
            text("SELECT current_database(), version();")
        )

        database, version = result.fetchone()

        print(f"Connected to database: {database}")
        print(f"PostgreSQL: {version}")


if __name__ == "__main__":
    test_connection()