-- ==============================================================================
-- EMBIP DDL MIGRATION: 004_documents_schema.sql
-- Description: Evolve existing Phase 2 Documents schema & add Document Chunks
-- Preserves existing Phase 2 UUID primary keys, workspace isolation, & document data.
-- ==============================================================================

-- 1. Evolve existing Phase 2 public.documents table safely
ALTER TABLE public.documents
    ADD COLUMN IF NOT EXISTS uploaded_by UUID REFERENCES public.users(id) ON DELETE CASCADE,
    ADD COLUMN IF NOT EXISTS original_filename VARCHAR(255),
    ADD COLUMN IF NOT EXISTS mime_type VARCHAR(100),
    ADD COLUMN IF NOT EXISTS checksum VARCHAR(64),
    ADD COLUMN IF NOT EXISTS processing_error TEXT,
    ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ DEFAULT now() NOT NULL;

-- Ensure default status check constraint permits Phase 7 lifecycle values
ALTER TABLE public.documents
    DROP CONSTRAINT IF EXISTS documents_status_check;

ALTER TABLE public.documents
    ADD CONSTRAINT documents_status_check
    CHECK (status IN ('uploaded', 'processing', 'processed', 'failed'));

-- 2. Create public.document_chunks table for RAG chunk storage
CREATE TABLE IF NOT EXISTS public.document_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL REFERENCES public.documents(id) ON DELETE CASCADE,
    chunk_index INT NOT NULL,
    content TEXT NOT NULL,
    token_count INT NOT NULL DEFAULT 0,
    char_count INT NOT NULL DEFAULT 0,
    metadata_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT now() NOT NULL,
    CONSTRAINT unique_doc_chunk_idx UNIQUE (document_id, chunk_index)
);

-- 3. Indexes for performance and query optimization
CREATE INDEX IF NOT EXISTS idx_documents_status ON public.documents(status);
CREATE INDEX IF NOT EXISTS idx_document_chunks_document_id ON public.document_chunks(document_id);

-- 4. Enable RLS on document_chunks & apply tenant isolation policy
ALTER TABLE public.document_chunks ENABLE ROW LEVEL SECURITY;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'document_chunks_workspace_isolation') THEN
        CREATE POLICY document_chunks_workspace_isolation ON public.document_chunks
            FOR ALL USING (
                EXISTS (
                    SELECT 1 FROM public.documents d
                    WHERE d.id = document_chunks.document_id
                      AND d.workspace_id = NULLIF(current_setting('app.current_workspace_id', true), '')::uuid
                )
            );
    END IF;
END $$;
