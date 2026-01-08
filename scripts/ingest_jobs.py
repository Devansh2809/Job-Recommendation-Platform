"""
Job ingestion pipeline.
Fetches jobs, generates embeddings, and builds FAISS index.
"""
import sys
from pathlib import Path
import argparse

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.services.job_fetcher import JobFetcher
from app.services.job_cleaner import JobCleaner
from app.services.embedder import get_embedder
from app.services.vector_store import VectorStore


def ingest_jobs(query: str = "software engineer", num_pages: int = 3, location: str = None):
    """
    Complete job ingestion pipeline.
    
    Args:
        query: Job search query
        num_pages: Number of pages to fetch
        location: Location filter
    """
    print("=" * 80)
    print("JOB INGESTION PIPELINE")
    print("=" * 80)
    print()
    
    # Step 1: Fetch jobs
    print("📥 Step 1: Fetching jobs...")
    fetcher = JobFetcher()
    jobs = fetcher.fetch_jobs(query=query, location=location, num_pages=num_pages)
    print(f"✅ Fetched {len(jobs)} jobs\n")
    
    # Step 2: Clean and prepare text
    print("🧹 Step 2: Cleaning job descriptions...")
    cleaner = JobCleaner()
    job_texts = []
    
    for job in jobs:
        clean_text = cleaner.create_embedding_text(job)
        job_texts.append(clean_text)
    
    print(f"✅ Prepared {len(job_texts)} job texts\n")
    
    # Step 3: Generate embeddings
    print("🤖 Step 3: Generating embeddings...")
    embedder = get_embedder()
    embeddings = embedder.embed_batch(job_texts, show_progress=True)
    print(f"✅ Generated embeddings with shape {embeddings.shape}\n")
    
    # Step 4: Build vector index
    print("🗂️  Step 4: Building FAISS index...")
    vector_store = VectorStore(dimension=embedder.get_embedding_dim())
    vector_store.create_index(embeddings, jobs)
    print()
    
    # Step 5: Save index
    print("💾 Step 5: Saving index to disk...")
    vector_store.save()
    print()
    
    # Summary
    print("=" * 80)
    print("INGESTION COMPLETE")
    print("=" * 80)
    print(f"Total jobs indexed: {len(jobs)}")
    print(f"Embedding dimension: {embedder.get_embedding_dim()}")
    print(f"Index stats: {vector_store.get_stats()}")
    print()


def main():
    parser = argparse.ArgumentParser(description="Ingest jobs into vector store")
    parser.add_argument("--query", type=str, default="software engineer", help="Job search query")
    parser.add_argument("--pages", type=int, default=3, help="Number of pages to fetch")
    parser.add_argument("--location", type=str, default=None, help="Location filter")
    
    args = parser.parse_args()
    
    ingest_jobs(query=args.query, num_pages=args.pages, location=args.location)


if __name__ == "__main__":
    main()