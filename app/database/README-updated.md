## ERD with Individual Columns (Vector Store Compatible)

This ERD uses individual columns for frequently accessed/filtered attributes while retaining `embedding` and `extra_metadata` columns for vector search compatibility via `timescale_vector`.

```mermaid
erDiagram
    databases ||--|{ sql_samples : "contains"
    databases ||--|{ database_schemas : "contains":w
    databases ||--|{ table_relationships : "contains"
    databases ||--|{ query_feedback : "receives"
    databases ||--|{ query_usage_stats : "tracks"

    database_schemas ||--o{ db_tables : "contains"
    db_tables ||--o{ db_columns : "contains"
    db_tables ||--o{ table_relationships : "has_from"
    db_tables ||--o{ table_relationships : "has_to"

    sql_samples ||--o{ query_usage_stats : "tracked_by"
    sql_samples ||--o{ query_feedback : "receives"

    %% Core database table (PK is UUID for FK consistency)
    databases {
        id uuid PK
        name varchar UK
        description text
        created_at timestamptz
        updated_at timestamptz
    }

    %% Vector Store Compatible Tables with Individual Columns
    sql_samples {
        id uuid PK
        database_id uuid FK
        query_text text
        nl_description text "Used as 'contents' for embedding"
        embedding vector
        complexity smallint
        tags text[]
        avg_rating float
        feedback_count integer
        extra_metadata jsonb "Optional: source, performance_notes, etc."
        created_at timestamptz
        updated_at timestamptz
    }

    database_schemas {
        id uuid PK
        database_id uuid FK
        schema_name varchar
        description text "Used as 'contents' for embedding"
        embedding vector
        include_in_context boolean "Flag to include in LLM context"
        extra_metadata jsonb "Optional: other schema details"
        created_at timestamptz
        updated_at timestamptz
    }

    db_tables {
        id uuid PK
        schema_id uuid FK
        table_name varchar
        description text "Used as 'contents' for embedding"
        embedding vector
        include_in_context boolean "Flag to include in LLM context"
        sample_data jsonb
        extra_metadata jsonb "Optional: other table details"
        created_at timestamptz
        updated_at timestamptz
    }

    db_columns {
        id uuid PK
        table_id uuid FK
        column_name varchar
        data_type varchar
        description text "Used as 'contents' for embedding"
        embedding vector
        is_primary_key boolean
        is_foreign_key boolean
        is_nullable boolean "Indicates if column allows NULL values"
        references_table varchar
        references_column varchar
        include_in_context boolean "Flag to include in LLM context"
        extra_metadata jsonb "Optional: constraints, defaults, etc."
        created_at timestamptz
        updated_at timestamptz
    }

    table_relationships {
        id uuid PK
        database_id uuid FK
        from_table_id uuid FK
        to_table_id uuid FK
        relationship_type varchar
        from_column varchar
        to_column varchar
        description text "Used as 'contents' for embedding"
        embedding vector
        extra_metadata jsonb "Optional: cardinality, etc."
        created_at timestamptz
        updated_at timestamptz
    }

    query_feedback {
        id uuid PK
        database_id uuid FK
        sql_sample_id uuid FK
        nl_query text "Used as 'contents' for embedding"
        embedding vector
        generated_sql text
        rating smallint
        feedback_text text
        is_correct boolean
        correction text
        user_id varchar
        extra_metadata jsonb "Optional: session_id, etc."
        created_at timestamptz
        updated_at timestamptz
    }

    %% Non-vector table, uses UUID PK/FKs for consistency
    query_usage_stats {
        id uuid PK
        database_id uuid FK
        sql_sample_id uuid FK
        nl_query text
        similarity_score float
        execution_time_ms integer
        success boolean
        error_message text
        created_at timestamptz
        updated_at timestamptz
    }
```

## SQL Schema (Individual Columns, Vector Compatible)

```sql
-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp"; -- For uuid_generate_v4()
CREATE EXTENSION IF NOT EXISTS vector;      -- For VECTOR type

-- Core database table
CREATE TABLE databases (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Vector Store Compatible Tables with Individual Columns

CREATE TABLE sql_samples (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    database_id UUID NOT NULL REFERENCES databases(id) ON DELETE CASCADE,
    query_text TEXT NOT NULL,
    nl_description TEXT, -- Used as 'contents' for embedding
    embedding VECTOR(1536), -- Assuming 1536 dimensions, adjust as needed
    complexity SMALLINT,
    tags TEXT[],
    avg_rating FLOAT,
    feedback_count INTEGER DEFAULT 0,
    extra_metadata JSONB, -- Optional: source, performance_notes, etc.
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE database_schemas (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    database_id UUID NOT NULL REFERENCES databases(id) ON DELETE CASCADE,
    schema_name VARCHAR(255) NOT NULL,
    description TEXT, -- Used as 'contents' for embedding
    embedding VECTOR(1536), -- Assuming 1536 dimensions, adjust as needed
    include_in_context BOOLEAN NOT NULL DEFAULT TRUE, -- Flag to include in LLM context
    extra_metadata JSONB, -- Optional: other schema details
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (database_id, schema_name)
);

CREATE TABLE db_tables (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    schema_id UUID NOT NULL REFERENCES database_schemas(id) ON DELETE CASCADE,
    table_name VARCHAR(255) NOT NULL,
    description TEXT, -- Used as 'contents' for embedding
    embedding VECTOR(1536), -- Assuming 1536 dimensions, adjust as needed
    include_in_context BOOLEAN NOT NULL DEFAULT TRUE, -- Flag to include in LLM context
    sample_data JSONB,
    extra_metadata JSONB, -- Optional: other table details
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (schema_id, table_name)
);

CREATE TABLE db_columns (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    table_id UUID NOT NULL REFERENCES db_tables(id) ON DELETE CASCADE,
    column_name VARCHAR(255) NOT NULL,
    data_type VARCHAR(100) NOT NULL,
    description TEXT, -- Used as 'contents' for embedding
    embedding VECTOR(1536), -- Assuming 1536 dimensions, adjust as needed
    is_primary_key BOOLEAN DEFAULT FALSE,
    is_foreign_key BOOLEAN DEFAULT FALSE,
    is_nullable BOOLEAN NOT NULL DEFAULT TRUE, -- Indicates if column allows NULL values
    references_table VARCHAR(255), -- Name of the referenced table
    references_column VARCHAR(255), -- Name of the referenced column
    include_in_context BOOLEAN NOT NULL DEFAULT TRUE, -- Flag to include in LLM context
    extra_metadata JSONB, -- Optional: constraints, defaults, etc.
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (table_id, column_name)
);

CREATE TABLE table_relationships (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    database_id UUID NOT NULL REFERENCES databases(id) ON DELETE CASCADE,
    from_table_id UUID NOT NULL REFERENCES db_tables(id) ON DELETE CASCADE,
    to_table_id UUID NOT NULL REFERENCES db_tables(id) ON DELETE CASCADE,
    relationship_type VARCHAR(50), -- e.g., 'one-to-many', 'many-to-one', 'one-to-one'
    from_column VARCHAR(255) NOT NULL, -- Name of the column in the 'from' table
    to_column VARCHAR(255) NOT NULL,   -- Name of the column in the 'to' table
    description TEXT, -- Used as 'contents' for embedding
    embedding VECTOR(1536), -- Assuming 1536 dimensions, adjust as needed
    extra_metadata JSONB, -- Optional: cardinality, etc.
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    -- Consider adding a UNIQUE constraint on (from_table_id, from_column, to_table_id, to_column) if appropriate
);

CREATE TABLE query_feedback (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    database_id UUID NOT NULL REFERENCES databases(id) ON DELETE CASCADE,
    sql_sample_id UUID REFERENCES sql_samples(id) ON DELETE SET NULL, -- Allow feedback even if original sample deleted
    nl_query TEXT, -- Used as 'contents' for embedding
    embedding VECTOR(1536), -- Assuming 1536 dimensions, adjust as needed
    generated_sql TEXT,
    rating SMALLINT CHECK (rating >= 1 AND rating <= 5), -- Example: 1-5 star rating
    feedback_text TEXT,
    is_correct BOOLEAN,
    correction TEXT,
    user_id VARCHAR(255), -- Or link to a users table if you have one
    extra_metadata JSONB, -- Optional: session_id, etc.
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Non-vector table, uses UUID PK/FKs for consistency
CREATE TABLE query_usage_stats (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    database_id UUID NOT NULL REFERENCES databases(id) ON DELETE CASCADE,
    sql_sample_id UUID REFERENCES sql_samples(id) ON DELETE SET NULL, -- Allow stats even if original sample deleted
    nl_query TEXT,
    similarity_score FLOAT,
    execution_time_ms INTEGER,
    success BOOLEAN,
    error_message TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW() -- Note: updated_at might not be needed here unless stats are updated
);

-- Optional: Add indexes for frequently queried columns (especially FKs and filterable fields)
CREATE INDEX idx_sql_samples_database_id ON sql_samples(database_id);
CREATE INDEX idx_sql_samples_complexity ON sql_samples(complexity);
CREATE INDEX idx_sql_samples_tags ON sql_samples USING GIN (tags); -- For array searching

CREATE INDEX idx_database_schemas_database_id ON database_schemas(database_id);
CREATE INDEX idx_db_tables_schema_id ON db_tables(schema_id);
CREATE INDEX idx_db_columns_table_id ON db_columns(table_id);

CREATE INDEX idx_table_relationships_database_id ON table_relationships(database_id);
CREATE INDEX idx_table_relationships_from_table_id ON table_relationships(from_table_id);
CREATE INDEX idx_table_relationships_to_table_id ON table_relationships(to_table_id);

CREATE INDEX idx_query_feedback_database_id ON query_feedback(database_id);
CREATE INDEX idx_query_feedback_sql_sample_id ON query_feedback(sql_sample_id);
CREATE INDEX idx_query_feedback_rating ON query_feedback(rating);
CREATE INDEX idx_query_feedback_user_id ON query_feedback(user_id);

CREATE INDEX idx_query_usage_stats_database_id ON query_usage_stats(database_id);
CREATE INDEX idx_query_usage_stats_sql_sample_id ON query_usage_stats(sql_sample_id);
CREATE INDEX idx_query_usage_stats_success ON query_usage_stats(success);

-- Optional: Add vector indexes (Example using HNSW, choose parameters based on your data/needs)
-- Adjust dimensions as needed
-- CREATE INDEX ON sql_samples USING HNSW (embedding vector_l2_ops);
-- CREATE INDEX ON database_schemas USING HNSW (embedding vector_l2_ops);
-- CREATE INDEX ON db_tables USING HNSW (embedding vector_l2_ops);
-- CREATE INDEX ON db_columns USING HNSW (embedding vector_l2_ops);
-- CREATE INDEX ON table_relationships USING HNSW (embedding vector_l2_ops);
-- CREATE INDEX ON query_feedback USING HNSW (embedding vector_l2_ops);

```
