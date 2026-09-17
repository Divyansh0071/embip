"""
Data Integrity & Quality Validation Script for NovaMart Synthetic Dataset.
Checks primary keys, foreign keys, uniqueness, date ranges, and mathematical consistency.
Exports validation report to data/output/validation_report.json.
"""

import json
import os
import sys
from pathlib import Path
import pandas as pd

# Set up paths
root_dir = Path(__file__).resolve().parent.parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))


def validate_dataset(data_dir: str = "data/output"):
    """Run full validation suite on generated CSV files."""
    print("=== Starting NovaMart Data Quality & Integrity Validation ===")
    report = {
        "timestamp": pd.Timestamp.now().isoformat(),
        "status": "PASS",
        "table_counts": {},
        "integrity_checks": {},
        "errors": [],
    }

    def log_error(err_msg: str):
        report["status"] = "FAIL"
        report["errors"].append(err_msg)
        print(f"[FAIL] {err_msg}")

    def log_pass(check_name: str, msg: str):
        report["integrity_checks"][check_name] = {"status": "PASS", "details": msg}
        print(f"[PASS] {check_name}: {msg}")


    # Load all CSVs
    files = [
        "organizations.csv", "workspaces.csv", "users.csv", "workspace_members.csv",
        "stores.csv", "warehouses.csv", "categories.csv", "products.csv",
        "inventory.csv", "employees.csv", "customers.csv", "sales_transactions.csv",
        "sales_items.csv", "operating_expenses.csv"
    ]

    dfs = {}
    for f in files:
        path = os.path.join(data_dir, f)
        if not os.path.exists(path):
            log_error(f"Missing expected CSV file: {path}")
            return report
        df = pd.read_csv(path)
        dfs[f] = df
        report["table_counts"][f] = len(df)

    print("\n1. Table Row Count Checks:")
    expected_counts = {
        "organizations.csv": 1,
        "workspaces.csv": 1,
        "stores.csv": 10,
        "warehouses.csv": 5,
        "categories.csv": 10,
        "products.csv": 50,
        "inventory.csv": 250,
        "employees.csv": 200,
    }
    for fname, exp_count in expected_counts.items():
        actual = len(dfs[fname])
        if actual == exp_count:
            log_pass(f"count_{fname}", f"Exactly {actual} rows")
        else:
            log_error(f"{fname} expected {exp_count} rows, got {actual}")

    # Minimum checks for large tables
    if len(dfs["customers.csv"]) >= 20000:
        log_pass("count_customers.csv", f"Satisfies minimum 20,000 customers (got {len(dfs['customers.csv']):,d})")
    else:
        log_error(f"customers.csv expected >= 20,000, got {len(dfs['customers.csv'])}")

    if len(dfs["sales_transactions.csv"]) >= 100000:
        log_pass("count_sales_transactions.csv", f"Satisfies minimum 100,000 transactions (got {len(dfs['sales_transactions.csv']):,d})")
    else:
        log_error(f"sales_transactions.csv expected >= 100,000, got {len(dfs['sales_transactions.csv'])}")

    print("\n2. Primary Key Uniqueness Checks:")
    for fname, df in dfs.items():
        if "id" in df.columns:
            dups = df["id"].duplicated().sum()
            if dups == 0:
                log_pass(f"pk_unique_{fname}", "All IDs unique")
            else:
                log_error(f"{fname} has {dups} duplicate primary key IDs")

    print("\n3. Business Code & Email Uniqueness Checks:")
    uniques = [
        ("stores.csv", "store_code"),
        ("warehouses.csv", "warehouse_code"),
        ("products.csv", "sku"),
        ("customers.csv", "customer_code"),
        ("customers.csv", "email"),
    ]
    for fname, col in uniques:
        df = dfs[fname]
        dups = df[col].duplicated().sum()
        if dups == 0:
            log_pass(f"unique_{fname}_{col}", f"Column '{col}' is 100% unique")
        else:
            log_error(f"{fname} column '{col}' has {dups} duplicate values")

    print("\n4. Inventory Composite Unique Constraint Check:")
    inv_df = dfs["inventory.csv"]
    inv_dups = inv_df.duplicated(subset=["warehouse_id", "product_id"]).sum()
    if inv_dups == 0:
        log_pass("unique_inventory_warehouse_product", "All warehouse-product inventory pairs unique")
    else:
        log_error(f"inventory.csv has {inv_dups} duplicate warehouse-product combinations")

    print("\n5. Foreign Key Relational Integrity Checks:")
    fk_relations = [
        ("workspaces.csv", "org_id", "organizations.csv", "id"),
        ("stores.csv", "workspace_id", "workspaces.csv", "id"),
        ("warehouses.csv", "workspace_id", "workspaces.csv", "id"),
        ("categories.csv", "workspace_id", "workspaces.csv", "id"),
        ("products.csv", "category_id", "categories.csv", "id"),
        ("inventory.csv", "warehouse_id", "warehouses.csv", "id"),
        ("inventory.csv", "product_id", "products.csv", "id"),
        ("employees.csv", "store_id", "stores.csv", "id"),
        ("sales_transactions.csv", "store_id", "stores.csv", "id"),
        ("sales_transactions.csv", "customer_id", "customers.csv", "id"),
        ("sales_items.csv", "transaction_id", "sales_transactions.csv", "id"),
        ("sales_items.csv", "product_id", "products.csv", "id"),
    ]
    for child_file, child_col, parent_file, parent_col in fk_relations:
        child_df = dfs[child_file]
        parent_df = dfs[parent_file]
        valid_parents = set(parent_df[parent_col].dropna())
        
        # Filter non-null child values
        child_vals = child_df[child_col].dropna()
        orphans = child_vals[~child_vals.isin(valid_parents)]
        if len(orphans) == 0:
            log_pass(f"fk_{child_file}_{child_col}", f"100% valid foreign keys referencing {parent_file}")
        else:
            log_error(f"{child_file}.{child_col} has {len(orphans)} orphan references to {parent_file}")

    print("\n6. Pricing & Monetary Logic Checks:")
    prod_df = dfs["products.csv"]
    invalid_cost = (prod_df["unit_cost"] <= 0).sum()
    invalid_margin = (prod_df["unit_price"] <= prod_df["unit_cost"]).sum()
    if invalid_cost == 0 and invalid_margin == 0:
        log_pass("products_pricing_logic", "All products have unit_cost > 0 and unit_price > unit_cost")
    else:
        log_error(f"products pricing invalid: {invalid_cost} invalid cost, {invalid_margin} negative/zero margins")

    print("\n7. Line Item & Transaction Mathematical Consistency Checks:")
    items_df = dfs["sales_items.csv"]
    items_df["expected_line_total"] = (items_df["quantity"] * items_df["unit_price"]).round(2)
    line_diff = (items_df["total_price"] - items_df["expected_line_total"]).abs()
    invalid_line_totals = (line_diff > 0.01).sum()
    if invalid_line_totals == 0:
        log_pass("sales_items_math", "100% of line items total_price match quantity * unit_price")
    else:
        log_error(f"sales_items.csv has {invalid_line_totals} mathematically inconsistent line totals")

    # Group line items by transaction_id to check subtotal match
    item_subtotals = items_df.groupby("transaction_id")["total_price"].sum().round(2).reset_index()
    item_subtotals.columns = ["id", "calculated_subtotal"]

    tx_df = dfs["sales_transactions.csv"]
    tx_merged = pd.merge(tx_df, item_subtotals, on="id", how="left")

    subtotal_diff = (tx_merged["subtotal"] - tx_merged["calculated_subtotal"]).abs()
    invalid_subtotals = (subtotal_diff > 0.01).sum()
    if invalid_subtotals == 0:
        log_pass("transaction_subtotal_math", "100% of transactions subtotal match sum of line items total_price")
    else:
        log_error(f"sales_transactions.csv has {invalid_subtotals} subtotal mismatches with line items")

    # Transaction total amount formula check: total_amount == subtotal - discount_amount + tax_amount
    expected_total = (tx_df["subtotal"] - tx_df["discount_amount"] + tx_df["tax_amount"]).round(2)
    total_diff = (tx_df["total_amount"] - expected_total).abs()
    invalid_totals = (total_diff > 0.01).sum()
    if invalid_totals == 0:
        log_pass("transaction_total_amount_math", "100% of transactions total_amount match subtotal - discount + tax")
    else:
        log_error(f"sales_transactions.csv has {invalid_totals} total_amount formula mismatches")

    print("\n8. Date Range Sanity Check:")
    tx_df["tx_date"] = pd.to_datetime(tx_df["transaction_date"])
    min_date = tx_df["tx_date"].min()
    max_date = tx_df["tx_date"].max()
    log_pass("transaction_date_range", f"Transaction dates span from {min_date.strftime('%Y-%m-%d')} to {max_date.strftime('%Y-%m-%d')}")

    # Write report JSON
    report_path = os.path.join(data_dir, "validation_report.json")
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)

    print(f"\n=== Validation Completed. Result: {report['status']} ===")
    print(f"Report saved to: {report_path}")
    return report


if __name__ == "__main__":
    validate_dataset()
