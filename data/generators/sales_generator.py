"""
Sales Transactions & Operating Expenses Generator for NovaMart.
"""

import math
import random
import uuid
from datetime import datetime, timedelta

from data.generators.config import (
    END_DATETIME,
    PAYMENT_METHODS,
    PAYMENT_WEIGHTS,
    SEED,
    START_DATETIME,
    STORES_DATA,
    TARGET_TRANSACTIONS,
    WORKSPACE_ID,
)

random.seed(SEED)


def _get_seasonality_multiplier(dt: datetime) -> float:
    """Calculate realistic seasonal & growth multipliers."""
    # Monthly seasonality: Diwali/Festival (Oct/Nov = 1.5x, Dec/Jan = 1.35x)
    month_weights = {
        1: 1.30, 2: 0.90, 3: 0.95, 4: 0.95, 5: 1.00, 6: 1.05,
        7: 0.95, 8: 1.10, 9: 1.05, 10: 1.55, 11: 1.65, 12: 1.40
    }
    m_mult = month_weights.get(dt.month, 1.0)

    # Day of week multiplier (Sat/Sun = 1.35x)
    dow_mult = 1.35 if dt.weekday() in (5, 6) else 0.95

    # Yearly trend multiplier (growth over 3 years)
    year_mult = 0.85 if dt.year == 2023 else (1.05 if dt.year == 2024 else (1.20 if dt.year == 2025 else 1.35))

    return m_mult * dow_mult * year_mult


def generate_sales_transactions_and_items(stores, customers, employees, products, target_count=TARGET_TRANSACTIONS):
    """
    Generate 100,000+ sales transactions & line items with strict mathematical consistency.
    """
    transactions = []
    items = []

    # Map employees by store_id
    store_employees = {}
    for emp in employees:
        s_id = emp.get("store_id")
        if s_id:
            store_employees.setdefault(s_id, []).append(emp["id"])

    # Prepare store probability weights
    store_map = {s["store_code"]: s["id"] for s in stores}
    store_ids = [s["id"] for s in stores]
    store_weights = [next(item["sales_weight"] for item in STORES_DATA if item["store_code"] == s["store_code"]) for s in stores]

    # Pre-calculate timeline seconds span
    total_seconds = int((END_DATETIME - START_DATETIME).total_seconds())

    # Customer IDs
    customer_ids = [c["id"] for c in customers]

    print(f"Generating {target_count} sales transactions across 3 years...")

    # Batch timestamps generation using seasonal distribution
    current_count = 0
    while current_count < target_count:
        # Sample random datetime in 3-year range
        random_sec = random.randint(0, total_seconds)
        tx_dt = START_DATETIME + timedelta(seconds=random_sec)

        # Apply seasonal acceptance rejection filter for distribution realism
        mult = _get_seasonality_multiplier(tx_dt)
        if random.random() > (mult / 2.5):
            continue

        # Select store
        s_id = random.choices(store_ids, weights=store_weights)[0]

        # Select customer
        c_id = random.choice(customer_ids)

        # Select employee from store (or None)
        emp_list = store_employees.get(s_id, [])
        e_id = random.choice(emp_list) if emp_list else None

        # Payment method
        pay_method = random.choices(PAYMENT_METHODS, weights=PAYMENT_WEIGHTS)[0]

        # Select line items (1 to 5 items)
        num_items = random.choices([1, 2, 3, 4, 5], weights=[0.45, 0.30, 0.15, 0.07, 0.03])[0]
        selected_products = random.sample(products, num_items)

        tx_id = str(uuid.uuid4())
        tx_subtotal = 0.0

        for prod in selected_products:
            qty = random.choices([1, 2, 3, 4], weights=[0.70, 0.20, 0.07, 0.03])[0]
            u_price = float(prod["unit_price"])
            c_price = float(prod["unit_cost"])
            l_total = round(qty * u_price, 2)

            items.append({
                "id": str(uuid.uuid4()),
                "workspace_id": WORKSPACE_ID,
                "transaction_id": tx_id,
                "product_id": prod["id"],
                "quantity": qty,
                "unit_price": u_price,
                "cost_price": c_price,
                "total_price": l_total,
                "created_at": tx_dt.strftime("%Y-%m-%d %H:%M:%S+00"),
            })

            tx_subtotal += l_total

        tx_subtotal = round(tx_subtotal, 2)

        # Discount (0%, 5%, 10%, or 15%)
        disc_rate = random.choices([0.0, 0.05, 0.10, 0.15], weights=[0.70, 0.15, 0.10, 0.05])[0]
        disc_amount = round(tx_subtotal * disc_rate, 2)

        # 18% GST Tax on discounted amount
        taxable_amount = tx_subtotal - disc_amount
        tax_amount = round(taxable_amount * 0.18, 2)

        total_amount = round(taxable_amount + tax_amount, 2)

        transactions.append({
            "id": tx_id,
            "workspace_id": WORKSPACE_ID,
            "store_id": s_id,
            "customer_id": c_id,
            "employee_id": e_id,
            "transaction_date": tx_dt.strftime("%Y-%m-%d %H:%M:%S+00"),
            "subtotal": tx_subtotal,
            "tax_amount": tax_amount,
            "discount_amount": disc_amount,
            "total_amount": total_amount,
            "payment_method": pay_method,
            "created_at": tx_dt.strftime("%Y-%m-%d %H:%M:%S+00"),
        })

        current_count += 1
        if current_count % 25000 == 0:
            print(f" Generated {current_count}/{target_count} transactions...")

    # Sort transactions chronologically
    transactions.sort(key=lambda x: x["transaction_date"])
    print(f"Completed generation: {len(transactions)} transactions, {len(items)} line items.")
    return transactions, items


def generate_operating_expenses(stores):
    """Generate 36 months of operating expenses for 10 stores (360 total records)."""
    expenses = []
    expense_categories = [
        ("Store Rent & Lease", 120000.0, 350000.0),
        ("Electricity & Utilities", 45000.0, 95000.0),
        ("Store Maintenance & Cleaning", 20000.0, 45000.0),
        ("Local Marketing & Promotions", 30000.0, 75000.0),
        ("Security & Facilities", 25000.0, 50000.0),
    ]

    for s in stores:
        # Generate monthly expense entries for 36 months (Oct 2023 to Sep 2026)
        curr_year, curr_month = 2023, 10
        for _ in range(36):
            exp_date = f"{curr_year}-{curr_month:02d}-01"
            
            for cat_name, min_amt, max_amt in expense_categories:
                # Adjust rent based on store square footage
                sqft_factor = s["square_feet"] / 15000.0
                amt = round(random.uniform(min_amt, max_amt) * sqft_factor, 2)

                expenses.append({
                    "id": str(uuid.uuid4()),
                    "workspace_id": WORKSPACE_ID,
                    "store_id": s["id"],
                    "expense_date": exp_date,
                    "category": cat_name,
                    "amount": amt,
                    "description": f"Monthly {cat_name} for {s['name']}",
                    "created_at": f"{exp_date} 00:00:00+00",
                })

            curr_month += 1
            if curr_month > 12:
                curr_month = 1
                curr_year += 1

    return expenses
