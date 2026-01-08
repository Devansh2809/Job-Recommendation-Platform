from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
import tempfile
import os
import hashlib
from typing import Dict, Optional
from pydantic import BaseModel

from app.services.text_extractor import (
    extract_text_from_pdf, 
    extract_text_from_docx,
    extract_text_from_image
)
from app.utils.cleaners import clean_text
from app.services.resume_parser import parse_resume
from app.services.job_service import JobService
from app.models.resume import ResumeProfile
from app.db.session import get_db
from app.core.config import settings

router = APIRouter(prefix="/resume", tags=["Resume"])


async def extract_text(file: UploadFile) -> str:
    suffix = file.filename.split(".")[-1].lower()

    with tempfile.NamedTemporaryFile(delete=False, suffix="." + suffix) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    try:
        if suffix == "pdf":
            raw = extract_text_from_pdf(tmp_path, use_ocr_fallback=True)
        elif suffix == "docx":
            raw = extract_text_from_docx(tmp_path)
        elif suffix in ["jpg", "jpeg", "png", "tiff", "bmp"]:
            raw = extract_text_from_image(tmp_path)
        else:
            raise ValueError(f"Unsupported file type: {suffix}")

        if len(raw.strip()) < 50:
            raise ValueError("Could not extract sufficient text from document. Please ensure your resume contains readable text.")

        return clean_text(raw)

    finally:
        os.unlink(tmp_path)


@router.post("/quick-parse")
async def quick_parse_resume(file: UploadFile = File(...)):
    """
    STEP 1: Quick parse - returns resume info in < 1 second.
    Frontend displays skills immediately.
    """
    try:
        text = await extract_text(file)
        parsed = parse_resume(text)
        
        resume_hash = hashlib.md5(text.encode()).hexdigest()[:16]
        
        print(f" Parsed resume - Skills found: {len(parsed.get('skills', []))}")
        
        return {
            "success": True,
            "resume_id": resume_hash,
            "resume": parsed,
            "message": "Resume parsed successfully. Call /fetch-jobs to get recommendations."
        }
    except Exception as e:
        print(f" Parse error: {e}")
        raise HTTPException(status_code=400, detail=f"Error parsing resume: {str(e)}")


@router.post("/fetch-jobs")
async def fetch_jobs_for_resume(
    resume_data: Dict,
    top_k: int = 10,
    db: AsyncSession = Depends(get_db)
):
    """
    STEP 2: Fetch jobs for parsed resume.
    Expects the full resume object from /quick-parse
    """
    try:
        skills = resume_data.get('skills', [])
        print(f" Received resume data - Skills: {len(skills)}")
        print(f"   First 5 skills: {skills[:5] if skills else 'NONE'}")
        
        if not skills:
            return {
                "success": True,
                "jobs_found": 0,
                "recommendations": [],
                "message": "No skills found in resume. Unable to match jobs."
            }
        
        job_service = JobService(db)
        jobs = await job_service.get_jobs_for_resume(resume_data, top_k=top_k)
        
        return {
            "success": True,
            "jobs_found": len(jobs),
            "recommendations": jobs,
            "message": f"Found {len(jobs)} matching jobs"
        }
    except Exception as e:
        print(f" Error fetching jobs: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error fetching jobs: {str(e)}")


@router.post("/parse", response_model=ResumeProfile)
async def parse_resume_endpoint(file: UploadFile = File(...)):
    """
    Parse resume only - no job matching.
    """
    text = await extract_text(file)
    parsed = parse_resume(text)
    return parsed


@router.post("/upload-and-match")
async def upload_resume_and_match(
    file: UploadFile = File(...),
    top_k: int = 10,
    db: AsyncSession = Depends(get_db)
):
    """
    Single endpoint: Upload, parse, and get jobs.
    """
    try:
        text = await extract_text(file)
        parsed = parse_resume(text)
        
        job_service = JobService(db)
        jobs = await job_service.get_jobs_for_resume(parsed, top_k=top_k)
        
        return {
            "success": True,
            "resume": parsed,
            "jobs_found": len(jobs),
            "recommendations": jobs
        }
    except Exception as e:
        print(f" Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/debug/cache-stats")
async def get_cache_stats(db: AsyncSession = Depends(get_db)):
    """Debug endpoint to check cache status"""
    from app.db.models import CachedJob, SearchQuery
    
    stmt = select(func.count(CachedJob.id))
    result = await db.execute(stmt)
    job_count = result.scalar()
    
    stmt = select(func.count(SearchQuery.id))
    result = await db.execute(stmt)
    query_count = result.scalar()
    
    stmt = select(CachedJob).limit(5)
    result = await db.execute(stmt)
    sample_jobs = result.scalars().all()
    
    return {
        "cache_enabled": settings.ENABLE_CACHE,
        "cached_jobs_count": job_count,
        "search_queries_count": query_count,
        "sample_jobs": [
            {
                "id": job.id,
                "title": job.title,
                "company": job.company,
                "expires_at": str(job.expires_at)
            }
            for job in sample_jobs
        ],
        "database_connected": True,
        "ttl_days": settings.JOB_CACHE_TTL_DAYS
    }


class SaveProfileRequest(BaseModel):
    user_id: str
    parsed_resume: dict


@router.post("/save-profile")
async def save_profile(
    request: SaveProfileRequest,
    db: AsyncSession = Depends(get_db)
):
    """Save parsed resume to user profile"""
    from app.db.crud import save_user_profile, get_user_profile
    
    try:
        profile_model = await save_user_profile(db, request.user_id, request.parsed_resume)
        profile_data = await get_user_profile(db, request.user_id)
        
        return {
            "success": True,
            "message": "Profile saved successfully",
            "profile": profile_data
        }
    except Exception as e:
        print(f" Error saving profile: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error saving profile: {str(e)}")


@router.get("/profile/{user_id}")
async def get_profile(user_id: str, db: AsyncSession = Depends(get_db)):
    """Get user profile"""
    from app.db.crud import get_user_profile
    
    profile = await get_user_profile(db, user_id)
    
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    return {"success": True, "profile": profile}