"""
Job service with intelligent caching.
"""
from typing import List, Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession
import hashlib
import numpy as np

from app.services.job_fetcher import JobFetcher
from app.services.embedder import get_embedder
from app.db.crud import (
    check_cached_jobs,
    store_jobs_in_cache,
    generate_query_hash,
    log_resume_search
)
from app.core.config import settings


class JobService:
    """
    Service for fetching and caching jobs based on resume analysis.
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.fetcher = JobFetcher()
        self.embedder = get_embedder()
    
    async def get_jobs_for_resume(
        self,
        parsed_resume: Dict,
        top_k: int = 10
    ) -> List[Dict]:
        """
        Get jobs for a parsed resume - uses cache or fetches new jobs.
        
        Args:
            parsed_resume: Parsed resume dictionary from resume_parser
            top_k: Number of top matches to return
        
        Returns:
            List of job dictionaries with match scores
        """
        # Extract search criteria from resume
        skills = parsed_resume.get('skills', [])[:10]  # Top 10 skills
        experience_info = parsed_resume.get('experience_level', {})
        experience_level = experience_info.get('level', 'entry')
        
        if not skills:
            print(" No skills found in resume")
            return []
        
        # Generate resume hash for logging
        resume_text = parsed_resume.get('raw_text', '')
        resume_hash = hashlib.md5(resume_text.encode()).hexdigest()[:16]
        
        # Check cache first
        if settings.ENABLE_CACHE:
            cached_jobs = await check_cached_jobs(
                self.db,
                skills=skills,
                experience_level=experience_level,
                location=settings.DEFAULT_LOCATION
            )
            
            if cached_jobs:
                print(f" Found {len(cached_jobs)} cached jobs")
                # Rank cached jobs against resume
                ranked_jobs = await self._rank_jobs(cached_jobs, parsed_resume, top_k)
                
                # Log search
                query_hash = generate_query_hash(skills, experience_level, settings.DEFAULT_LOCATION)
                await log_resume_search(
                    self.db,
                    resume_hash=resume_hash,
                    query_hash=query_hash,
                    experience_level=experience_level,
                    skills=skills,
                    results_count=len(ranked_jobs)
                )
                
                return ranked_jobs
        
        # Cache miss - fetch new jobs from API
        print(f"🔄 No cached jobs found, fetching from API...")
        jobs = await self._fetch_jobs_from_api(skills, experience_level)
        
        if not jobs:
            print("⚠️ No jobs found from API")
            return []
        
        # Store in cache
        if settings.ENABLE_CACHE:
            await store_jobs_in_cache(
                self.db,
                jobs=jobs,
                skills=skills,
                experience_level=experience_level,
                location=settings.DEFAULT_LOCATION,
                ttl_days=settings.JOB_CACHE_TTL_DAYS
            )
        
        # Rank and return
        ranked_jobs = await self._rank_jobs(jobs, parsed_resume, top_k)
        
        # Log search
        query_hash = generate_query_hash(skills, experience_level, settings.DEFAULT_LOCATION)
        await log_resume_search(
            self.db,
            resume_hash=resume_hash,
            query_hash=query_hash,
            experience_level=experience_level,
            skills=skills,
            results_count=len(ranked_jobs)
        )
        
        return ranked_jobs
    
    async def _fetch_jobs_from_api(
        self,
        skills: List[str],
        experience_level: str
    ) -> List[Dict]:
        """Fetch jobs from external API based on skills"""
        # Create search query from top skills
        query = " OR ".join(skills[:5])  # Use top 5 skills
        
        # Fetch jobs
        jobs = self.fetcher.fetch_jobs(
            query=query,
            location=settings.DEFAULT_LOCATION,
            num_pages=3,  # Fetch ~30 jobs
            experience_level=experience_level
        )
        
        return jobs
    
    async def _rank_jobs(
        self,
        jobs: List[Dict],
        parsed_resume: Dict,
        top_k: int
    ) -> List[Dict]:
        """
        Rank jobs against resume using embeddings.
        
        Returns:
            Top K jobs with match_score added
        """
        if not jobs:
            return []
        
        # Create resume embedding text
        resume_text = self._create_resume_embedding_text(parsed_resume)
        resume_embedding = self.embedder.embed_text(resume_text)
        
        # Create job embeddings
        from app.services.job_cleaner import JobCleaner
        cleaner = JobCleaner()
        
        job_texts = [cleaner.create_embedding_text(job) for job in jobs]
        job_embeddings = self.embedder.embed_batch(job_texts)
        
        # Calculate similarity scores (cosine similarity)
        # Normalize vectors
        resume_norm = resume_embedding / np.linalg.norm(resume_embedding)
        job_norms = job_embeddings / np.linalg.norm(job_embeddings, axis=1, keepdims=True)
        
        # Calculate similarities
        similarities = np.dot(job_norms, resume_norm)
        
        # Add scores to jobs and sort
        for job, score in zip(jobs, similarities):
            job['match_score'] = float(score)
        
        # Sort by score and return top K
        ranked = sorted(jobs, key=lambda x: x['match_score'], reverse=True)
        return ranked[:top_k]
    async def search_jobs_by_query(
    self,
    search_context: Dict,
    top_k: int = 10
    ) -> List[Dict]:
        """
        Search jobs by query + user profile.
        Combines user skills with search query.
        """
        skills = search_context.get('skills', [])
        experience_level = search_context.get('experience_level', 'entry')
        query = search_context.get('query', '')
        
        # Check cache first
        if settings.ENABLE_CACHE:
            cached_jobs = await check_cached_jobs(
                self.db,
                skills=skills[:5],  # Top 5 skills for cache key
                experience_level=experience_level,
                location=settings.DEFAULT_LOCATION
            )
            
            if cached_jobs:
                # Filter cached jobs by query
                filtered = self._filter_by_query(cached_jobs, query)
                if len(filtered) >= top_k:
                    return await self._rank_jobs(filtered, search_context, top_k)
        
        # Fetch new jobs combining query + skills
        combined_query = f"{query} {' OR '.join(skills[:3])}"
        jobs = self.fetcher.fetch_jobs(
            query=combined_query,
            location=settings.DEFAULT_LOCATION,
            num_pages=3,
            experience_level=experience_level
        )
        
        # Cache the results
        if settings.ENABLE_CACHE and jobs:
            await store_jobs_in_cache(
                self.db,
                jobs=jobs,
                skills=skills,
                experience_level=experience_level,
                location=settings.DEFAULT_LOCATION,
                ttl_days=settings.JOB_CACHE_TTL_DAYS
            )
        
        # Rank and return
        return await self._rank_jobs(jobs, search_context, top_k)

    def _filter_by_query(self, jobs: List[Dict], query: str) -> List[Dict]:
        """Filter jobs by query string in title/description"""
        query_lower = query.lower()
        return [
            job for job in jobs
            if query_lower in job.get('title', '').lower() or
            query_lower in job.get('description', '').lower()
        ]
    def _create_resume_embedding_text(self, parsed_resume: Dict) -> str:
        """Create text representation of resume for embedding"""
        parts = []
        
        # Skills
        skills = parsed_resume.get('skills', [])
        if skills:
            parts.append(f"Skills: {', '.join(skills[:20])}")
        
        # Projects
        projects = parsed_resume.get('projects', [])
        for proj in projects[:3]:
            title = proj.get('title', '')
            tech = proj.get('technologies', '')
            if title:
                parts.append(f"Project: {title}. Technologies: {tech}")
        
        # Education
        education = parsed_resume.get('education', [])
        for edu in education:
            degree = edu.get('degree', '')
            institution = edu.get('institution', '')
            if degree:
                parts.append(f"Education: {degree} at {institution}")
        
        return " ".join(parts)