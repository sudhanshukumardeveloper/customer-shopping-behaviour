"""Load the cleaned dataset into PostgreSQL.

The database schema is created separately by sql/create_tables.sql. This script
preserves that schema (including the primary key, checks, indexes, and views),
truncates the existing data, and reloads the validated cleaned CSV.
"""

import os
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy import SmallInteger, Numeric, Text


DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "shopping_db")

CSV_PATH = os.path.join("data", "processed", "customer_shopping_behavior_cleaned.csv")

if not DB_PASSWORD:
    raise RuntimeError("Set DB_PASSWORD as an environment variable before running the ingestion script.")

COLUMN_TYPES = {
    "customer_id": SmallInteger(),
    "age": SmallInteger(),
    "gender": Text(),
    "item_purchased": Text(),
    "category": Text(),
    "purchase_amount": Numeric(10, 2),
    "location": Text(),
    "size": Text(),
    "color": Text(),
    "season": Text(),
    "review_rating": Numeric(3, 1),
    "subscription_status": SmallInteger(),
    "shipping_type": Text(),
    "discount_applied": SmallInteger(),
    "previous_purchases": SmallInteger(),
    "payment_method": Text(),
    "frequency_of_purchases": Text(),
    "age_group": Text(),
    "purchase_frequency_days": SmallInteger(),
}


def main() -> None:
    print(f"Loading: {CSV_PATH}")
    df = pd.read_csv(CSV_PATH)
    print(f"  {len(df):,} rows x {df.shape[1]} columns loaded.")

    if df["customer_id"].isna().any() or not df["customer_id"].is_unique:
        raise ValueError("customer_id must be non-null and unique.")

    connection_url = (
        f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}"
        f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
    engine = create_engine(connection_url, future=True)

    # The DDL owns the table structure. Do not use if_exists='replace':
    # replacing the table would remove constraints, indexes and views.
    with engine.begin() as conn:
        conn.execute(text("TRUNCATE TABLE customer"))
        df.to_sql(
            name="customer",
            con=conn,
            if_exists="append",
            index=False,
            dtype=COLUMN_TYPES,
            method="multi",
            chunksize=500,
        )

        db_count = conn.execute(text("SELECT COUNT(*) FROM customer")).scalar()
        assert db_count == len(df), "Row count mismatch after ingestion."

    print(f"Ingestion complete. Rows in 'customer' table: {db_count:,}")


if __name__ == "__main__":
    main()
