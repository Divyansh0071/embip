-- ==============================================================================
-- EMBIP DDL MIGRATION: 003_auth_rbac_rls.sql
-- Description: Profile & Onboarding Triggers for Supabase Auth Integration
-- ==============================================================================

-- Function to handle new user signup from Supabase auth.users
CREATE OR REPLACE FUNCTION public.handle_new_user_signup()
RETURNS TRIGGER AS $$
DECLARE
    new_org_id UUID;
    new_workspace_id UUID;
    user_name TEXT;
BEGIN
    -- 1. Extract full_name or fallback to email local part
    user_name := COALESCE(
        NEW.raw_user_meta_data->>'full_name',
        split_part(NEW.email, '@', 1)
    );

    -- 2. Insert into public.users if profile does not exist
    INSERT INTO public.users (id, email, full_name, avatar_url, created_at)
    VALUES (
        NEW.id,
        NEW.email,
        user_name,
        NEW.raw_user_meta_data->>'avatar_url',
        NOW()
    )
    ON CONFLICT (id) DO UPDATE
    SET email = EXCLUDED.email,
        full_name = COALESCE(public.users.full_name, EXCLUDED.full_name);

    -- 3. Create default Organization for new user if no membership exists
    IF NOT EXISTS (
        SELECT 1 FROM public.workspace_members WHERE user_id = NEW.id
    ) THEN
        INSERT INTO public.organizations (name)
        VALUES (user_name || ' Organization')
        RETURNING id INTO new_org_id;

        -- Create default Workspace
        INSERT INTO public.workspaces (org_id, name)
        VALUES (new_org_id, 'Default Workspace')
        RETURNING id INTO new_workspace_id;

        -- Create WorkspaceMember with ADMIN role for creator
        INSERT INTO public.workspace_members (workspace_id, user_id, role)
        VALUES (new_workspace_id, NEW.id, 'ADMIN');
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger execution on auth.users table (if auth schema exists)
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_tables WHERE schemaname = 'auth' AND tablename = 'users') THEN
        IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'on_auth_user_created') THEN
            CREATE TRIGGER on_auth_user_created
                AFTER INSERT ON auth.users
                FOR EACH ROW EXECUTE FUNCTION public.handle_new_user_signup();
        END IF;
    END IF;
END $$;
