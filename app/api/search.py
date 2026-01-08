from fastapi import APIRouter, Depends, Query,HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.db.session import get_db
from app.db.crud import get_user_profile
from app.services.job_service import JobService

router = APIRouter(prefix="/search", tags=["Search"])

@router.post("/jobs")
async def search_jobs(
    user_id: str,
    query: str = Query(..., description="Job search query like 'software developer', 'product manager'"),
    top_k: int = 10,
    db: AsyncSession = Depends(get_db)
):
    """
    Search jobs based on user profile and query.
    Uses cached jobs if available, otherwise fetches from API.
    """
    # Get user profile
    profile = await get_user_profile(db, user_id)
    
    if not profile:
        raise HTTPException(status_code=404, detail="Please upload resume first")
    
    # Create search context combining profile + query
    search_context = {
        "skills": profile["skills"],
        "experience_level": profile["experience_level"],
        "query": query,
        "raw_text": f"Looking for {query} position. Skills: {', '.join(profile['skills'][:10])}"
    }
    
    # Use job service to search
    job_service = JobService(db)
    jobs = await job_service.search_jobs_by_query(search_context, top_k=top_k)
    
    return {
        "success": True,
        "query": query,
        "profile_used": {
            "skills_count": len(profile["skills"]),
            "experience_level": profile["experience_level"]
        },
        "jobs_found": len(jobs),
        "recommendations": jobs
    }