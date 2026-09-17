"""
Main Data Generation Pipeline Orchestrator.
Exports clean relational CSV datasets to data/output/ directory.
"""

import os
import time
import pandas as pd
from data.generators.retail_generator import (
    generate_categories,
    generate_customers,
    generate_employees,
    generate_inventory,
    generate_products,
    generate_stores,
    generate_tenancy,
    generate_warehouses,
)
from data.generators.sales_generator import (
    generate_operating_expenses,
    generate_sales_transactions_and_items,
)


def run_data_generation(output_dir: str = "data/output"):
    """Orchestrate synthetic data generation and export to CSV."""
    start_time = time.time()
    os.makedirs(output_dir, exist_ok=True)
    print(f"=== Starting NovaMart Data Generation (Seed: 42) ===")

    # 1. Tenancy Core
    print("1. Generating Organizations, Workspaces, & Users...")
    orgs, workspaces, users, members = generate_tenancy()

    # 2. Physical Infrastructure
    print("2. Generating Stores & Warehouses...")
    stores = generate_stores()
    warehouses = generate_warehouses()

    # 3. Product Catalog & Inventory
    print("3. Generating Product Categories, Products, & Inventory...")
    categories = generate_categories()
    products = generate_products(categories)
    inventory = generate_inventory(warehouses, products)

    # 4. Human Resources & Customer Directory
    print("4. Generating Employees (200) & Customers (20,000)...")
    employees = generate_employees(stores, warehouses)
    customers = generate_customers(target_count=20000)

    # 5. Business Operations & Financial Transactions
    print("5. Generating 100,000 Sales Transactions & Line Items...")
    transactions, sales_items = generate_sales_transactions_and_items(
        stores, customers, employees, products, target_count=100000
    )

    print("6. Generating Store Operating Expenses...")
    operating_expenses = generate_operating_expenses(stores)

    # Write DataFrames to CSV
    entity_map = {
        "organizations.csv": orgs,
        "workspaces.csv": workspaces,
        "users.csv": users,
        "workspace_members.csv": members,
        "stores.csv": stores,
        "warehouses.csv": warehouses,
        "categories.csv": categories,
        "products.csv": products,
        "inventory.csv": inventory,
        "employees.csv": employees,
        "customers.csv": customers,
        "sales_transactions.csv": transactions,
        "sales_items.csv": sales_items,
        "operating_expenses.csv": operating_expenses,
    }

    print("\n=== Exporting CSV Files to data/output/ ===")
    counts_summary = {}
    for filename, records in entity_map.items():
        filepath = os.path.join(output_dir, filename)
        df = pd.DataFrame(records)
        df.to_csv(filepath, index=False)
        counts_summary[filename] = len(df)
        print(f" Saved {filename:<25} ({len(df):>7,d} rows)")

    elapsed = round(time.time() - start_time, 2)
    print(f"\n[SUCCESS] Data generation complete in {elapsed} seconds.")
    return counts_summary


if __name__ == "__main__":
    run_data_generation()
