"""
Test resume-to-job search using the vector store.
"""
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.services.embedder import get_embedder
from app.services.vector_store import VectorStore


def main():
    print("🔍 Testing Job Search\n")
    
    # Load vector store
    print("📂 Loading vector store...")
    embedder = get_embedder()
    vector_store = VectorStore(dimension=embedder.get_embedding_dim())
    vector_store.load()
    print()
    
    # Test resume
    sample_resume = """
    Senior Software Engineer with 7 years of experience.
    
    Skills: Python, FastAPI, React, Machine Learning, AWS, Kubernetes, Docker
    
    Experience:
    - Led development of ML-powered recommendation systems
    - Built scalable APIs serving millions of requests
    - Deployed microservices on Kubernetes
    
    Looking for senior engineer or tech lead roles in AI/ML companies.
    """
    
    print("📄 Sample Resume:")
    print("-" * 80)
    print(sample_resume)
    print("-" * 80)
    print()
    
    # Generate resume embedding
    print("🤖 Generating resume embedding...")
    resume_embedding = embedder.embed_text(sample_resume)
    print(f"✅ Embedding shape: {resume_embedding.shape}\n")
    
    # Search for matching jobs
    print("🎯 Finding matching jobs...\n")
    results = vector_store.search(resume_embedding, k=5)
    
    print("=" * 80)
    print("TOP MATCHING JOBS")
    print("=" * 80)
    print()
    
    for rank, (job, score) in enumerate(results, 1):
        print(f"{rank}. {job['title']}")
        print(f"   Company: {job['company']}")
        print(f"   Location: {job['location']}")
        print(f"   Type: {job['employment_type']}")
        print(f"   Match Score: {score:.4f} ({score*100:.1f}%)")
        print(f"   URL: {job['url']}")
        print()


if __name__ == "__main__":
    main()