"""
Data Generation Configuration & Constants for NovaMart Retail Solutions.
"""

from datetime import date, datetime

# Deterministic Seed
SEED = 42

# Date Range: 3 Years of Historical Data
START_DATE = date(2023, 10, 1)
END_DATE = date(2026, 9, 18)

START_DATETIME = datetime(2023, 10, 1, 0, 0, 0)
END_DATETIME = datetime(2026, 9, 18, 23, 59, 59)

# Isolated Demo Tenant UUIDs
ORG_ID = "00000000-0000-4000-a000-000000000001"
WORKSPACE_ID = "00000000-0000-4000-a000-000000000002"
ADMIN_USER_ID = "00000000-0000-4000-a000-000000000003"

ORG_NAME = "NovaMart Retail Solutions"
WORKSPACE_NAME = "NovaMart Analytics"

# Target Record Counts
TARGET_STORES = 10
TARGET_WAREHOUSES = 5
TARGET_CATEGORIES = 10
TARGET_PRODUCTS = 50
TARGET_EMPLOYEES = 200
TARGET_CUSTOMERS = 20000
TARGET_TRANSACTIONS = 100000

# 10 Stores Specification
STORES_DATA = [
    {
        "store_code": "STR-MUM-01",
        "name": "NovaMart Bandra Flagship",
        "city": "Mumbai",
        "state": "Maharashtra",
        "zip_code": "400050",
        "square_feet": 18500,
        "opened_date": "2021-03-15",
        "sales_weight": 0.16,
    },
    {
        "store_code": "STR-DEL-02",
        "name": "NovaMart Connaught Place",
        "city": "Delhi",
        "state": "Delhi",
        "zip_code": "110001",
        "square_feet": 22000,
        "opened_date": "2021-06-01",
        "sales_weight": 0.18,
    },
    {
        "store_code": "STR-BLR-03",
        "name": "NovaMart Indiranagar",
        "city": "Bengaluru",
        "state": "Karnataka",
        "zip_code": "560038",
        "square_feet": 19200,
        "opened_date": "2021-09-10",
        "sales_weight": 0.15,
    },
    {
        "store_code": "STR-HYD-04",
        "name": "NovaMart Banjara Hills",
        "city": "Hyderabad",
        "state": "Telangana",
        "zip_code": "500034",
        "square_feet": 16800,
        "opened_date": "2022-01-20",
        "sales_weight": 0.12,
    },
    {
        "store_code": "STR-CHN-05",
        "name": "NovaMart T. Nagar",
        "city": "Chennai",
        "state": "Tamil Nadu",
        "zip_code": "600017",
        "square_feet": 17500,
        "opened_date": "2022-04-12",
        "sales_weight": 0.11,
    },
    {
        "store_code": "STR-PUN-06",
        "name": "NovaMart Koregaon Park",
        "city": "Pune",
        "state": "Maharashtra",
        "zip_code": "411001",
        "square_feet": 14000,
        "opened_date": "2022-08-05",
        "sales_weight": 0.08,
    },
    {
        "store_code": "STR-KOL-07",
        "name": "NovaMart Park Street",
        "city": "Kolkata",
        "state": "West Bengal",
        "zip_code": "700016",
        "square_feet": 15600,
        "opened_date": "2022-11-18",
        "sales_weight": 0.07,
    },
    {
        "store_code": "STR-AMD-08",
        "name": "NovaMart CG Road",
        "city": "Ahmedabad",
        "state": "Gujarat",
        "zip_code": "380009",
        "square_feet": 13500,
        "opened_date": "2023-02-14",
        "sales_weight": 0.05,
    },
    {
        "store_code": "STR-JAI-09",
        "name": "NovaMart Malviya Nagar",
        "city": "Jaipur",
        "state": "Rajasthan",
        "zip_code": "302017",
        "square_feet": 12800,
        "opened_date": "2023-05-30",
        "sales_weight": 0.04,
    },
    {
        "store_code": "STR-SUR-10",
        "name": "NovaMart Vesu Boulevard",
        "city": "Surat",
        "state": "Gujarat",
        "zip_code": "395007",
        "square_feet": 14200,
        "opened_date": "2023-08-22",
        "sales_weight": 0.04,
    },
]

# 5 Warehouses Specification
WAREHOUSES_DATA = [
    {
        "warehouse_code": "WRH-BHW-01",
        "name": "Bhiwandi Distribution Hub",
        "city": "Thane",
        "state": "Maharashtra",
        "capacity_sqft": 85000,
    },
    {
        "warehouse_code": "WRH-GUR-02",
        "name": "Gurgaon Logistics Depot",
        "city": "Gurgaon",
        "state": "Haryana",
        "capacity_sqft": 92000,
    },
    {
        "warehouse_code": "WRH-HOS-03",
        "name": "Hoskote Fulfillment Center",
        "city": "Bengaluru",
        "state": "Karnataka",
        "capacity_sqft": 78000,
    },
    {
        "warehouse_code": "WRH-SHM-04",
        "name": "Shamshabad Cargo Warehouse",
        "city": "Hyderabad",
        "state": "Telangana",
        "capacity_sqft": 65000,
    },
    {
        "warehouse_code": "WRH-DNK-05",
        "name": "Dankuni Freight Terminal",
        "city": "Kolkata",
        "state": "West Bengal",
        "capacity_sqft": 70000,
    },
]

# Categories Specification
CATEGORIES_DATA = [
    {"name": "Consumer Electronics", "description": "Laptops, Audio, Smart Home Devices, & Gadgets"},
    {"name": "Mobile & Accessories", "description": "Smartphones, Power Banks, Chargers, & Cases"},
    {"name": "Home Appliances", "description": "Refrigerators, Washing Machines, Air Conditioners, & Microwaves"},
    {"name": "Grocery & Gourmet", "description": "Staples, Packaged Foods, Beverages, & Snacks"},
    {"name": "Personal Care & Beauty", "description": "Skincare, Haircare, Cosmetics, & Hygiene Essentials"},
    {"name": "Home & Kitchen", "description": "Cookware, Dining, Storage Containers, & Furnishings"},
    {"name": "Apparel & Fashion", "description": "Men, Women, & Kids Clothing, Ethnic Wear, & Casuals"},
    {"name": "Footwear & Leather", "description": "Sports Shoes, Formal Shoes, Sandals, & Travel Bags"},
    {"name": "Sports & Fitness", "description": "Gym Equipment, Yoga Mats, Activewear, & Sports Gear"},
    {"name": "Office & Stationery", "description": "Printers, Desk Accessories, Notebooks, & Writing Supplies"},
]

# Payment Methods
PAYMENT_METHODS = ["UPI", "Credit Card", "Debit Card", "Net Banking", "Cash"]
PAYMENT_WEIGHTS = [0.45, 0.25, 0.15, 0.08, 0.07]
