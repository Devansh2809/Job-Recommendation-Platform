-- Job cache table with TTL
CREATE TABLE IF NOT EXISTS cached_jobs (
    id VARCHAR(255) PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    company VARCHAR(255) NOT NULL,
    location VARCHAR(255),
    description TEXT,
    requirements TEXT,
    employment_type VARCHAR(50),
    experience_level VARCHAR(50),
    url TEXT,
    salary_min DECIMAL(10, 2),
    salary_max DECIMAL(10, 2),
    
    -- Search metadata
    search_query_hash VARCHAR(64) NOT NULL,  -- Hash of the search criteria
    raw_data JSONB,  -- Store full job JSON
    
    -- TTL fields
    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    
    -- Indexing
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for efficient search query lookups
CREATE INDEX IF NOT EXISTS idx_search_query_hash ON cached_jobs(search_query_hash);
CREATE INDEX IF NOT EXISTS idx_expires_at ON cached_jobs(expires_at);
CREATE INDEX IF NOT EXISTS idx_experience_level ON cached_jobs(experience_level);

-- Search query cache table (tracks what queries have been made)
CREATE TABLE IF NOT EXISTS search_queries (
    id SERIAL PRIMARY KEY,
    query_hash VARCHAR(64) UNIQUE NOT NULL,
    
    -- Extracted search criteria
    keywords TEXT[],
    skills TEXT[],
    experience_level VARCHAR(50),
    location VARCHAR(255),
    employment_type VARCHAR(50),
    
    -- Metadata
    query_count INTEGER DEFAULT 1,
    last_fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Job embeddings table (for vector search)
CREATE TABLE IF NOT EXISTS job_embeddings (
    job_id VARCHAR(255) PRIMARY KEY REFERENCES cached_jobs(id) ON DELETE CASCADE,
    embedding VECTOR(384),  -- Use pgvector extension or store as JSONB/BYTEA
    embedding_text TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Resume search history (optional: for analytics)
CREATE TABLE IF NOT EXISTS resume_searches (
    id SERIAL PRIMARY KEY,
    resume_hash VARCHAR(64),
    query_hash VARCHAR(64),
    experience_level VARCHAR(50),
    skills TEXT[],
    results_count INTEGER,
    searched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
-- Add to schemas.sql
CREATE TABLE IF NOT EXISTS user_profiles (
    user_id VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255),
    email VARCHAR(255),
    phone VARCHAR(50),
    skills TEXT[],
    experience_level VARCHAR(50),
    years_experience INTEGER,
    is_student BOOLEAN,
    seeking_internship BOOLEAN,
    education JSONB,
    projects JSONB,
    raw_resume_text TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_user_skills ON user_profiles USING GIN(skills);
CREATE INDEX IF NOT EXISTS idx_user_exp_level ON user_profiles(experience_level);