"""
Retail Domain Data Generator for NovaMart Entities.
"""

import random
import uuid
from datetime import date, datetime, timedelta
from faker import Faker

from data.generators.config import (
    ADMIN_USER_ID,
    CATEGORIES_DATA,
    END_DATE,
    ORG_ID,
    ORG_NAME,
    SEED,
    START_DATE,
    STORES_DATA,
    TARGET_CUSTOMERS,
    TARGET_EMPLOYEES,
    TARGET_PRODUCTS,
    WAREHOUSES_DATA,
    WORKSPACE_ID,
    WORKSPACE_NAME,
)

fake = Faker("en_IN")
Faker.seed(SEED)
random.seed(SEED)


def generate_tenancy():
    """Generate Organization, Workspace, and Demo User metadata."""
    org = {
        "id": ORG_ID,
        "name": ORG_NAME,
        "created_at": "2023-01-01 00:00:00+00",
    }
    workspace = {
        "id": WORKSPACE_ID,
        "org_id": ORG_ID,
        "name": WORKSPACE_NAME,
        "created_at": "2023-01-01 00:00:00+00",
    }
    user = {
        "id": ADMIN_USER_ID,
        "email": "demo.admin@novamart.com",
        "full_name": "NovaMart Admin User",
        "avatar_url": None,
        "created_at": "2023-01-01 00:00:00+00",
    }
    member = {
        "id": str(uuid.uuid4()),
        "workspace_id": WORKSPACE_ID,
        "user_id": ADMIN_USER_ID,
        "role": "ADMIN",
        "joined_at": "2023-01-01 00:00:00+00",
    }

    return [org], [workspace], [user], [member]


def generate_stores():
    """Generate 10 Retail Stores."""
    stores = []
    for s in STORES_DATA:
        stores.append({
            "id": str(uuid.uuid4()),
            "workspace_id": WORKSPACE_ID,
            "store_code": s["store_code"],
            "name": s["name"],
            "city": s["city"],
            "state": s["state"],
            "zip_code": s["zip_code"],
            "square_feet": s["square_feet"],
            "opened_date": s["opened_date"],
            "created_at": f"{s['opened_date']} 00:00:00+00",
        })
    return stores


def generate_warehouses():
    """Generate 5 Logistics Warehouses."""
    warehouses = []
    for w in WAREHOUSES_DATA:
        warehouses.append({
            "id": str(uuid.uuid4()),
            "workspace_id": WORKSPACE_ID,
            "warehouse_code": w["warehouse_code"],
            "name": w["name"],
            "city": w["city"],
            "state": w["state"],
            "capacity_sqft": w["capacity_sqft"],
            "created_at": "2023-01-01 00:00:00+00",
        })
    return warehouses


def generate_categories():
    """Generate 10 Product Categories."""
    categories = []
    for cat in CATEGORIES_DATA:
        categories.append({
            "id": str(uuid.uuid4()),
            "workspace_id": WORKSPACE_ID,
            "name": cat["name"],
            "description": cat["description"],
            "created_at": "2023-01-01 00:00:00+00",
        })
    return categories


def generate_products(categories):
    """Generate 50 Realistic Products mapped to 10 Categories."""
    product_templates = [
        # Consumer Electronics (Category index 0)
        (0, "NovaBook Pro 15 Laptop", 52000.0, 68999.0, 15),
        (0, "UltraSound Noise-Canceling Headphones", 4500.0, 6999.0, 25),
        (0, "SmartHome Voice Assistant Hub", 2800.0, 4499.0, 30),
        (0, "VisionMax 27-inch 4K Monitor", 16500.0, 23999.0, 20),
        (0, "Wireless Bluetooth Soundbar 120W", 5200.0, 7999.0, 25),
        
        # Mobile & Accessories (Category index 1)
        (1, "NovaPhone X 128GB Smartphone", 28000.0, 37999.0, 25),
        (1, "PowerMax 20000mAh Power Bank", 1100.0, 1899.0, 50),
        (1, "FastCharge 65W GaN Wall Charger", 750.0, 1499.0, 40),
        (1, "TrueWireless Earbuds Pro", 2200.0, 3499.0, 35),
        (1, "Tempered Glass Screen Guard Pack", 150.0, 399.0, 100),

        # Home Appliances (Category index 2)
        (2, "EcoChill 340L Double Door Refrigerator", 24000.0, 32990.0, 10),
        (2, "AquaWash 7.5kg Front Load Washer", 19500.0, 26990.0, 10),
        (2, "CoolBreeze 1.5 Ton Inverter AC", 27500.0, 37490.0, 12),
        (2, "QuickChef 25L Convection Microwave", 6800.0, 9990.0, 15),
        (2, "PureAir HEPA Air Purifier", 7200.0, 11490.0, 18),

        # Grocery & Gourmet (Category index 3)
        (3, "Royal Basmati Rice 5kg", 420.0, 599.0, 60),
        (3, "Organic Cold Pressed Sunflower Oil 2L", 310.0, 449.0, 50),
        (3, "Premium Whole Wheat Atta 10kg", 320.0, 459.0, 80),
        (3, "Roasted Almonds & Cashews Mix 500g", 450.0, 699.0, 45),
        (3, "Assorted Darjeeling Tea Pack 250g", 210.0, 349.0, 50),

        # Personal Care & Beauty (Category index 4)
        (4, "Herbal Glow Face Wash 150ml", 120.0, 249.0, 80),
        (4, "Intense Moisture Body Lotion 400ml", 180.0, 329.0, 60),
        (4, "Vitamin C Brightening Serum 30ml", 320.0, 599.0, 40),
        (4, "Keratin Repair Shampoo 650ml", 260.0, 499.0, 50),
        (4, "Daily Sunscreen Gel SPF50 100g", 210.0, 399.0, 70),

        # Home & Kitchen (Category index 5)
        (5, "Non-Stick Induction Cookware 3-Piece Set", 1450.0, 2499.0, 25),
        (5, "Stainless Steel Thermal Flask 1L", 420.0, 799.0, 40),
        (5, "Airtight Glass Container Set of 4", 550.0, 999.0, 35),
        (5, "Microfiber Bedsheet Set Double Bed", 650.0, 1199.0, 30),
        (5, "Chef Knife Set with Wooden Block", 890.0, 1599.0, 20),

        # Apparel & Fashion (Category index 6)
        (6, "Classic Slim Fit Cotton Shirt", 580.0, 1299.0, 40),
        (6, "Stretchable Denim Jeans Navy", 720.0, 1699.0, 45),
        (6, "Women Cotton Anarkali Kurta Set", 850.0, 1899.0, 35),
        (6, "Breathable Sports Polo T-Shirt", 320.0, 799.0, 60),
        (6, "Winter Fleece Zip Hoodie", 680.0, 1499.0, 30),

        # Footwear & Leather (Category index 7)
        (7, "AirCushion Running Sneakers", 1250.0, 2499.0, 30),
        (7, "Genuine Leather Oxford Dress Shoes", 1650.0, 3299.0, 20),
        (7, "Casual Canvas Loafers", 620.0, 1299.0, 40),
        (7, "Hard Shell Cabin Luggage 55cm", 1850.0, 3499.0, 15),
        (7, "Leather Laptop Messenger Bag", 1100.0, 2199.0, 25),

        # Sports & Fitness (Category index 8)
        (8, "Anti-Slip TPE Yoga Mat 6mm", 380.0, 899.0, 40),
        (8, "Adjustable Dumbbell Set 20kg", 1800.0, 3299.0, 15),
        (8, "Pro Badminton Racket Twin Pack", 750.0, 1499.0, 30),
        (8, "Smart Fitness Tracker Band 5", 1400.0, 2499.0, 35),
        (8, "Ergonomic Speed Jump Rope", 150.0, 399.0, 50),

        # Office & Stationery (Category index 9)
        (9, "Wireless Laser Printer All-in-One", 8500.0, 12999.0, 12),
        (9, "Ergonomic Mesh Office Chair", 4200.0, 6999.0, 15),
        (9, "Executive Hardbound Diary 2026", 180.0, 399.0, 60),
        (9, "Gel Pen Box of 20 Assorted", 120.0, 299.0, 80),
        (9, "Metal Desk Organizer Tray", 310.0, 599.0, 40),
    ]

    products = []
    idx = 1
    for cat_idx, name, cost, price, reorder in product_templates:
        category_id = categories[cat_idx]["id"]
        sku = f"SKU-{categories[cat_idx]['name'][:3].upper()}-{idx:03d}"
        products.append({
            "id": str(uuid.uuid4()),
            "workspace_id": WORKSPACE_ID,
            "category_id": category_id,
            "sku": sku,
            "name": name,
            "unit_cost": cost,
            "unit_price": price,
            "reorder_level": reorder,
            "created_at": "2023-01-01 00:00:00+00",
        })
        idx += 1

    return products


def generate_inventory(warehouses, products):
    """Generate 250 inventory records (5 warehouses x 50 products)."""
    inventory = []
    for w in warehouses:
        for p in products:
            # Vary inventory on hand realistically (10 to 450 units)
            qty = random.choices(
                [0, random.randint(3, 9), random.randint(15, 60), random.randint(80, 450)],
                weights=[0.04, 0.08, 0.48, 0.40]
            )[0]
            inventory.append({
                "id": str(uuid.uuid4()),
                "workspace_id": WORKSPACE_ID,
                "warehouse_id": w["id"],
                "product_id": p["id"],
                "quantity_on_hand": qty,
                "last_updated": "2026-09-15 10:00:00+00",
            })
    return inventory


def generate_employees(stores, warehouses):
    """Generate ~200 employees across stores & warehouses."""
    employees = []
    roles_and_salaries = [
        ("Store Manager", 650000.0, 850000.0),
        ("Assistant Manager", 450000.0, 600000.0),
        ("Inventory Specialist", 350000.0, 480000.0),
        ("Senior Sales Associate", 300000.0, 420000.0),
        ("Sales Associate", 220000.0, 320000.0),
        ("Cashier", 200000.0, 280000.0),
        ("Warehouse Supervisor", 500000.0, 700000.0),
        ("Warehouse Operator", 220000.0, 320000.0),
    ]

    # Assign ~16 employees per store (160 total)
    for s in stores:
        # 1 Manager
        fname, lname = fake.first_name(), fake.last_name()
        hired = fake.date_between_dates(date(2021, 1, 1), date(2023, 6, 1))
        employees.append({
            "id": str(uuid.uuid4()),
            "workspace_id": WORKSPACE_ID,
            "store_id": s["id"],
            "first_name": fname,
            "last_name": lname,
            "role": "Store Manager",
            "salary": round(random.uniform(680000, 820000), 2),
            "hired_date": hired.isoformat(),
            "created_at": f"{hired.isoformat()} 00:00:00+00",
        })

        # 1 Assistant Manager
        fname, lname = fake.first_name(), fake.last_name()
        hired = fake.date_between_dates(date(2021, 1, 1), date(2023, 8, 1))
        employees.append({
            "id": str(uuid.uuid4()),
            "workspace_id": WORKSPACE_ID,
            "store_id": s["id"],
            "first_name": fname,
            "last_name": lname,
            "role": "Assistant Manager",
            "salary": round(random.uniform(480000, 580000), 2),
            "hired_date": hired.isoformat(),
            "created_at": f"{hired.isoformat()} 00:00:00+00",
        })

        # 14 staff members
        for _ in range(14):
            role_title, min_sal, max_sal = random.choice(roles_and_salaries[2:6])
            fname, lname = fake.first_name(), fake.last_name()
            hired = fake.date_between_dates(date(2021, 6, 1), date(2024, 6, 1))
            employees.append({
                "id": str(uuid.uuid4()),
                "workspace_id": WORKSPACE_ID,
                "store_id": s["id"],
                "first_name": fname,
                "last_name": lname,
                "role": role_title,
                "salary": round(random.uniform(min_sal, max_sal), 2),
                "hired_date": hired.isoformat(),
                "created_at": f"{hired.isoformat()} 00:00:00+00",
            })

    # Assign ~8 employees per warehouse (40 total) -> Total 200 employees
    for w in warehouses:
        # 1 Warehouse Supervisor
        fname, lname = fake.first_name(), fake.last_name()
        hired = fake.date_between_dates(date(2021, 1, 1), date(2023, 1, 1))
        employees.append({
            "id": str(uuid.uuid4()),
            "workspace_id": WORKSPACE_ID,
            "store_id": None,
            "first_name": fname,
            "last_name": lname,
            "role": "Warehouse Supervisor",
            "salary": round(random.uniform(520000, 680000), 2),
            "hired_date": hired.isoformat(),
            "created_at": f"{hired.isoformat()} 00:00:00+00",
        })

        # 7 Warehouse Operators
        for _ in range(7):
            fname, lname = fake.first_name(), fake.last_name()
            hired = fake.date_between_dates(date(2021, 6, 1), date(2024, 1, 1))
            employees.append({
                "id": str(uuid.uuid4()),
                "workspace_id": WORKSPACE_ID,
                "store_id": None,
                "first_name": fname,
                "last_name": lname,
                "role": "Warehouse Operator",
                "salary": round(random.uniform(240000, 340000), 2),
                "hired_date": hired.isoformat(),
                "created_at": f"{hired.isoformat()} 00:00:00+00",
            })

    return employees


def generate_customers(target_count=TARGET_CUSTOMERS):
    """Generate 20,000 synthetic Indian customers with unique codes and emails."""
    customers = []
    used_emails = set()

    indian_cities = [
        ("Mumbai", "Maharashtra"),
        ("Delhi", "Delhi"),
        ("Bengaluru", "Karnataka"),
        ("Hyderabad", "Telangana"),
        ("Chennai", "Tamil Nadu"),
        ("Pune", "Maharashtra"),
        ("Kolkata", "West Bengal"),
        ("Ahmedabad", "Gujarat"),
        ("Jaipur", "Rajasthan"),
        ("Surat", "Gujarat"),
        ("Lucknow", "Uttar Pradesh"),
        ("Chandigarh", "Punjab"),
        ("Kochi", "Kerala"),
        ("Indore", "Madhya Pradesh"),
        ("Nagpur", "Maharashtra"),
    ]

    for i in range(1, target_count + 1):
        code = f"CUST-{i:05d}"
        fname = fake.first_name()
        lname = fake.last_name()
        
        # Ensure email uniqueness
        email_prefix = f"{fname.lower()}.{lname.lower()}{i}"
        email = f"{email_prefix}@example.org"
        used_emails.add(email)

        city, state = random.choice(indian_cities)
        signup_dt = fake.date_between_dates(START_DATE, END_DATE)

        customers.append({
            "id": str(uuid.uuid4()),
            "workspace_id": WORKSPACE_ID,
            "customer_code": code,
            "first_name": fname,
            "last_name": lname,
            "email": email,
            "city": city,
            "state": state,
            "signup_date": signup_dt.isoformat(),
            "created_at": f"{signup_dt.isoformat()} 00:00:00+00",
        })

    return customers
