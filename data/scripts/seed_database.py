"""
Database Seeding Script for NovaMart Demo Enterprise Data.
Reads CSV data from data/output/ and inserts into the database in relational order.
Supports both PostgreSQL (Supabase) and local SQLite environments.
"""

import asyncio
import os
import sys
import time
from pathlib import Path
import pandas as pd
from sqlalchemy import text

# Ensure root & backend directories are in Python path
root_dir = Path(__file__).resolve().parent.parent.parent
backend_dir = root_dir / "backend"

if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.core.database import AsyncSessionLocal, Base, engine
import app.models  # Ensures all ORM models are registered in Base.metadata
from data.generators.generate_data import run_data_generation



async def seed_database(data_dir: str = "data/output"):
    """Seed NovaMart synthetic dataset into target database."""
    print("=== Starting Database Seeding Process ===")
    
    # Ensure database schema tables exist
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Check if CSVs exist, if not run generation
    if not os.path.exists(os.path.join(data_dir, "sales_transactions.csv")):
        print("Data files not found in data/output. Generating dataset first...")
        run_data_generation(data_dir)


    start_time = time.time()

    # Define table loading order based on foreign key dependencies
    loading_sequence = [
        ("organizations", "organizations.csv"),
        ("workspaces", "workspaces.csv"),
        ("users", "users.csv"),
        ("workspace_members", "workspace_members.csv"),
        ("stores", "stores.csv"),
        ("warehouses", "warehouses.csv"),
        ("categories", "categories.csv"),
        ("products", "products.csv"),
        ("inventory", "inventory.csv"),
        ("employees", "employees.csv"),
        ("customers", "customers.csv"),
        ("sales_transactions", "sales_transactions.csv"),
        ("sales_items", "sales_items.csv"),
        ("operating_expenses", "operating_expenses.csv"),
    ]

    async with AsyncSessionLocal() as session:
        # Check if NovaMart workspace is already seeded
        res = await session.execute(
            text("SELECT COUNT(*) FROM workspaces WHERE id = '00000000-0000-4000-a000-000000000002'")
        )
        existing_ws = res.scalar()
        
        if existing_ws > 0:
            print("Found existing NovaMart Workspace. Cleaning workspace records for re-seeding...")
            # Clean existing workspace data in reverse dependency order
            for table_name, _ in reversed(loading_sequence):
                if table_name not in ("organizations", "users"):
                    await session.execute(
                        text(f"DELETE FROM {table_name} WHERE workspace_id = '00000000-0000-4000-a000-000000000002'")
                    )
            await session.commit()

        print("\n--- Inserting Tables in Relational Order ---")
        for table_name, csv_filename in loading_sequence:
            filepath = os.path.join(data_dir, csv_filename)
            df = pd.read_csv(filepath)
            records = df.to_dict(orient="records")
            
            # Replace NaNs with None for SQL NULL
            for r in records:
                for k, v in r.items():
                    if pd.isna(v):
                        r[k] = None

            print(f" Seeding {table_name:<20} ({len(records):>7,d} rows)...", end="", flush=True)

            # Insert in batches of 5000
            batch_size = 5000
            for i in range(0, len(records), batch_size):
                batch = records[i : i + batch_size]
                if not batch:
                    continue

                columns = list(batch[0].keys())
                col_names = ", ".join(columns)
                val_placeholders = ", ".join([f":{c}" for c in columns])

                # Use SQLite / PostgreSQL safe insert
                sql_str = f"INSERT INTO {table_name} ({col_names}) VALUES ({val_placeholders})"
                if "sqlite" not in str(engine.url):
                    sql_str += " ON CONFLICT DO NOTHING"
                
                await session.execute(text(sql_str), batch)
                await session.commit()

            print(" [DONE]")

    elapsed = round(time.time() - start_time, 2)
    print(f"\n[SUCCESS] Database Seeding Completed Successfully in {elapsed} seconds!")


if __name__ == "__main__":
    asyncio.run(seed_database())
