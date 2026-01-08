"""
SQLAlchemy models for job caching.
"""
from sqlalchemy import Column, String, Text, TIMESTAMP, Integer, DECIMAL, Boolean, Index
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class CachedJob(Base):
    """Cached job postings with TTL"""
    __tablename__ = "cached_jobs"
    
    id = Column(String(255), primary_key=True)
    title = Column(String(500), nullable=False)
    company = Column(String(255), nullable=False)
    location = Column(String(255))
    description = Column(Text)
    requirements = Column(Text)
    employment_type = Column(String(50))
    experience_level = Column(String(50))
    url = Column(Text)
    salary_min = Column(DECIMAL(10, 2))
    salary_max = Column(DECIMAL(10, 2))
    is_remote = Column(Boolean, default=False)
    
    # Search metadata
    search_query_hash = Column(String(64), nullable=False, index=True)
    raw_data = Column(JSONB)
    
    # TTL fields
    fetched_at = Column(TIMESTAMP, default=datetime.utcnow)
    expires_at = Column(TIMESTAMP, nullable=False, index=True)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_search_exp_level', 'search_query_hash', 'experience_level'),
    )


class SearchQuery(Base):
    """Track search queries for analytics and cache management"""
    __tablename__ = "search_queries"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    query_hash = Column(String(64), unique=True, nullable=False, index=True)
    
    # Search criteria
    keywords = Column(ARRAY(Text))
    skills = Column(ARRAY(Text))
    experience_level = Column(String(50))
    location = Column(String(255))
    employment_type = Column(String(50))
    
    # Metadata
    query_count = Column(Integer, default=1)
    last_fetched_at = Column(TIMESTAMP, default=datetime.utcnow)
    expires_at = Column(TIMESTAMP, nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)


class ResumeSearch(Base):
    """Log resume searches for analytics"""
    __tablename__ = "resume_searches"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    resume_hash = Column(String(64))
    query_hash = Column(String(64))
    experience_level = Column(String(50))
    skills = Column(ARRAY(Text))
    results_count = Column(Integer)
    searched_at = Column(TIMESTAMP, default=datetime.utcnow)
class UserProfile(Base):
    __tablename__ = "user_profiles"
    
    user_id = Column(String(255), primary_key=True)
    name = Column(String(255))
    email = Column(String(255))
    phone = Column(String(50))
    skills = Column(ARRAY(Text))
    experience_level = Column(String(50))
    years_experience = Column(Integer)
    is_student = Column(Boolean)
    seeking_internship = Column(Boolean)
    education = Column(JSONB)
    projects = Column(JSONB)
    raw_resume_text = Column(Text)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)