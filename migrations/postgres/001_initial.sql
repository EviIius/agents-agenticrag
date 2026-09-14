-- Production-target schema for PostgreSQL + pgvector.
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS index_generations (
    id text PRIMARY KEY,
    signature text NOT NULL UNIQUE,
    embedding_provider_label text NOT NULL UNIQUE,
    dimensions integer NOT NULL CHECK (dimensions > 0),
    metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS documents (
    id text PRIMARY KEY,
    collection_id text NOT NULL,
    logical_path text NOT NULL,
    current_version_id text,
    created_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE (collection_id, logical_path)
);

CREATE TABLE IF NOT EXISTS source_versions (
    id text PRIMARY KEY,
    document_id text NOT NULL REFERENCES documents(id),
    content_sha256 text NOT NULL,
    parsed_sha256 text NOT NULL,
    provenance_sha256 text NOT NULL,
    scope_sha256 text NOT NULL,
    media_type text NOT NULL,
    object_path text NOT NULL,
    parser_id text NOT NULL,
    byte_size bigint NOT NULL CHECK (byte_size >= 0),
    parsed_content text NOT NULL,
    publication_at timestamptz,
    effective_at timestamptz,
    ingested_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE (document_id, content_sha256, parsed_sha256, provenance_sha256, parser_id, scope_sha256)
);

ALTER TABLE source_versions ADD COLUMN IF NOT EXISTS parsed_sha256 text;
ALTER TABLE source_versions ADD COLUMN IF NOT EXISTS provenance_sha256 text;
ALTER TABLE source_versions ADD COLUMN IF NOT EXISTS parser_id text NOT NULL DEFAULT 'text-v1';
ALTER TABLE source_versions ADD COLUMN IF NOT EXISTS byte_size bigint;
ALTER TABLE source_versions ADD COLUMN IF NOT EXISTS parsed_content text;
UPDATE source_versions
SET parsed_sha256 = content_sha256,
    provenance_sha256 = coalesce(
        provenance_sha256,
        '4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945'
    ),
    byte_size = coalesce(byte_size, 0)
WHERE parsed_sha256 IS NULL OR provenance_sha256 IS NULL OR byte_size IS NULL;
ALTER TABLE source_versions
    DROP CONSTRAINT IF EXISTS source_versions_document_id_content_sha256_scope_sha256_key;
DROP INDEX IF EXISTS source_versions_identity_v2_idx;
CREATE UNIQUE INDEX IF NOT EXISTS source_versions_identity_v3_idx
    ON source_versions(
        document_id, content_sha256, parsed_sha256, provenance_sha256, parser_id, scope_sha256
    );

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'documents_current_version_fk'
          AND conrelid = 'documents'::regclass
    ) THEN
        ALTER TABLE documents
            ADD CONSTRAINT documents_current_version_fk
            FOREIGN KEY (current_version_id) REFERENCES source_versions(id);
    END IF;
END
$$;

CREATE TABLE IF NOT EXISTS source_scopes (
    source_version_id text NOT NULL REFERENCES source_versions(id) ON DELETE CASCADE,
    scope text NOT NULL,
    PRIMARY KEY (source_version_id, scope)
);

CREATE TABLE IF NOT EXISTS chunks (
    id text PRIMARY KEY,
    source_version_id text NOT NULL REFERENCES source_versions(id) ON DELETE CASCADE,
    index_generation_id text NOT NULL REFERENCES index_generations(id),
    ordinal integer NOT NULL CHECK (ordinal >= 0),
    heading text,
    content text NOT NULL,
    start_char integer NOT NULL CHECK (start_char >= 0),
    end_char integer NOT NULL CHECK (end_char > start_char),
    page_start integer,
    page_end integer,
    section_path jsonb NOT NULL DEFAULT '[]'::jsonb,
    provenance jsonb NOT NULL DEFAULT '[]'::jsonb,
    search_document tsvector GENERATED ALWAYS AS (
        setweight(to_tsvector('simple', coalesce(heading, '')), 'A') ||
        setweight(to_tsvector('simple', content), 'B')
    ) STORED,
    embedding vector NOT NULL,
    UNIQUE (source_version_id, index_generation_id, ordinal)
);

ALTER TABLE chunks ADD COLUMN IF NOT EXISTS section_path jsonb NOT NULL DEFAULT '[]'::jsonb;
ALTER TABLE chunks ADD COLUMN IF NOT EXISTS provenance jsonb NOT NULL DEFAULT '[]'::jsonb;

CREATE INDEX IF NOT EXISTS chunks_search_document_gin ON chunks USING gin (search_document);
CREATE INDEX IF NOT EXISTS chunks_source_ordinal_idx ON chunks (source_version_id, ordinal);
CREATE INDEX IF NOT EXISTS chunks_generation_idx ON chunks (index_generation_id);
CREATE INDEX IF NOT EXISTS source_scopes_scope_idx ON source_scopes (scope, source_version_id);
CREATE INDEX IF NOT EXISTS documents_collection_idx ON documents (collection_id);

-- Exact vector search is the initial baseline. Add HNSW only after measured latency requires it;
-- collection, generation, current-version, and scope predicates must remain in every query.
