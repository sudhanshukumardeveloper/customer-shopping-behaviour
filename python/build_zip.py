import os, zipfile

zip_name = "customer_shopping_behavior_project.zip"
root     = "customer_shopping_behavior_project"

project_files = [
    "README.md",
    "requirements.txt",
    "data/raw/customer_shopping_behavior.csv",
    "data/processed/customer_shopping_behavior_cleaned.csv",
    "python/data_cleaning.py",
    "python/ingest_to_postgres.py",
    "sql/create_tables.sql",
    "sql/data_analysis.sql",
    "sql/business_queries.sql",
    "reports/data_cleaning_report.txt",
]

with zipfile.ZipFile(zip_name, "w", zipfile.ZIP_DEFLATED) as zf:
    for src in project_files:
        if os.path.exists(src):
            zf.write(src, arcname=root + "/" + src)
        else:
            print("MISSING:", src)

print("=== ZIP CONTENTS ===")
total_unc = 0
with zipfile.ZipFile(zip_name, "r") as zf:
    for info in sorted(zf.infolist(), key=lambda x: x.filename):
        label = info.filename.replace(root + "/", "")
        print("  {:<58}  {:>9,} B".format(label, info.file_size))
        total_unc += info.file_size
    print()
    print("  Files inside       : {}".format(len(zf.infolist())))
    print("  Uncompressed total : {:,} bytes  ({:.1f} KB)".format(total_unc, total_unc / 1024))
    zip_size = os.path.getsize(zip_name)
    print("  ZIP file size      : {:,} bytes  ({:.1f} KB)".format(zip_size, zip_size / 1024))
    print("  Saved to           : {}".format(os.path.abspath(zip_name)))
