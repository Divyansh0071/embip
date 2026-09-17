# NovaMart Retail Solutions — Demo Dataset (`data/`)

This directory contains the synthetic dataset generation, quality validation, database seeding pipelines, and CSV files for **NovaMart Retail Solutions** (Phase 5).

---

## 1. Company & Tenant Profile

* **Company Name:** NovaMart Retail Solutions
* **Industry:** Retail & E-Commerce (Multi-Category Omnichannel Retailer)
* **Isolated Tenant Organization ID:** `00000000-0000-4000-a000-000000000001`
* **Isolated Tenant Workspace ID:** `00000000-0000-4000-a000-000000000002`
* **Demo Admin User:** `demo.admin@novamart.com` (`00000000-0000-4000-a000-000000000003`)
* **Historical Timeline:** 3 Full Years (`2023-10-01` to `2026-09-18`)
* **Deterministic Random Seed:** `42`

---

## 2. Dataset Entity Summary & Record Counts

| CSV File | Entity Description | Record Count | Unique Identifiers / Constraints |
| :--- | :--- | :---: | :--- |
| `organizations.csv` | Tenant Organization | **1** | Primary Key UUID |
| `workspaces.csv` | Tenant Workspace | **1** | Primary Key UUID |
| `users.csv` | Demo User Profile | **1** | Unique Email |
| `workspace_members.csv` | Workspace RBAC Membership | **1** | Unique `(workspace_id, user_id)` |
| `stores.csv` | Retail Stores | **10** | Unique `store_code` |
| `warehouses.csv` | Fulfillment Warehouses | **5** | Unique `warehouse_code` |
| `categories.csv` | Product Categories | **10** | Unique Category Names |
| `products.csv` | Product Catalog | **50** | Unique `sku`, Unit Cost < Unit Price |
| `inventory.csv` | Warehouse Stock | **250** | Unique `(warehouse_id, product_id)` |
| `employees.csv` | Store & Warehouse Staff | **200** | Unique Employee UUIDs |
| `customers.csv` | Customer Directory | **20,000** | Unique `customer_code`, Unique `email` |
| `sales_transactions.csv` | Sales Transactions | **100,000** | Subtotal, Discount, Tax, & Total Math Validated |
| `sales_items.csv` | Transaction Line Items | **193,416** | 100% Mathematically Consistent Line Totals |
| `operating_expenses.csv` | Monthly Store Overhead | **1,800** | 36 Months x 5 Overhead Categories x 10 Stores |

---

## 3. Directory Layout

```
data/
├── generators/
│   ├── config.py             # Constants, seed=42, date ranges, stores, categories
│   ├── retail_generator.py   # Stores, Warehouses, Products, Inventory, Customers, Employees
│   ├── sales_generator.py    # Transactions, Line Items, Operating Expenses
│   └── generate_data.py      # Main pipeline orchestrator exporting to CSV
├── output/
│   ├── *.csv                 # 14 relational CSV files
│   └── validation_report.json# Data quality audit report
├── scripts/
│   ├── generate_demo_data.py # CLI runner to generate synthetic data
│   ├── validate_demo_data.py # Integrity, FK, PK, and mathematical consistency validator
│   └── seed_database.py     # Safe, repeatable database seeder into target DB/SQLite
└── README.md
```

---

## 4. Execution Commands

### Generate Synthetic Dataset:
```bash
backend\.venv\Scripts\python.exe data/scripts/generate_demo_data.py
```

### Validate Data Integrity & Quality:
```bash
backend\.venv\Scripts\python.exe data/scripts/validate_demo_data.py
```

### Seed Database (Safe, Non-Destructive):
```bash
backend\.venv\Scripts\python.exe data/scripts/seed_database.py
```

---

## 5. Tenant Isolation & Security

* **Multi-Tenant Isolation:** Demo data is assigned exclusively to Workspace ID `00000000-0000-4000-a000-000000000002`.
* **Zero Real PII:** All customer names, emails, addresses, and employee records are 100% synthetically generated via `Faker` (India locale).
* **Zero Committed Credentials:** Database connection strings are loaded exclusively from environment configuration (`.env.local` / `DATABASE_URL`).
