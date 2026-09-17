# Database Planning & Foundations (`database/`)

This directory will contain database migrations, seed data scripts, and maintenance utilities for EMBIP.

## Directory Structure

```
database/
├── migrations/ # SQL migration files and schema definitions
├── seeds/      # Seed data scripts for initial setup
├── scripts/    # Database administration and backup scripts
└── README.md   # Documentation
```

## Implementation Plan

* **Phase 2 (Database Setup):** Relational schema definition (NovaMart Retail domain), Async SQLAlchemy models, Supabase integration, and Row Level Security (RLS) policies.
* **Phase 3 (Demo Data):** Populating seed scripts for 10 stores, 5 warehouses, 50 products, 200 employees, 20,000+ customers, and 100,000+ transactions.
