"""
Application configuration.
"""
import os
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""
    
    # API Configuration
    RAPIDAPI_KEY: str = ""
    RAPIDAPI_HOST: str = "jsearch.p.rapidapi.com"
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost/jobplatform"
    DEBUG: bool = False
    
    # Embedding Model
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    
    # Vector Store (deprecated - now use DB)
    VECTOR_INDEX_PATH: str = "data/faiss_index"
    JOB_METADATA_PATH: str = "data/job_metadata.json"
    
    # Job Fetching
    DEFAULT_JOB_QUERY: str = "software engineer"
    DEFAULT_LOCATION: str = "India"
    MAX_JOBS_PER_FETCH: int = 50
    
    # Caching
    JOB_CACHE_TTL_DAYS: int = 3
    ENABLE_CACHE: bool = True
    FRONTEND_URL: str = "http://localhost:5173"
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()