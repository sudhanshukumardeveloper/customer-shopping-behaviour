"""
ingest_to_postgres.py
=====================
Loads data/processed/customer_shopping_behavior_cleaned.csv into a
PostgreSQL table named `customer` using SQLAlchemy + pandas.

Dependencies
------------
    pip install sqlalchemy psycopg2-binary pandas

Usage
-----
    1. Set the five DB_* environment variables below (or edit the defaults).
    2. Run:  python python/ingest_to_postgres.py

The script will:
    - Create the `customer` table if it does not exist (via pandas to_sql).
    - Truncate and reload on repeated runs (if_exists='replace').
    - Print a row-count confirmation after ingestion.
"""

import os
import pandas as pd
from sqlalchemy import create_engine, text

# ── Database connection settings ───────────────────────────────────────────
# Override any of these via environment variables or edit the defaults below.
DB_USER     = os.getenv("DB_USER",     "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "your_password")
DB_HOST     = os.getenv("DB_HOST",     "localhost")
DB_PORT     = os.getenv("DB_PORT",     "5432")
DB_NAME     = os.getenv("DB_NAME",     "shopping_db")

# ── Paths ──────────────────────────────────────────────────────────────────
CSV_PATH = os.path.join("data", "processed", "customer_shopping_behavior_cleaned.csv")

# ── SQLAlchemy dtype mapping ───────────────────────────────────────────────
# Explicit types ensure PostgreSQL columns are sized correctly rather than
# defaulting to TEXT or DOUBLE PRECISION everywhere.
from sqlalchemy import (
    Integer, SmallInteger, Numeric, Text, Float
)

COLUMN_TYPES = {
    "age":                    SmallInteger(),
    "gender":                 Text(),
    "item_purchased":         Text(),
    "category":               Text(),
    "purchase_amount":        Numeric(10, 2),
    "location":               Text(),
    "size":                   Text(),
    "color":                  Text(),
    "season":                 Text(),
    "review_rating":          Numeric(3, 1),
    "subscription_status":    SmallInteger(),   # 0 or 1
    "shipping_type":          Text(),
    "discount_applied":       SmallInteger(),   # 0 or 1
    "previous_purchases":     SmallInteger(),
    "payment_method":         Text(),
    "frequency_of_purchases": Text(),
    "age_group":              Text(),
    "purchase_frequency_days": SmallInteger(),
}

def main() -> None:
    # 1. Load CSV
    print(f"Loading: {CSV_PATH}")
    df = pd.read_csv(CSV_PATH)
    print(f"  {len(df):,} rows x {df.shape[1]} columns loaded.")

    # 2. Build engine
    connection_url = (
        f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}"
        f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
    engine = create_engine(connection_url, future=True)
    print(f"Connecting to: {DB_HOST}:{DB_PORT}/{DB_NAME}")

    # 3. Write to PostgreSQL
    # if_exists='replace' drops and recreates the table on every run,
    # which is safe for an initial load. Switch to 'append' for incremental
    # loads once the table is established.
    with engine.begin() as conn:
        df.to_sql(
            name="customer",
            con=conn,
            if_exists="replace",   # use 'append' for incremental loads
            index=False,
            dtype=COLUMN_TYPES,
            method="multi",        # bulk INSERT; faster than row-by-row
            chunksize=500,
        )

    # 4. Verify row count
    with engine.connect() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM customer"))
        db_count = result.scalar()

    print(f"Ingestion complete. Rows in 'customer' table: {db_count:,}")
    assert db_count == len(df), "Row count mismatch! Check for duplicates."


if __name__ == "__main__":
    main()
