-- =============================================================================
-- create_tables.sql
-- Customer Shopping Behavior Database — DDL
-- =============================================================================
-- Run this script ONCE to create the schema before loading data.
-- The ingest_to_postgres.py script handles the actual data load via pandas
-- to_sql; this script is provided for documentation, manual setup, and
-- re-creation scenarios.
-- =============================================================================

-- Drop if re-running from scratch
DROP TABLE IF EXISTS customer;

-- ── Main table ────────────────────────────────────────────────────────────────
CREATE TABLE customer (
    -- Demographics
    age                     SMALLINT        NOT NULL CHECK (age BETWEEN 18 AND 120),
    gender                  TEXT            NOT NULL,

    -- Purchase details
    item_purchased          TEXT            NOT NULL,
    category                TEXT            NOT NULL,
    purchase_amount         NUMERIC(10, 2)  NOT NULL CHECK (purchase_amount >= 0),
    location                TEXT            NOT NULL,

    -- Product attributes
    size                    TEXT,
    color                   TEXT,
    season                  TEXT,

    -- Review
    review_rating           NUMERIC(3, 1)   CHECK (review_rating BETWEEN 1.0 AND 5.0),

    -- Customer profile
    subscription_status     SMALLINT        NOT NULL DEFAULT 0 CHECK (subscription_status IN (0, 1)),
    shipping_type           TEXT,
    discount_applied        SMALLINT        NOT NULL DEFAULT 0 CHECK (discount_applied IN (0, 1)),
    previous_purchases      SMALLINT        NOT NULL DEFAULT 0 CHECK (previous_purchases >= 0),
    payment_method          TEXT,

    -- Engineered features
    frequency_of_purchases  TEXT,
    age_group               TEXT,
    purchase_frequency_days SMALLINT        CHECK (purchase_frequency_days > 0)
);

-- ── Indexes for common query patterns ────────────────────────────────────────
-- These speed up the GROUP BY, WHERE, and JOIN patterns used in the analysis
-- and business queries.

-- Frequently filtered / grouped columns
CREATE INDEX idx_customer_gender           ON customer (gender);
CREATE INDEX idx_customer_category         ON customer (category);
CREATE INDEX idx_customer_subscription     ON customer (subscription_status);
CREATE INDEX idx_customer_discount         ON customer (discount_applied);
CREATE INDEX idx_customer_shipping_type    ON customer (shipping_type);
CREATE INDEX idx_customer_age_group        ON customer (age_group);
CREATE INDEX idx_customer_item_purchased   ON customer (item_purchased);

-- Range/aggregate columns
CREATE INDEX idx_customer_purchase_amount  ON customer (purchase_amount);
CREATE INDEX idx_customer_review_rating    ON customer (review_rating);
CREATE INDEX idx_customer_prev_purchases   ON customer (previous_purchases);

-- ── Optional: enumeration / lookup views ─────────────────────────────────────
-- Handy reference views — no separate lookup tables needed given the small
-- cardinality of each categorical column.

CREATE OR REPLACE VIEW v_categories AS
    SELECT DISTINCT category FROM customer ORDER BY 1;

CREATE OR REPLACE VIEW v_items AS
    SELECT DISTINCT item_purchased, category FROM customer ORDER BY 2, 1;
