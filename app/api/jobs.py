"""
Job-related API endpoints.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import numpy as np

from app.services.embedder import get_embedder
from app.services.vector_store import VectorStore

router = APIRouter(prefix="/jobs", tags=["Jobs"])


class JobRecommendationRequest(BaseModel):
    resume_text: str
    experience_level: Optional[str] = None
    top_k: int = 10


class JobMatch(BaseModel):
    id: str
    title: str
    company: str
    location: str
    employment_type: str
    experience_level: str
    match_score: float
    url: str
    description: str
    requirements: str


class JobRecommendationResponse(BaseModel):
    candidate_name: Optional[str] = None
    experience_level: str
    matches: List[JobMatch]


# Load vector store at startup
# embedder = None
# vector_store = None

# @router.on_event("startup")
# async def load_vector_store():
#     global embedder, vector_store
#     try:
#         embedder = get_embedder()
#         vector_store = VectorStore(dimension=embedder.get_embedding_dim())
#         vector_store.load()
#         print("   Vector store loaded successfully")
#     except Exception as e:
#         print(f" Failed to load vector store: {e}")
#         print("Run: python -m scripts.ingest_jobs")


@router.post("/recommend", response_model=JobRecommendationResponse)
async def get_job_recommendations(request: JobRecommendationRequest):
    """
    Get job recommendations based on resume text.
    """
    if vector_store is None or embedder is None:
        raise HTTPException(
            status_code=503,
            detail="Job index not loaded. Please run job ingestion first."
        )
    
    try:
        # Generate resume embedding
        resume_embedding = embedder.embed_text(request.resume_text)
        
        # Determine experience level
        exp_level = request.experience_level or "entry"
        
        # Search based on experience level
        if exp_level == "student":
            # Get both internships and entry-level
            results_intern = vector_store.search(
                resume_embedding,
                k=request.top_k,
                filters={"experience_level": "student"}
            )
            results_entry = vector_store.search(
                resume_embedding,
                k=5,
                filters={"experience_level": "entry"}
            )
            results = results_intern + results_entry
            results = sorted(results, key=lambda x: x[1], reverse=True)[:request.top_k]
        else:
            # Filter by appropriate levels
            allowed_levels = {
                "entry": ["entry", "mid"],
                "mid": ["entry", "mid", "senior"],
                "senior": ["mid", "senior", "lead"],
                "lead": ["senior", "lead"]
            }.get(exp_level, ["mid"])
            
            all_results = vector_store.search(resume_embedding, k=50)
            results = [
                (job, score) for job, score in all_results
                if job.get('experience_level', 'mid') in allowed_levels
            ][:request.top_k]
        
        # Format results
        matches = []
        for job, score in results:
            matches.append(JobMatch(
                id=job['id'],
                title=job['title'],
                company=job['company'],
                location=job['location'],
                employment_type=job['employment_type'],
                experience_level=job.get('experience_level', 'N/A'),
                match_score=float(score),
                url=job['url'],
                description=job.get('description', '')[:500],  # Limit description
                requirements=job.get('requirements', '')[:300]
            ))
        
        return JobRecommendationResponse(
            experience_level=exp_level,
            matches=matches
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating recommendations: {str(e)}")


@router.get("/stats")
async def get_stats():
    """Get job index statistics"""
    if vector_store is None:
        return {"status": "not_loaded"}
    
    return vector_store.get_stats()