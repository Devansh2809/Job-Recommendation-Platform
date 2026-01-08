"""
Test embedding generation for jobs and resumes.
"""
import sys
from pathlib import Path
import json
import numpy as np

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.services.embedder import Embedder
from app.services.job_cleaner import JobCleaner


def main():
    print("🧪 Testing Embedding Generation\n")
    
    # Load sample jobs
    data_dir = project_root / "data"
    sample_jobs_file = data_dir / "sample_jobs.json"
    
    if not sample_jobs_file.exists():
        print("❌ Run test_job.py first to fetch sample jobs!")
        return
    
    with open(sample_jobs_file, "r", encoding="utf-8") as f:
        jobs = json.load(f)
    
    print(f"Loaded {len(jobs)} sample jobs\n")
    
    # Initialize embedder
    embedder = Embedder()
    
    # Test 1: Single text embedding
    print("=" * 80)
    print("TEST 1: Single Job Embedding")
    print("=" * 80)
    
    cleaner = JobCleaner()
    job_text = cleaner.create_embedding_text(jobs[0])
    
    print(f"Job: {jobs[0]['title']} at {jobs[0]['company']}")
    print(f"Text length: {len(job_text)} characters\n")
    
    embedding = embedder.embed_text(job_text)
    print(f"✅ Embedding generated")
    print(f"   Shape: {embedding.shape}")
    print(f"   Dimension: {len(embedding)}")
    print(f"   Sample values: {embedding[:5]}")
    print()
    
    # Test 2: Batch embedding
    print("=" * 80)
    print("TEST 2: Batch Job Embeddings")
    print("=" * 80)
    
    job_texts = [cleaner.create_embedding_text(job) for job in jobs]
    
    embeddings = embedder.embed_batch(job_texts, show_progress=True)
    print(f"\n✅ Batch embeddings generated")
    print(f"   Shape: {embeddings.shape}")
    print(f"   {embeddings.shape[0]} jobs x {embeddings.shape[1]} dimensions")
    print()
    
    # Test 3: Similarity calculation
    print("=" * 80)
    print("TEST 3: Job Similarity")
    print("=" * 80)
    
    # Compare first job with all others
    job_0_embedding = embeddings[0]
    
    # Calculate cosine similarity
    def cosine_similarity(a, b):
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
    
    print(f"Comparing: {jobs[0]['title']} at {jobs[0]['company']}\n")
    
    for i in range(1, len(jobs)):
        similarity = cosine_similarity(job_0_embedding, embeddings[i])
        print(f"  vs {jobs[i]['title']} at {jobs[i]['company']}")
        print(f"     Similarity: {similarity:.4f}\n")
    
    # Test 4: Resume vs Job matching
    print("=" * 80)
    print("TEST 4: Resume-to-Job Matching")
    print("=" * 80)
    
    # Simulate a resume
    sample_resume = """
    Software Engineer with 5 years experience in Python, Machine Learning, and AI.
    
    Skills: Python, TensorFlow, PyTorch, FastAPI, React, Docker, Kubernetes, AWS
    
    Experience:
    - Built ML models for production systems
    - Developed REST APIs using FastAPI
    - Deployed applications on Kubernetes
    
    Looking for AI/ML engineering roles in tech companies.
    """
    
    print("Sample Resume:")
    print(sample_resume[:200] + "...\n")
    
    # Embed resume
    resume_embedding = embedder.embed_text(sample_resume)
    
    # Find best matching jobs
    print("Top 3 Matching Jobs:\n")
    
    similarities = []
    for i, job_emb in enumerate(embeddings):
        sim = cosine_similarity(resume_embedding, job_emb)
        similarities.append((i, sim))
    
    # Sort by similarity (descending)
    similarities.sort(key=lambda x: x[1], reverse=True)
    
    for rank, (job_idx, sim) in enumerate(similarities[:3], 1):
        job = jobs[job_idx]
        print(f"{rank}. {job['title']} at {job['company']}")
        print(f"   Location: {job['location']}")
        print(f"   Similarity Score: {sim:.4f}")
        print(f"   Match: {sim * 100:.1f}%\n")
    
    # Save embeddings
    output_file = data_dir / "sample_embeddings.npy"
    np.save(output_file, embeddings)
    print(f"✅ Saved embeddings to {output_file}")


if __name__ == "__main__":
    main()