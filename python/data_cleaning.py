"""Data cleaning pipeline for the Customer Shopping Behavior dataset.

Input : data/raw/customer_shopping_behavior.csv
Output: data/processed/customer_shopping_behavior_cleaned.csv

The raw file is never modified. The pipeline validates the customer identifier,
handles missing ratings, normalizes categorical fields, engineers analytical
features, and writes a reproducible analysis-ready dataset.
"""

import os
import pandas as pd
from pandas.api.types import CategoricalDtype

RAW_PATH = os.path.join("data", "raw", "customer_shopping_behavior.csv")
CLEANED_PATH = os.path.join("data", "processed", "customer_shopping_behavior_cleaned.csv")

os.makedirs(os.path.dirname(CLEANED_PATH), exist_ok=True)

# 1. Load raw data and capture baseline quality metrics
raw = pd.read_csv(RAW_PATH)
df = raw.copy()

before_rows, before_cols = df.shape
before_missing = df.isnull().sum()
before_duplicates = int(df.duplicated().sum())

# Basic integrity checks
required_columns = [
    "customer_id", "age", "gender", "item_purchased", "category",
    "purchase_amount", "location", "size", "color", "season",
    "review_rating", "subscription_status", "shipping_type",
    "discount_applied", "previous_purchases", "payment_method",
    "frequency_of_purchases",
]
missing_required = sorted(set(required_columns) - set(df.columns))
if missing_required:
    raise ValueError(f"Missing required columns: {missing_required}")

if df["customer_id"].isna().any() or not df["customer_id"].is_unique:
    raise ValueError("customer_id must be present and unique.")

# 2. Normalize column names
df.columns = (
    df.columns.str.strip().str.lower()
    .str.replace(r"[\s\-]+", "_", regex=True)
)

# 3. Impute review_rating
# Prefer the median within each product category; use the global median only
# as a safety fallback if an entire category has missing ratings.
category_medians = df.groupby("category", observed=True)["review_rating"].transform("median")
df["review_rating"] = (
    df["review_rating"]
    .fillna(category_medians)
    .fillna(df["review_rating"].median())
)

# 4. Encode Yes/No flags with validation
for col in ["subscription_status", "discount_applied"]:
    unknown = sorted(set(df[col].dropna().unique()) - {"Yes", "No"})
    if unknown:
        raise ValueError(f"Unexpected values in {col}: {unknown}")
    df[col] = df[col].map({"Yes": 1, "No": 0}).astype("Int8")

# 5. Ordered categorical fields
size_dtype = CategoricalDtype(categories=["S", "M", "L", "XL"], ordered=True)
freq_dtype = CategoricalDtype(
    categories=["Annually", "Monthly", "Fortnightly", "Weekly"],
    ordered=True,
)

df["size"] = df["size"].astype(size_dtype)
df["frequency_of_purchases"] = df["frequency_of_purchases"].astype(freq_dtype)

# 6. Other categorical fields
cat_cols = [
    "gender", "item_purchased", "category", "location",
    "color", "season", "shipping_type", "payment_method",
]
for col in cat_cols:
    df[col] = df[col].astype("category")

# 7. Engineer age_group
df["age_group"] = pd.cut(
    df["age"],
    bins=[17, 25, 35, 50, 65, 100],
    labels=["18-25", "26-35", "36-50", "51-65", "66+"],
    include_lowest=True,
).astype("category")

# 8. Engineer purchase_frequency_days
freq_days_map = {
    "Weekly": 7,
    "Fortnightly": 14,
    "Monthly": 30,
    "Annually": 365,
}
df["purchase_frequency_days"] = (
    df["frequency_of_purchases"].map(freq_days_map).astype("Int16")
)

# 9. Final validation
if df["review_rating"].isna().any():
    raise ValueError("review_rating still contains missing values after imputation.")
if not df["age"].between(18, 120).all():
    raise ValueError("age contains values outside the supported 18–120 range.")
if (df["purchase_amount"] < 0).any():
    raise ValueError("purchase_amount contains negative values.")
if not df["review_rating"].between(1.0, 5.0).all():
    raise ValueError("review_rating contains values outside 1.0–5.0.")

# Keep customer_id: it is the unique row/customer key and supports traceability.
# No analytical feature is discarded here.
df.to_csv(CLEANED_PATH, index=False)

# 10. Console quality report
after_rows, after_cols = df.shape
after_missing = df.isnull().sum()

SEP = "=" * 70
print(SEP)
print("  CUSTOMER SHOPPING BEHAVIOR - DATA CLEANING SUMMARY REPORT")
print(SEP)
print(f"\nRaw input   : {RAW_PATH}")
print(f"Cleaned out : {CLEANED_PATH}")
print(f"Rows        : {before_rows} -> {after_rows}")
print(f"Columns     : {before_cols} -> {after_cols}")
print(f"Duplicate rows (raw): {before_duplicates}")
print(f"Missing values      : {int(before_missing.sum())} -> {int(after_missing.sum())}")
print("\nTransformations:")
print("  - Normalized column names to lower_snake_case")
print("  - Imputed review_rating using category median with global fallback")
print("  - Encoded subscription_status and discount_applied: Yes/No -> 1/0")
print("  - Preserved customer_id as the unique record key")
print("  - Set ordered categoricals for size and purchase frequency")
print("  - Engineered age_group and purchase_frequency_days")
print("\nCleaning complete. Raw file is UNCHANGED.")
print(SEP)
