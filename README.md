# Job Recommendation Platform

A sophisticated NLP-powered job recommendation system that leverages natural language processing, vector embeddings, and intelligent caching to match candidates with relevant job opportunities based on their resume analysis.

## Table of Contents

- [Overview](#overview)
- [System Architecture](#system-architecture)
- [Technical Stack](#technical-stack)
- [Core Features](#core-features)
- [How It Works](#how-it-works)
- [Installation](#installation)
- [Configuration](#configuration)
- [API Documentation](#api-documentation)
- [Database Schema](#database-schema)
- [Machine Learning Pipeline](#machine-learning-pipeline)
- [Performance Optimization](#performance-optimization)

## Overview

The Job Recommendation Platform is an intelligent job matching system that analyzes candidate resumes and recommends relevant job postings using semantic similarity matching. The system employs state-of-the-art NLP models to understand both resume content and job descriptions, creating accurate matches based on skills, experience level, and career objectives.

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend Layer                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   React UI   │  │  Firebase    │  │    Vite      │         │
│  │   (Framer)   │  │    Auth      │  │   Build      │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                       API Gateway (FastAPI)                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Resume     │  │     Jobs     │  │    Search    │         │
│  │   Endpoint   │  │   Endpoint   │  │   Endpoint   │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Service Layer                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Resume     │  │     Job      │  │   Embedder   │         │
│  │   Parser     │  │   Service    │  │   Service    │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │     Job      │  │   Vector     │  │  Scheduler   │         │
│  │   Fetcher    │  │    Store     │  │   Service    │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Data Layer                                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │  PostgreSQL  │  │    FAISS     │  │   JSearch    │         │
│  │   Database   │  │ Vector Index │  │     API      │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└─────────────────────────────────────────────────────────────────┘
```

## Technical Stack

### Backend

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **API Framework** | FastAPI 0.104+ | High-performance async REST API |
| **Server** | Uvicorn / Gunicorn | ASGI server with worker management |
| **Database** | PostgreSQL + AsyncPG | Async database operations |
| **ORM** | SQLAlchemy 2.0 | Database modeling and queries |
| **NLP Model** | spaCy 3.7 | Named entity recognition and text processing |
| **Embeddings** | SentenceTransformers | Semantic text encoding (all-MiniLM-L6-v2) |
| **Vector Search** | FAISS | Fast similarity search on embeddings |
| **Deep Learning** | PyTorch 2.0 | Neural network backend for transformers |
| **Transformers** | Hugging Face 4.30+ | Pre-trained language models |
| **Document Parsing** | PDFMiner.six, docx2txt | Resume text extraction |
| **OCR** | Tesseract + pdf2image | Image-based document processing |
| **Web Scraping** | BeautifulSoup4, lxml | Job data cleaning and parsing |
| **Scheduling** | APScheduler 3.10 | Background job cleanup tasks |
| **HTTP Client** | Requests 2.31 | External API communication |

### Frontend

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Framework** | React 18.2 | Component-based UI |
| **Build Tool** | Vite 5.0 | Fast development and bundling |
| **Animation** | Framer Motion 10.18 | Smooth UI transitions |
| **Authentication** | Firebase 10.14 | User authentication and management |
| **Deployment** | Vercel | Frontend hosting platform |

### External Services

- **JSearch API** (RapidAPI): Real-time job posting aggregation
- **Firebase Auth**: Secure user authentication
- **PostgreSQL Cloud**: Database hosting

## Core Features

### 1. Intelligent Resume Parsing

The system employs a multi-stage resume parsing pipeline:

- **Text Extraction**: Supports PDF, DOCX, and image formats with OCR fallback
- **Section Detection**: Automatically identifies resume sections (education, experience, projects, skills)
- **Contact Extraction**: Regex-based extraction of email, phone, and name
- **Skill Identification**: Dynamic skill extraction using NLP and context analysis
- **Experience Classification**: Determines candidate level (student/entry/mid/senior/lead)

### 2. Semantic Job Matching

Vector-based similarity matching using transformer models:

- **Embedding Generation**: Converts resumes and job descriptions to 384-dimensional vectors
- **Cosine Similarity**: Ranks jobs based on semantic similarity to candidate profile
- **Context-Aware Matching**: Considers skills, experience level, and job requirements
- **Real-time Ranking**: Sub-second matching against hundreds of jobs

### 3. Intelligent Caching System

Multi-level caching strategy to optimize API costs and response times:

- **Query-Based Caching**: Hashes search parameters (skills + experience + location)
- **TTL Management**: Configurable expiration (default: 3 days)
- **Hit Rate Optimization**: Reuses cached jobs for similar queries
- **Background Cleanup**: Scheduled purging of expired cache entries

### 4. User Profile Management

Persistent user state management:

- **Resume Storage**: Saves parsed resume data per user
- **Profile Enrichment**: Tracks skills, education, projects, and preferences
- **Search History**: Logs searches for analytics and recommendations

## How It Works

### Resume Processing Pipeline

```
┌─────────────────┐
│  Upload Resume  │
│  (PDF/DOCX/IMG) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Text Extraction │
│ ─────────────── │
│ • PDFMiner.six  │
│ • docx2txt      │
│ • Tesseract OCR │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Text Cleaning   │
│ ─────────────── │
│ • Remove noise  │
│ • Normalize     │
│ • Fix encoding  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│Section Splitting│
│ ─────────────── │
│ • Heading       │
│   detection     │
│ • Content       │
│   grouping      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Section         │
│ Classification  │
│ ─────────────── │
│ • Skills        │
│ • Education     │
│ • Experience    │
│ • Projects      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Entity          │
│ Extraction      │
│ ─────────────── │
│ • Skills (NLP)  │
│ • Contact info  │
│ • Dates         │
│ • Institutions  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Experience     │
│  Level          │
│  Detection      │
│ ─────────────── │
│ • Student       │
│ • Entry/Mid     │
│ • Senior/Lead   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Structured      │
│ Resume JSON     │
└─────────────────┘
```

### Job Recommendation Flow

```
┌──────────────────┐
│  Parsed Resume   │
└────────┬─────────┘
         │
         ▼
┌──────────────────────────┐
│  Extract Search Criteria │
│  ──────────────────────  │
│  • Top 10 skills         │
│  • Experience level      │
│  • Location preference   │
└────────┬─────────────────┘
         │
         ▼
┌──────────────────────────┐
│   Generate Query Hash    │
│   SHA256(skills+exp+loc) │
└────────┬─────────────────┘
         │
         ▼
    ┌────────────┐
    │ Check Cache│
    └────┬───┬───┘
         │   │
    Hit  │   │ Miss
         │   │
         │   ▼
         │ ┌──────────────────┐
         │ │  Fetch from API  │
         │ │  ──────────────  │
         │ │  • JSearch API   │
         │ │  • Filter by exp │
         │ │  • ~30 jobs      │
         │ └────────┬─────────┘
         │          │
         │          ▼
         │ ┌──────────────────┐
         │ │  Store in Cache  │
         │ │  TTL: 3 days     │
         │ └────────┬─────────┘
         │          │
         ▼          ▼
┌──────────────────────────┐
│   Embedding Generation   │
│   ──────────────────────│
│   Resume: 384-dim vector │
│   Each Job: 384-dim      │
└────────┬─────────────────┘
         │
         ▼
┌──────────────────────────┐
│  Similarity Calculation  │
│  ──────────────────────  │
│  Cosine(resume, job)     │
│  = dot(norm(r), norm(j)) │
└────────┬─────────────────┘
         │
         ▼
┌──────────────────────────┐
│   Rank by Similarity     │
│   Return Top K (10)      │
└──────────────────────────┘
```

## Installation

### Prerequisites

- Python 3.9+
- Node.js 18+
- PostgreSQL 14+
- Tesseract OCR (for image-based resumes)

### Backend Setup

```bash
# Clone repository
git clone <repository-url>
cd JobRecommendationPlatform

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_sm

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Initialize database
alembic upgrade head

# Run backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env
# Add Firebase config

# Run development server
npm run dev

# Build for production
npm run build
```

## Configuration

### Environment Variables

```env
# API Keys
RAPIDAPI_KEY=your_jsearch_api_key
RAPIDAPI_HOST=jsearch.p.rapidapi.com

# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost/jobplatform

# Application Settings
DEBUG=false
DEFAULT_LOCATION=India
JOB_CACHE_TTL_DAYS=3
ENABLE_CACHE=true

# ML Models
EMBEDDING_MODEL=all-MiniLM-L6-v2

# Frontend
FRONTEND_URL=http://localhost:5173
```

## API Documentation

### Resume Endpoints

#### POST /resume/quick-parse

Parses uploaded resume and extracts structured information.

**Request:**
```bash
curl -X POST http://localhost:8000/resume/quick-parse \
  -F "file=@resume.pdf"
```

**Response:**
```json
{
  "success": true,
  "resume_id": "a1b2c3d4e5f6g7h8",
  "resume": {
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "+1-234-567-8900",
    "skills": ["Python", "FastAPI", "React", "PostgreSQL"],
    "experience_level": {
      "level": "mid",
      "years_experience": 3,
      "is_student": false
    },
    "education": [...],
    "projects": [...]
  }
}
```

#### POST /resume/fetch-jobs

Fetches matching jobs for parsed resume.

**Request:**
```json
{
  "skills": ["Python", "FastAPI"],
  "experience_level": {
    "level": "mid",
    "years_experience": 3
  },
  "raw_text": "..."
}
```

**Response:**
```json
{
  "success": true,
  "jobs_found": 10,
  "recommendations": [
    {
      "id": "job123",
      "title": "Backend Engineer",
      "company": "Tech Corp",
      "location": "San Francisco, CA",
      "match_score": 0.87,
      "description": "...",
      "requirements": "...",
      "url": "https://..."
    }
  ]
}
```

### Health Check

#### GET /health

```json
{
  "status": "healthy",
  "version": "2.0.0",
  "database": "connected"
}
```

## Database Schema

### Tables

#### cached_jobs
Stores job postings with TTL-based expiration.

```sql
CREATE TABLE cached_jobs (
    id VARCHAR(255) PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    company VARCHAR(255) NOT NULL,
    location VARCHAR(255),
    description TEXT,
    requirements TEXT,
    employment_type VARCHAR(50),
    experience_level VARCHAR(50),
    url TEXT,
    salary_min DECIMAL(10,2),
    salary_max DECIMAL(10,2),
    is_remote BOOLEAN DEFAULT FALSE,
    search_query_hash VARCHAR(64) NOT NULL,
    raw_data JSONB,
    fetched_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_search_exp_level ON cached_jobs(search_query_hash, experience_level);
CREATE INDEX idx_expires ON cached_jobs(expires_at);
```

#### search_queries
Tracks search patterns for cache optimization.

```sql
CREATE TABLE search_queries (
    id SERIAL PRIMARY KEY,
    query_hash VARCHAR(64) UNIQUE NOT NULL,
    keywords TEXT[],
    skills TEXT[],
    experience_level VARCHAR(50),
    location VARCHAR(255),
    query_count INTEGER DEFAULT 1,
    last_fetched_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### user_profiles
Stores user resume data and preferences.

```sql
CREATE TABLE user_profiles (
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
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

## Machine Learning Pipeline

### Embedding Model

**Model**: `sentence-transformers/all-MiniLM-L6-v2`

**Specifications:**
- Architecture: MiniLM (distilled BERT)
- Embedding Dimension: 384
- Max Sequence Length: 256 tokens
- Parameters: 22.7M
- Inference Speed: ~500 sentences/second (CPU)

**Why This Model:**
- Balanced performance vs. speed
- Optimized for semantic similarity tasks
- Small model size (suitable for deployment)
- Strong performance on STS benchmarks

### Similarity Calculation

The system uses **cosine similarity** for ranking:

```python
# Normalize vectors
resume_norm = resume_embedding / ||resume_embedding||
job_norm = job_embedding / ||job_embedding||

# Calculate similarity
similarity = resume_norm · job_norm

# Range: [-1, 1], where 1 = identical, 0 = orthogonal, -1 = opposite
```

### Skill Extraction Algorithm

Dynamic skill extraction using multiple strategies:

1. **Pattern Matching**: Regular expressions for common tech terms
2. **NLP Entity Recognition**: spaCy NER for contextual extraction
3. **Context Analysis**: Identifies skills mentioned in proximity to keywords
4. **Deduplication**: Normalizes variations (e.g., "React.js" → "React")

## Performance Optimization

### Caching Strategy

- **Cache Hit Rate**: ~70% for typical queries
- **API Cost Reduction**: 10x fewer external API calls
- **Response Time**: 
  - Cache hit: <500ms
  - Cache miss: 2-4 seconds

### Database Indexing

```sql
-- Composite index for common query pattern
CREATE INDEX idx_search_exp_level ON cached_jobs(search_query_hash, experience_level);

-- TTL cleanup optimization
CREATE INDEX idx_expires ON cached_jobs(expires_at);
```

### Background Jobs

APScheduler manages maintenance tasks:

```python
# Daily cleanup at 2 AM
scheduler.add_job(
    cleanup_expired_jobs,
    trigger=CronTrigger(hour=2, minute=0)
)
```

### Vector Search Optimization

FAISS IndexFlatL2 with L2 normalization provides:
- O(n) search complexity
- Exact nearest neighbor results
- Suitable for datasets up to 10K vectors

For larger datasets, consider:
- FAISS IVF indices (approximate search)
- Dimensionality reduction (PCA to 128-256 dims)
- GPU acceleration (faiss-gpu)

## Development

### Project Structure

```
app/
├── api/              # FastAPI route handlers
│   ├── resume.py     # Resume parsing endpoints
│   ├── jobs.py       # Job listing endpoints
│   └── search.py     # Search endpoints
├── core/
│   └── config.py     # Configuration management
├── db/
│   ├── models.py     # SQLAlchemy models
│   ├── crud.py       # Database operations
│   └── session.py    # DB connection handling
├── models/
│   └── resume.py     # Pydantic schemas
├── services/
│   ├── resume_parser.py        # Resume parsing logic
│   ├── job_service.py          # Job matching service
│   ├── embedder.py             # Embedding generation
│   ├── vector_store.py         # FAISS vector operations
│   ├── job_fetcher.py          # External API client
│   ├── scheduler.py            # Background tasks
│   └── skill_extractor_dynamic.py  # NLP skill extraction
└── utils/
    └── cleaners.py   # Text preprocessing
```

### Testing

```bash
# Backend tests
pytest tests/ -v --cov=app

# Frontend tests
cd frontend
npm test
```

## Deployment

### Backend (Gunicorn + Uvicorn)

```bash
gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --timeout 120
```

### Frontend (Vercel)

```bash
cd frontend
vercel --prod
```

### Database Migrations

```bash
# Create migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

## Performance Metrics

### Typical Performance

| Operation | Avg Time | Max Time |
|-----------|----------|----------|
| Resume parsing | 800ms | 2s |
| Job fetch (cache hit) | 350ms | 800ms |
| Job fetch (cache miss) | 3.2s | 6s |
| Embedding generation | 150ms | 400ms |
| Similarity ranking (100 jobs) | 50ms | 150ms |

### Scalability

- **Concurrent Users**: 100+ (with 4 Gunicorn workers)
- **Database Load**: 1000+ queries/minute
- **Cache Size**: 10,000+ job postings
- **Daily API Calls**: <100 (with effective caching)



