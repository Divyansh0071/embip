"""
Database Schema Context Service for EMBIP & NovaMart Retail Domain (Phase 9).
Provides structured, accurate PostgreSQL schema metadata for LLM prompt context.
"""

from typing import Dict, List, Optional


class SchemaContextService:
    """
    Service providing controlled schema descriptions of the NovaMart & EMBIP database.
    Prevents blind schema dumps while ensuring full accuracy for LLM SQL generation.
    """

    # Static catalog of real NovaMart schema tables and columns matching DDL migrations
    SCHEMA_METADATA: Dict[str, Dict[str, str]] = {
        "stores": {
            "id": "UUID PRIMARY KEY",
            "workspace_id": "UUID NOT NULL (FK -> workspaces.id)",
            "store_code": "VARCHAR(50) NOT NULL (e.g. STR-001)",
            "name": "VARCHAR(255) NOT NULL (Store location name)",
            "city": "VARCHAR(100)",
            "state": "VARCHAR(50)",
            "zip_code": "VARCHAR(20)",
            "square_feet": "INTEGER (Store retail size in sq ft)",
            "opened_date": "DATE (Opening date)",
        },
        "warehouses": {
            "id": "UUID PRIMARY KEY",
            "workspace_id": "UUID NOT NULL (FK -> workspaces.id)",
            "warehouse_code": "VARCHAR(50) NOT NULL (e.g. WH-001)",
            "name": "VARCHAR(255) NOT NULL",
            "city": "VARCHAR(100)",
            "state": "VARCHAR(50)",
            "capacity_sqft": "INTEGER",
        },
        "categories": {
            "id": "UUID PRIMARY KEY",
            "workspace_id": "UUID NOT NULL (FK -> workspaces.id)",
            "name": "VARCHAR(100) NOT NULL (Category name e.g. Electronics, Grocery)",
            "description": "TEXT",
        },
        "products": {
            "id": "UUID PRIMARY KEY",
            "workspace_id": "UUID NOT NULL (FK -> workspaces.id)",
            "category_id": "UUID (FK -> categories.id)",
            "sku": "VARCHAR(100) NOT NULL (Stock keeping unit code)",
            "name": "VARCHAR(255) NOT NULL (Product title)",
            "unit_cost": "NUMERIC(12, 2) NOT NULL (Cost price per unit)",
            "unit_price": "NUMERIC(12, 2) NOT NULL (Selling price per unit)",
            "reorder_level": "INTEGER (Low stock threshold)",
        },
        "inventory": {
            "id": "UUID PRIMARY KEY",
            "workspace_id": "UUID NOT NULL (FK -> workspaces.id)",
            "warehouse_id": "UUID NOT NULL (FK -> warehouses.id)",
            "product_id": "UUID NOT NULL (FK -> products.id)",
            "quantity_on_hand": "INTEGER NOT NULL (Current stock quantity)",
            "last_updated": "TIMESTAMPTZ",
        },
        "employees": {
            "id": "UUID PRIMARY KEY",
            "workspace_id": "UUID NOT NULL (FK -> workspaces.id)",
            "store_id": "UUID (FK -> stores.id)",
            "first_name": "VARCHAR(100) NOT NULL",
            "last_name": "VARCHAR(100) NOT NULL",
            "role": "VARCHAR(100) NOT NULL (e.g. Store Manager, Sales Associate)",
            "salary": "NUMERIC(12, 2) (Annual salary)",
            "hired_date": "DATE",
        },
        "customers": {
            "id": "UUID PRIMARY KEY",
            "workspace_id": "UUID NOT NULL (FK -> workspaces.id)",
            "customer_code": "VARCHAR(50) NOT NULL (e.g. CUST-1001)",
            "first_name": "VARCHAR(100) NOT NULL",
            "last_name": "VARCHAR(100) NOT NULL",
            "email": "VARCHAR(255)",
            "city": "VARCHAR(100)",
            "state": "VARCHAR(50)",
            "signup_date": "DATE",
        },
        "sales_transactions": {
            "id": "UUID PRIMARY KEY",
            "workspace_id": "UUID NOT NULL (FK -> workspaces.id)",
            "store_id": "UUID (FK -> stores.id)",
            "customer_id": "UUID (FK -> customers.id)",
            "employee_id": "UUID (FK -> employees.id)",
            "transaction_date": "TIMESTAMPTZ NOT NULL (Date and time of sale)",
            "subtotal": "NUMERIC(12, 2) NOT NULL",
            "tax_amount": "NUMERIC(12, 2) DEFAULT 0.00",
            "discount_amount": "NUMERIC(12, 2) DEFAULT 0.00",
            "total_amount": "NUMERIC(12, 2) NOT NULL (Final sale total)",
            "payment_method": "VARCHAR(50) NOT NULL (Credit Card, Cash, Mobile Pay)",
        },
        "sales_items": {
            "id": "UUID PRIMARY KEY",
            "workspace_id": "UUID NOT NULL (FK -> workspaces.id)",
            "transaction_id": "UUID NOT NULL (FK -> sales_transactions.id)",
            "product_id": "UUID (FK -> products.id)",
            "quantity": "INTEGER NOT NULL (Units sold)",
            "unit_price": "NUMERIC(12, 2) NOT NULL",
            "cost_price": "NUMERIC(12, 2) NOT NULL",
            "total_price": "NUMERIC(12, 2) NOT NULL (quantity * unit_price)",
        },
        "operating_expenses": {
            "id": "UUID PRIMARY KEY",
            "workspace_id": "UUID NOT NULL (FK -> workspaces.id)",
            "store_id": "UUID (FK -> stores.id)",
            "expense_date": "DATE NOT NULL",
            "category": "VARCHAR(100) NOT NULL (Rent, Utilities, Marketing, Maintenance)",
            "amount": "NUMERIC(12, 2) NOT NULL (Expense cost)",
            "description": "TEXT",
        },
    }

    def get_formatted_schema_context(self, relevant_tables: Optional[List[str]] = None) -> str:
        """
        Formats database schema catalog into clean DDL-like markdown for prompt context.
        If relevant_tables is provided, filters to those tables. Otherwise returns full domain schema.
        """
        tables_to_include = relevant_tables or list(self.SCHEMA_METADATA.keys())
        lines = ["### Database Schema Definitions (PostgreSQL):"]

        for table in tables_to_include:
            if table not in self.SCHEMA_METADATA:
                continue

            lines.append(f"\nTable: {table}")
            lines.append("Columns:")
            cols = self.SCHEMA_METADATA[table]
            for col_name, col_type in cols.items():
                lines.append(f"  - {col_name}: {col_type}")

        lines.append("\n### Key Business Rules & Relationships:")
        lines.append("- Revenue & Sales Total: Use SUM(sales_transactions.total_amount) or SUM(sales_items.total_price).")
        lines.append("- Profit/Margin: Calculated as (total_price - (cost_price * quantity)) or SUM(sales_items.total_price - (sales_items.cost_price * sales_items.quantity)).")
        lines.append("- Net Profit: (Total Sales Revenue) - SUM(operating_expenses.amount).")
        lines.append("- Store Performance: Join sales_transactions to stores on sales_transactions.store_id = stores.id.")
        lines.append("- Product Category Sales: Join sales_items to products (product_id), then categories (category_id).")
        lines.append("- Multi-Tenancy: All queries MUST include or preserve workspace scoping. The system sets app.current_workspace_id.")
        lines.append("- Date Filtering: Use transaction_date for sales_transactions, expense_date for operating_expenses.")

        return "\n".join(lines)


# Singleton Instance
schema_context_service = SchemaContextService()
