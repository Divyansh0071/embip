-- ==============================================================================
-- EMBIP DDL MIGRATION: 002_enable_rls.sql
-- Description: Enable Row Level Security (RLS) & Multi-Tenant Isolation Policies
-- ==============================================================================

-- 1. Enable RLS on core multi-tenancy tables
ALTER TABLE workspaces ENABLE ROW LEVEL SECURITY;
ALTER TABLE workspace_members ENABLE ROW LEVEL SECURITY;

-- 2. Enable RLS on NovaMart business domain tables
ALTER TABLE stores ENABLE ROW LEVEL SECURITY;
ALTER TABLE warehouses ENABLE ROW LEVEL SECURITY;
ALTER TABLE categories ENABLE ROW LEVEL SECURITY;
ALTER TABLE products ENABLE ROW LEVEL SECURITY;
ALTER TABLE inventory ENABLE ROW LEVEL SECURITY;
ALTER TABLE employees ENABLE ROW LEVEL SECURITY;
ALTER TABLE customers ENABLE ROW LEVEL SECURITY;
ALTER TABLE sales_transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE sales_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE operating_expenses ENABLE ROW LEVEL SECURITY;

-- 3. Enable RLS on system metadata & audit tables
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE queries ENABLE ROW LEVEL SECURITY;
ALTER TABLE query_executions ENABLE ROW LEVEL SECURITY;
ALTER TABLE reports ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;

-- ------------------------------------------------------------------------------
-- TENANT ISOLATION POLICIES
-- Uses current session workspace setting `app.current_workspace_id`
-- ------------------------------------------------------------------------------

DO $$
BEGIN
    -- Stores Policy
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'stores_workspace_isolation') THEN
        CREATE POLICY stores_workspace_isolation ON stores
            FOR ALL USING (workspace_id = NULLIF(current_setting('app.current_workspace_id', true), '')::uuid);
    END IF;

    -- Products Policy
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'products_workspace_isolation') THEN
        CREATE POLICY products_workspace_isolation ON products
            FOR ALL USING (workspace_id = NULLIF(current_setting('app.current_workspace_id', true), '')::uuid);
    END IF;

    -- Sales Transactions Policy
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'sales_tx_workspace_isolation') THEN
        CREATE POLICY sales_tx_workspace_isolation ON sales_transactions
            FOR ALL USING (workspace_id = NULLIF(current_setting('app.current_workspace_id', true), '')::uuid);
    END IF;

    -- Documents Policy
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'documents_workspace_isolation') THEN
        CREATE POLICY documents_workspace_isolation ON documents
            FOR ALL USING (workspace_id = NULLIF(current_setting('app.current_workspace_id', true), '')::uuid);
    END IF;

    -- Reports Policy
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'reports_workspace_isolation') THEN
        CREATE POLICY reports_workspace_isolation ON reports
            FOR ALL USING (workspace_id = NULLIF(current_setting('app.current_workspace_id', true), '')::uuid);
    END IF;
END $$;
