"""
Database CRUD operations for job caching.
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, and_, func
from datetime import datetime, timedelta
from typing import List, Optional, Dict
import hashlib
import json

from app.db.models import CachedJob, SearchQuery, ResumeSearch, UserProfile


def generate_query_hash(skills: List[str], experience_level: str, location: str = None) -> str:
    """Generate consistent hash for search queries"""
    skills_str = ",".join(sorted([s.lower().strip() for s in skills]))
    exp_str = experience_level.lower().strip()
    loc_str = (location or "").lower().strip()
    
    query_string = f"{skills_str}|{exp_str}|{loc_str}"
    return hashlib.sha256(query_string.encode()).hexdigest()


async def check_cached_jobs(
    db: AsyncSession,
    skills: List[str],
    experience_level: str,
    location: Optional[str] = None
) -> Optional[List[Dict]]:
    """
    Check if jobs for this query are already cached and not expired.
    
    Returns:
        List of cached jobs if found and valid, None otherwise
    """
    query_hash = generate_query_hash(skills, experience_level, location)
    
    stmt = select(SearchQuery).where(
        and_(
            SearchQuery.query_hash == query_hash,
            SearchQuery.expires_at > datetime.utcnow()
        )
    )
    result = await db.execute(stmt)
    search_query = result.scalar_one_or_none()
    
    if not search_query:
        return None
    
    search_query.query_count += 1
    search_query.last_fetched_at = datetime.utcnow()
    
    stmt = select(CachedJob).where(
        and_(
            CachedJob.search_query_hash == query_hash,
            CachedJob.expires_at > datetime.utcnow()
        )
    )
    result = await db.execute(stmt)
    cached_jobs = result.scalars().all()
    
    if not cached_jobs:
        return None
    
    await db.commit()
    
    return [job_to_dict(job) for job in cached_jobs]


async def store_jobs_in_cache(
    db: AsyncSession,
    jobs: List[Dict],
    skills: List[str],
    experience_level: str,
    location: Optional[str] = None,
    ttl_days: int = 3
) -> None:
    """
    Store fetched jobs in cache with TTL.
    
    Args:
        jobs: List of job dictionaries from API
        skills: Skills used in search
        experience_level: Experience level filter
        location: Location filter
        ttl_days: Time to live in days (default 3)
    """
    query_hash = generate_query_hash(skills, experience_level, location)
    expires_at = datetime.utcnow() + timedelta(days=ttl_days)
    
    stmt = select(SearchQuery).where(SearchQuery.query_hash == query_hash)
    result = await db.execute(stmt)
    search_query = result.scalar_one_or_none()
    
    if search_query:
        search_query.query_count += 1
        search_query.last_fetched_at = datetime.utcnow()
        search_query.expires_at = expires_at
    else:
        search_query = SearchQuery(
            query_hash=query_hash,
            keywords=skills[:10],
            skills=skills,
            experience_level=experience_level,
            location=location,
            expires_at=expires_at
        )
        db.add(search_query)
    
    for job in jobs:
        cached_job = CachedJob(
            id=job['id'],
            title=job['title'],
            company=job['company'],
            location=job.get('location'),
            description=job.get('description'),
            requirements=job.get('requirements'),
            employment_type=job.get('employment_type'),
            experience_level=job.get('experience_level'),
            url=job.get('url'),
            salary_min=job.get('min_salary'),
            salary_max=job.get('max_salary'),
            is_remote=job.get('is_remote', False),
            search_query_hash=query_hash,
            raw_data=job,
            expires_at=expires_at
        )
        
        await db.merge(cached_job)
    
    await db.commit()
    print(f"  Stored {len(jobs)} jobs in cache (expires in {ttl_days} days)")


async def cleanup_expired_jobs(db: AsyncSession) -> int:
    """
    Delete expired jobs from cache.
    
    Returns:
        Number of jobs deleted
    """
    stmt = delete(CachedJob).where(CachedJob.expires_at <= datetime.utcnow())
    result = await db.execute(stmt)
    jobs_deleted = result.rowcount
    
    stmt = delete(SearchQuery).where(SearchQuery.expires_at <= datetime.utcnow())
    await db.execute(stmt)
    
    await db.commit()
    
    if jobs_deleted > 0:
        print(f"🗑️  Cleaned up {jobs_deleted} expired jobs")
    
    return jobs_deleted


async def log_resume_search(
    db: AsyncSession,
    resume_hash: str,
    query_hash: str,
    experience_level: str,
    skills: List[str],
    results_count: int
) -> None:
    """Log a resume search for analytics"""
    search = ResumeSearch(
        resume_hash=resume_hash,
        query_hash=query_hash,
        experience_level=experience_level,
        skills=skills[:20],
        results_count=results_count
    )
    db.add(search)
    await db.commit()


def job_to_dict(job: CachedJob) -> Dict:
    """Convert CachedJob model to dictionary"""
    return {
        "id": job.id,
        "title": job.title,
        "company": job.company,
        "location": job.location,
        "description": job.description,
        "requirements": job.requirements,
        "employment_type": job.employment_type,
        "experience_level": job.experience_level,
        "url": job.url,
        "min_salary": float(job.salary_min) if job.salary_min else None,
        "max_salary": float(job.salary_max) if job.salary_max else None,
        "is_remote": job.is_remote,
    }


async def save_user_profile(db: AsyncSession, user_id: str, parsed_resume: Dict) -> UserProfile:
    """Save or update user profile with parsed resume data"""
    stmt = select(UserProfile).where(UserProfile.user_id == user_id)
    result = await db.execute(stmt)
    profile = result.scalar_one_or_none()
    
    exp_info = parsed_resume.get('experience_level', {})
    
    if profile:
        profile.skills = parsed_resume.get('skills', [])
        profile.experience_level = exp_info.get('level', 'entry')
        profile.years_experience = exp_info.get('years_experience', 0)
        profile.is_student = exp_info.get('is_student', False)
        profile.seeking_internship = exp_info.get('seeking_internship', False)
        profile.education = parsed_resume.get('education', [])
        profile.projects = parsed_resume.get('projects', [])
        profile.updated_at = datetime.utcnow()
    else:
        profile = UserProfile(
            user_id=user_id,
            name=parsed_resume.get('name'),
            email=parsed_resume.get('email'),
            phone=parsed_resume.get('phone'),
            skills=parsed_resume.get('skills', []),
            experience_level=exp_info.get('level', 'entry'),
            years_experience=exp_info.get('years_experience', 0),
            is_student=exp_info.get('is_student', False),
            seeking_internship=exp_info.get('seeking_internship', False),
            education=parsed_resume.get('education', []),
            projects=parsed_resume.get('projects', []),
            raw_resume_text=parsed_resume.get('raw_text', '')
        )
        db.add(profile)
    
    await db.commit()
    await db.refresh(profile)
    return profile


async def get_user_profile(db: AsyncSession, user_id: str) -> Optional[Dict]:
    """Get user profile"""
    stmt = select(UserProfile).where(UserProfile.user_id == user_id)
    result = await db.execute(stmt)
    profile = result.scalar_one_or_none()
    
    if not profile:
        return None
    
    return {
        "user_id": profile.user_id,
        "name": profile.name,
        "email": profile.email,
        "phone": profile.phone,
        "skills": profile.skills,
        "experience_level": profile.experience_level,
        "years_experience": profile.years_experience,
        "is_student": profile.is_student,
        "seeking_internship": profile.seeking_internship,
        "education": profile.education,
        "projects": profile.projects,
        "updated_at": str(profile.updated_at)
    }