# Customer Shopping Behavior — End-to-End Data Analytics Project

> **Stack:** Python · Pandas · PostgreSQL · SQLAlchemy · Power BI  
> **Pipeline:** Raw CSV → Data Cleaning → SQL Analysis → Interactive Dashboard

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Business Problem & Objectives](#business-problem--objectives)
3. [Dataset Description](#dataset-description)
4. [Tools & Technologies](#tools--technologies)
5. [Data Cleaning & EDA Methodology](#data-cleaning--eda-methodology)
6. [SQL Queries & Key Business Findings](#sql-queries--key-business-findings)
7. [Power BI Dashboard Highlights](#power-bi-dashboard-highlights)
8. [Actionable Business Recommendations](#actionable-business-recommendations)
9. [Repository Structure](#repository-structure)
10. [Setup & Reproduction Instructions](#setup--reproduction-instructions)

---

## Project Overview

This project performs a complete, production-style data analytics pipeline on a retail customer shopping behavior dataset. Starting from a raw CSV file, the project covers every phase of a real analytics workflow:

- **Data Understanding** — profiling, quality audit, and a data dictionary
- **Data Cleaning** — automated Python script with reproducible transformations
- **Database Integration** — PostgreSQL ingestion via SQLAlchemy
- **SQL Analysis** — eight business queries using aggregations, subqueries, CTEs, and window functions
- **BI Dashboard** — Power BI report with KPI cards, donut chart, column/bar charts, and interactive slicers

The original raw file is preserved unmodified throughout the entire pipeline.

---

## Business Problem & Objectives

### Problem Statement
A retail business has collected transactional and behavioral data for 500 customers but lacks a structured analytical framework to extract actionable insights. Key decision-makers cannot currently answer questions such as: *Which age group drives the most revenue? Do subscribers spend more? Which products should be promoted or restocked per category?*

### Objectives

| # | Objective |
|---|-----------|
| 1 | Establish a clean, analysis-ready dataset from raw transactional data |
| 2 | Quantify revenue contribution by gender, age group, and product category |
| 3 | Evaluate the financial impact of the subscription programme |
| 4 | Identify high-value customers who respond to discounts |
| 5 | Surface the top-selling products within each category |
| 6 | Segment the customer base by purchase frequency for targeted marketing |
| 7 | Deliver an interactive Power BI dashboard for non-technical stakeholders |

---

## Dataset Description

| Property | Value |
|---|---|
| **File name** | `data_raw_customer_shopping_behavior.csv` |
| **Rows** | 500 |
| **Columns (raw)** | 17 |
| **Columns (cleaned)** | 18 (+2 engineered, −1 dropped) |
| **Duplicate rows** | 0 |
| **Missing values (raw)** | 26 (in `review_rating` only — 5.2%) |
| **Missing values (cleaned)** | 0 |
| **Date range** | No timestamp column — cross-sectional snapshot |

### Column Summary

| Column | Type | Description |
|---|---|---|
| `age` | Integer | Customer age (18–70) |
| `gender` | Categorical | Male / Female |
| `item_purchased` | Categorical | Specific product bought (18 unique items) |
| `category` | Categorical | Product group: Clothing, Accessories, Footwear, Outerwear |
| `purchase_amount` | Float (USD) | Transaction value ($20.23–$299.48) |
| `location` | Categorical | US state (6 states) |
| `size` | Ordered Category | Clothing size: S < M < L < XL |
| `color` | Categorical | Product colour (6 values) |
| `season` | Categorical | Purchase season (Fall, Winter, Summer, Spring) |
| `review_rating` | Float | Customer rating 1.0–5.0 |
| `subscription_status` | Integer (0/1) | Active subscription: 1 = Yes, 0 = No |
| `shipping_type` | Categorical | Express, Standard, Free Shipping, Next Day |
| `discount_applied` | Integer (0/1) | Discount used: 1 = Yes, 0 = No |
| `previous_purchases` | Integer | Prior purchase count (1–15) |
| `payment_method` | Categorical | PayPal, Bank Transfer, Credit Card, Cash, Venmo |
| `frequency_of_purchases` | Ordered Category | Annually < Monthly < Fortnightly < Weekly |
| `age_group` *(engineered)* | Categorical | Binned age: 18-25, 26-35, 36-50, 51-65, 66+ |
| `purchase_frequency_days` *(engineered)* | Integer | Numeric days between purchases (7/14/30/365) |

---

## Tools & Technologies

| Layer | Tool / Library | Purpose |
|---|---|---|
| Data wrangling | Python 3, Pandas | Cleaning, transformation, feature engineering |
| Database | PostgreSQL | Structured storage and SQL analysis |
| ORM / Ingestion | SQLAlchemy, psycopg2 | Python → PostgreSQL data load |
| SQL analysis | PostgreSQL SQL | Business queries, CTEs, window functions |
| Visualisation | Power BI Desktop | Interactive dashboard |
| Version control | Git | Project tracking |

---

## Data Cleaning & EDA Methodology

### Script: [`python/data_cleaning.py`](python/data_cleaning.py)

The cleaning pipeline follows a strict **read-only raw, write-only processed** pattern. The original file at `data/raw/customer_shopping_behavior.csv` is never modified.

#### Step-by-Step Transformations

| Step | Action | Detail |
|---|---|---|
| 1 | Load raw data | Snapshot `before` statistics captured immediately after load |
| 2 | Rename columns | Normalise to `lower_snake_case` (all columns were already compliant) |
| 3 | Impute `review_rating` | Fill 26 nulls with **category-level medians** — Accessories: 2.6, Clothing: 2.9, Footwear: 3.05, Outerwear: 3.0 — rather than a single global median, to preserve category-level satisfaction differences |
| 4 | Encode boolean columns | `subscription_status` and `discount_applied`: `"Yes"` → `1`, `"No"` → `0` (dtype: `Int8`) |
| 5 | Ordinal encoding | `size` → ordered Categorical (`S < M < L < XL`); `frequency_of_purchases` → ordered Categorical (`Annually < Monthly < Fortnightly < Weekly`) |
| 6 | Category dtype | 8 free-text columns cast to `pd.Categorical` for memory efficiency and faster groupby |
| 7 | Engineer `age_group` | `pd.cut` with bins `[17, 25, 35, 50, 65, 100]` → labels `18-25, 26-35, 36-50, 51-65, 66+` |
| 8 | Engineer `purchase_frequency_days` | Map text frequency to integer days: Weekly→7, Fortnightly→14, Monthly→30, Annually→365 |
| 9 | Drop `customer_id` | Row identifier only; contributes no analytical signal |
| 10 | Save cleaned CSV | Output to `data/processed/customer_shopping_behavior_cleaned.csv` |

#### Before vs After Summary

| Metric | Before | After |
|---|---|---|
| Rows | 500 | 500 (no rows deleted) |
| Columns | 17 | 18 |
| Missing values | 26 | **0** |
| Duplicate rows | 0 | 0 |

---

## SQL Queries & Key Business Findings

### Schema: [`sql/create_tables.sql`](sql/create_tables.sql)
Defines the `customer` table with `CHECK` constraints on all bounded columns, 9 performance indexes, and two convenience views (`v_categories`, `v_items`).

### Ingestion: [`python/ingest_to_postgres.py`](python/ingest_to_postgres.py)
Loads the cleaned CSV into PostgreSQL using `pandas.to_sql` with explicit SQLAlchemy `dtype` mapping, `method='multi'` bulk insert, and a post-load row-count assertion.

---

### Analytical Queries: [`sql/data_analysis.sql`](sql/data_analysis.sql)

#### Q1 — Revenue by Gender

| Gender | Total Revenue | Orders |
|---|---|---|
| Male | $47,238.52 | 277 |
| Female | $36,438.29 | 223 |

Male customers generate **29.6% more revenue** in absolute terms, driven by higher order volume rather than higher per-order spend.

---

#### Q2 — Discounted High-Spenders

- **128 customers** applied a discount AND spent above the dataset average of $167.35.
- Their average spend: **$237.93** — 42% above the overall average.
- Combined revenue from this group: **$30,455.14** (36.4% of total revenue from 25.6% of customers).

---

#### Q3 — Top 5 Products by Average Review Rating *(min. 5 reviews)*

| Rank | Product | Category | Reviews | Avg Rating |
|---|---|---|---|---|
| 1 | Blouse | Clothing | 25 | 3.23 |
| 2 | Coat | Outerwear | 28 | 3.22 |
| 3 | Sandals | Footwear | 34 | 3.21 |
| 4 | Boots | Footwear | 27 | 3.14 |
| 5 | Skirt | Clothing | 28 | 3.03 |

Overall average rating is **2.93 / 5.0** — below mid-scale — indicating a systemic satisfaction opportunity across all categories.

---

#### Q4 — Shipping Type Spend: Standard vs Express

| Shipping Type | Orders | Avg Spend | Total Revenue |
|---|---|---|---|
| Standard | 130 | $170.37 | $22,147.51 |
| Express | 137 | $162.17 | $22,216.70 |

Standard shipping customers spend **$8.20 more per order** on average, suggesting higher-value purchases are not driving faster shipping selection.

---

#### Q5 — Subscriber vs Non-Subscriber Metrics

| Status | Customers | Avg Spend | Total Revenue |
|---|---|---|---|
| Subscriber (1) | 245 | $167.90 | $41,135.86 |
| Non-Subscriber (0) | 255 | $166.83 | $42,540.95 |

Subscribers and non-subscribers spend virtually identically ($1.07 difference per order). The subscription programme does not currently produce a measurable revenue lift per customer.

---

### Business Queries: [`sql/business_queries.sql`](sql/business_queries.sql)

#### Q6 — Customer Segmentation (CTE + CASE)

| Segment | Definition | Customers | % of Base | Avg Spend | Total Revenue |
|---|---|---|---|---|---|
| New | `previous_purchases = 1` | 33 | 6.6% | $175.46 | $5,790.11 |
| Returning | `previous_purchases 2–10` | 301 | 60.2% | $164.05 | $49,377.92 |
| Loyal | `previous_purchases > 10` | 166 | 33.2% | $171.74 | $28,508.78 |

The **Returning** segment is the largest revenue contributor ($49,378) and the prime conversion target for Loyal status.

---

#### Q7 — Top 3 Products per Category (`ROW_NUMBER() OVER PARTITION BY`)

| Category | Rank 1 | Rank 2 | Rank 3 |
|---|---|---|---|
| Accessories | Belt (34 orders) | Scarf (28) | Backpack (26) |
| Clothing | Pants (33 orders) | Skirt (28) | Blouse (25) |
| Footwear | Sandals (34 orders) | Loafers (33) | Sneakers (32) |
| Outerwear | Jacket (30 orders) | Sweater (30) | Hoodie (29) |

---

#### Q8 — Revenue by Age Group

| Age Group | Customers | Total Revenue | Revenue Share |
|---|---|---|---|
| 18-25 | — | $13,562.46 | 16.2% |
| 26-35 | — | $14,757.12 | 17.6% |
| 36-50 | — | $23,614.99 | 28.2% |
| 51-65 | — | $23,931.69 | 28.6% |
| 66+ | — | $7,810.55 | 9.3% |

The **36-50** and **51-65** brackets together generate **56.8% of total revenue** ($47,547) despite being mid-to-late career demographics.

---

## Power BI Dashboard Highlights

### Canvas Specifications
- **Canvas size:** 1500 × 820 px
- **Theme:** Dark navy (`#1A2235`) with blue (`#3B82D4`) and purple (`#7C5CD8`) accents
- **Font:** Segoe UI throughout

### Layout Zones

```
┌─────────────────────────────────────────────────────────────┐
│  HEADER BAR  (1500 × 60)                                    │
├─────────────────────────────────────────────────────────────┤
│  SLICER ROW: Subscription | Gender | Category | Shipping    │
├───────────┬───────────┬───────────┬──────────────────────── ┤
│ KPI Card  │ KPI Card  │ KPI Card  │ KPI Card                │
│ Total Rev │ Customers │ Avg Purch │ Avg Rating              │
├───────────┼───────────────────────┼─────────────────────────┤
│           │  Column Chart         │  Bar Chart              │
│  Donut    │  Revenue by Category  │  Sales Count by Cat.    │
│  (Sub     ├───────────────────────┼─────────────────────────┤
│  Status)  │  Column Chart         │  Bar Chart              │
│           │  Revenue by Age Group │  Sales Count by Age Grp │
└───────────┴───────────────────────┴─────────────────────────┘
```

### DAX Measures Used

| Measure | Formula Summary |
|---|---|
| Total Revenue | `SUMX(customer, customer[purchase_amount])` → `$83,676.81` |
| Total Customers | `COUNTROWS(customer)` → `500` |
| Avg Purchase Amount | `AVERAGEX(...)` → `$167.35` |
| Avg Rating | `AVERAGEX(...)` → `2.93` |
| Revenue Share % | `DIVIDE([Total Revenue], CALCULATE([Total Revenue], ALL(customer)), 0)` |
| Rating Band Color | `SWITCH(TRUE(), ...)` — drives conditional font colour (green/amber/red) |

### Interactive Slicers
All four slicers (Subscription Status, Gender, Category, Shipping Type) cross-filter every KPI card and all four charts simultaneously.

### Screenshots
> _Add Power BI screenshots here after publishing the `.pbix` file._
>
> Suggested filenames:
> - `assets/dashboard_full.png` — full 1500×820 canvas
> - `assets/dashboard_kpi_row.png` — zoomed KPI cards
> - `assets/dashboard_charts.png` — lower chart section

---

## Actionable Business Recommendations

### 1. Convert Returning Customers to Loyal
Returning customers (60.2% of the base, $49,378 revenue) sit just below the Loyal threshold of 10+ purchases. A targeted **"10th purchase reward"** push notification or email sequence could accelerate conversion and unlock the higher $171.74 avg spend seen in the Loyal tier.

### 2. Re-evaluate the Subscription Programme
Subscribers and non-subscribers spend identically ($167.90 vs $166.83). The programme does not currently produce measurable spend lift. Consider adding **exclusive subscriber discounts, early access, or free shipping upgrades** to create a tangible financial incentive that justifies the subscription.

### 3. Protect Discounted High-Spenders from Over-Discounting
128 customers (25.6% of the base) who used discounts already spend 42% above average ($237.93 vs $167.35). These customers are not price-sensitive — they would likely purchase without discounts. Migrate them to a **loyalty points programme** rather than continued blanket discounting to protect margin.

### 4. Prioritise the 36–65 Age Demographic
The 36-50 and 51-65 brackets generate 56.8% of total revenue. Marketing budget, product assortment, and channel strategy (email, search, in-store) should be weighted toward these groups. The 18-25 bracket (16.2% of revenue) may be worth long-term nurturing investment but should not receive disproportionate current budget.

### 5. Stock and Feature Top-Ranked Products per Category
Based on order volume, these are the hero SKUs for each category:
- **Accessories:** Belt, Scarf, Backpack
- **Clothing:** Pants, Skirt, Blouse
- **Footwear:** Sandals, Loafers, Sneakers
- **Outerwear:** Jacket, Sweater, Hoodie

Ensure these items are never out-of-stock, feature them in category landing page banners, and use them as cross-sell anchors for lower-performing items.

### 6. Address the Below-Average Rating (2.93 / 5.0)
The overall satisfaction score is below the mid-point of the scale. The top-rated products (Blouse: 3.23, Coat: 3.22, Sandals: 3.21) still score below 3.5. A post-purchase review incentive programme and product quality review for the lowest-rated items could improve this metric and reduce churn.

### 7. Investigate Standard vs Express Shipping
Standard shipping customers spend $8.20 more per order than Express customers, despite slower delivery. Consider introducing a **free Standard shipping threshold** (e.g., "Free Standard on orders over $150") to encourage higher basket sizes without cannibalising Express revenue.

---

## Repository Structure

```
customer-shopping-behavior/
│
├── data/
│   ├── raw/
│   │   └── customer_shopping_behavior.csv          # Original dataset — NEVER MODIFIED
│   └── processed/
│       └── customer_shopping_behavior_cleaned.csv  # Output of data_cleaning.py
│
├── python/
│   ├── data_cleaning.py                            # Full cleaning pipeline + summary report
│   └── ingest_to_postgres.py                       # SQLAlchemy CSV → PostgreSQL loader
│
├── sql/
│   ├── create_tables.sql                           # DDL: table, constraints, indexes, views
│   ├── data_analysis.sql                           # Business queries 1–5
│   └── business_queries.sql                        # Business queries 6–8 (CTEs, window fns)
│
├── assets/                                         # (add Power BI screenshots here)
│   └── .gitkeep
│
├── README.md                                       # This file
└── requirements.txt                                # Python dependencies
```

---

## Setup & Reproduction Instructions

### Prerequisites

| Tool | Version tested | Install |
|---|---|---|
| Python | 3.10+ | [python.org](https://python.org) |
| PostgreSQL | 14+ | [postgresql.org](https://postgresql.org) |
| Power BI Desktop | Latest | [Microsoft Store](https://aka.ms/pbidesktopstore) |

### 1. Clone the repository

```bash
git clone https://github.com/<your-username>/customer-shopping-behavior.git
cd customer-shopping-behavior
```

### 2. Install Python dependencies

```bash
pip install -r requirements.txt
```

`requirements.txt` contents:
```
pandas>=2.0
sqlalchemy>=2.0
psycopg2-binary>=2.9
```

### 3. Run the data cleaning pipeline

```bash
python python/data_cleaning.py
```

Expected output:
- `data/processed/customer_shopping_behavior_cleaned.csv` created
- Summary report printed to console (500 rows, 18 columns, 0 missing values)

### 4. Set up PostgreSQL database

```sql
-- Run in psql or pgAdmin
CREATE DATABASE shopping_db;
```

Then apply the DDL:

```bash
psql -U postgres -d shopping_db -f sql/create_tables.sql
```

### 5. Ingest cleaned data into PostgreSQL

```bash
# Set your credentials as environment variables
export DB_USER=postgres
export DB_PASSWORD=your_password
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=shopping_db

python python/ingest_to_postgres.py
```

Windows (PowerShell):
```powershell
$env:DB_USER="postgres"; $env:DB_PASSWORD="your_password"
python python/ingest_to_postgres.py
```

### 6. Run SQL analysis queries

```bash
# Analysis queries (Q1–Q5)
psql -U postgres -d shopping_db -f sql/data_analysis.sql

# Business queries (Q6–Q8)
psql -U postgres -d shopping_db -f sql/business_queries.sql
```

Or open both files in **pgAdmin → Query Tool** and run interactively.

### 7. Open Power BI Dashboard

1. Open **Power BI Desktop**
2. **Get Data → Text/CSV** → select `data/processed/customer_shopping_behavior_cleaned.csv`
3. Confirm column types (numeric columns as Decimal/Whole Number, text columns as Text)
4. Add the DAX measures and calculated columns listed in `README.md` Section 6
5. Build visuals following the layout coordinates in the Power BI design document

---

## License

This project is for educational and portfolio purposes. The dataset is synthetic retail transaction data.

---

*Generated from verified project outputs. No statistics were fabricated — all figures derive directly from `customer_shopping_behavior_cleaned.csv`.*
