"""
data_cleaning.py
================
Data cleaning stage for the Customer Shopping Behavior dataset.

Input  : data/raw/customer_shopping_behavior.csv   (never modified)
Output : data/processed/customer_shopping_behavior_cleaned.csv

Steps
-----
1.  Load raw data and snapshot "before" statistics
2.  Rename columns to lower_snake_case
3.  Impute missing review_rating with category-level medians
4.  Encode boolean Yes/No columns as integers (1 / 0)
5.  Apply ordinal encoding to `size` and `purchase_frequency`
6.  Cast remaining string columns to pandas Categorical dtype
7.  Engineer age_group (binned) feature
8.  Engineer purchase_frequency_days (numeric) feature
9.  Drop redundant columns with justification
10. Save cleaned CSV
11. Print before/after summary report
"""

import os
import pandas as pd

# ── Paths ──────────────────────────────────────────────────────────────────
RAW_PATH     = os.path.join("data", "raw", "customer_shopping_behavior.csv")
CLEANED_PATH = os.path.join("data", "processed", "customer_shopping_behavior_cleaned.csv")

os.makedirs(os.path.dirname(CLEANED_PATH), exist_ok=True)

# ── 1. Load ────────────────────────────────────────────────────────────────
raw = pd.read_csv(RAW_PATH)
df  = raw.copy()          # work on copy; raw is never touched

# ── Snapshot: BEFORE ──────────────────────────────────────────────────────
before_rows    = len(df)
before_cols    = df.shape[1]
before_missing = df.isnull().sum()
before_dtypes  = df.dtypes.copy()

# ── 2. Rename columns → lower_snake_case ──────────────────────────────────
# All columns are already lowercase; just normalise spaces/dashes if any.
df.columns = (
    df.columns
    .str.strip()
    .str.lower()
    .str.replace(r"[\s\-]+", "_", regex=True)
)

# ── 3. Impute missing review_rating with category-level medians ───────────
# Why category-level? Products vary in satisfaction. Using the median per
# product category gives a better estimate than a single global median.
cat_medians = df.groupby("category")["review_rating"].transform("median")
df["review_rating"] = df["review_rating"].fillna(cat_medians)

# ── 4. Encode boolean Yes/No columns → 1 / 0 ─────────────────────────────
bool_cols = ["subscription_status", "discount_applied"]
for col in bool_cols:
    df[col] = df[col].map({"Yes": 1, "No": 0}).astype("Int8")

# ── 5. Ordinal encoding ───────────────────────────────────────────────────
# size: natural clothing order S < M < L < XL
size_order = {"S": 0, "M": 1, "L": 2, "XL": 3}
df["size_encoded"] = df["size"].map(size_order).astype("Int8")

# frequency_of_purchases: least → most frequent
freq_order = {"Annually": 0, "Monthly": 1, "Fortnightly": 2, "Weekly": 3}
df["purchase_frequency_encoded"] = df["frequency_of_purchases"].map(freq_order).astype("Int8")

# ── 6. Cast string columns to Categorical dtype ───────────────────────────
cat_cols = [
    "gender", "item_purchased", "category", "location",
    "color", "season", "shipping_type", "payment_method",
]
for col in cat_cols:
    df[col] = df[col].astype("category")

# Ordered categoricals (for proper sort/comparison behaviour)
from pandas.api.types import CategoricalDtype

size_dtype = CategoricalDtype(categories=["S", "M", "L", "XL"], ordered=True)
df["size"] = df["size"].astype(size_dtype)

freq_dtype = CategoricalDtype(
    categories=["Annually", "Monthly", "Fortnightly", "Weekly"], ordered=True
)
df["frequency_of_purchases"] = df["frequency_of_purchases"].astype(freq_dtype)

# ── 7. Engineer: age_group ────────────────────────────────────────────────
# Bins align with common retail customer segments.
# 18–25 = Young Adults, 26–35 = Early Career, 36–50 = Mid-Career,
# 51–65 = Pre-Retirement, 66+ = Seniors
df["age_group"] = pd.cut(
    df["age"],
    bins=[17, 25, 35, 50, 65, 100],
    labels=["18-25", "26-35", "36-50", "51-65", "66+"],
).astype("category")

# ── 8. Engineer: purchase_frequency_days ─────────────────────────────────
# Converts the text frequency into an approximate number of days between
# purchases. Useful for numeric models and sorting/aggregation.
freq_days_map = {
    "Weekly":      7,
    "Fortnightly": 14,
    "Monthly":     30,
    "Annually":    365,
}
df["purchase_frequency_days"] = df["frequency_of_purchases"].map(freq_days_map).astype("Int16")

# ── 9. Drop redundant columns (with justification) ────────────────────────
# customer_id  → Acts only as a row identifier; contributes no analytical
#                signal; index already uniquely identifies rows.
#
# size_encoded / purchase_frequency_encoded → These were intermediate helper
#                columns. The ordered Categorical columns (size,
#                frequency_of_purchases) already carry the ordering
#                information for pandas operations. purchase_frequency_days
#                provides the numeric representation for ML/models.
#                Keeping both the raw label AND a separate int column avoids
#                confusion; drop the raw integer-only intermediates.

REDUNDANT = ["customer_id", "size_encoded", "purchase_frequency_encoded"]
df.drop(columns=REDUNDANT, inplace=True)

# ── 10. Save cleaned CSV ──────────────────────────────────────────────────
df.to_csv(CLEANED_PATH, index=False)

# ── 11. Print Before / After Summary Report ───────────────────────────────
after_rows    = len(df)
after_cols    = df.shape[1]
after_missing = df.isnull().sum()
after_dtypes  = df.dtypes.copy()

SEP = "=" * 70

print(SEP)
print("  CUSTOMER SHOPPING BEHAVIOR - DATA CLEANING SUMMARY REPORT")
print(SEP)

print("\n>> FILES")
print(f"  Raw input  : {RAW_PATH}")
print(f"  Cleaned out: {CLEANED_PATH}")

print("\n>> SHAPE")
print(f"  {'Metric':<20} {'Before':>10} {'After':>10}")
print(f"  {'-'*20} {'-'*10} {'-'*10}")
print(f"  {'Rows':<20} {before_rows:>10} {after_rows:>10}")
print(f"  {'Columns':<20} {before_cols:>10} {after_cols:>10}")

print("\n-- MISSING VALUES")
all_cols = sorted(set(before_missing.index) | set(after_missing.index))
print(f"  {'Column':<30} {'Before':>8} {'After':>8}")
print(f"  {'-'*30} {'-'*8} {'-'*8}")
for col in all_cols:
    b = before_missing.get(col, 0)
    a = after_missing.get(col, 0)
    flag = " [fixed]" if b > 0 and a == 0 else ""
    if b > 0 or a > 0:
        print(f"  {col:<30} {int(b):>8} {int(a):>8}{flag}")
total_before = int(before_missing.sum())
total_after  = int(after_missing.sum())
print(f"  {'TOTAL':<30} {total_before:>8} {total_after:>8}")

print("\n>> DATA TYPES  (After Cleaning)")
print(f"  {'Column':<30} {'Dtype'}")
print(f"  {'-'*30} {'-'*30}")
for col, dtype in after_dtypes.items():
    print(f"  {col:<30} {dtype}")

print("\n-- DROPPED COLUMNS & JUSTIFICATION")
justifications = {
    "customer_id":               "Row identifier only - no analytical value",
    "size_encoded":              "Redundant - size column is now an ordered Categorical",
    "purchase_frequency_encoded":"Redundant - purchase_frequency_days gives numeric form",
}
for col, reason in justifications.items():
    print(f"  - {col:<32} {reason}")

print("\n++ NEW / ENGINEERED COLUMNS")
new_cols = {
    "age_group":               "Binned age: 18-25, 26-35, 36-50, 51-65, 66+",
    "purchase_frequency_days": "Numeric days between purchases (7/14/30/365)",
}
for col, desc in new_cols.items():
    print(f"  - {col:<32} {desc}")

print("\n** ENCODING CHANGES")
print("  - subscription_status  : Yes/No  -> 1/0  (Int8)")
print("  - discount_applied     : Yes/No  -> 1/0  (Int8)")
print("  - size                 : string  -> Ordered Categorical (S<M<L<XL)")
print("  - frequency_of_purchases: string -> Ordered Categorical (Annually<Monthly<Fortnightly<Weekly)")
print("  - 8 string columns     : string  -> Categorical dtype")

print(f"\n{SEP}")
print("  Cleaning complete. Raw file is UNCHANGED.")
print(SEP)
