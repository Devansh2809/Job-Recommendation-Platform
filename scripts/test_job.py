"""
Test script to verify job fetching works.
"""
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.services.job_fetcher import JobFetcher
from app.services.job_cleaner import JobCleaner
import json


def main():
    print("🔍 Testing Job Fetcher...\n")
    
    # Initialize fetcher
    fetcher = JobFetcher()
    
    # Test 1: Fetch software engineer jobs
    print("Fetching software engineer jobs in USA...")
    jobs = fetcher.fetch_jobs(
        query="software engineer",
        location="United States",
        num_pages=1
    )
    
    print(f"✅ Fetched {len(jobs)} jobs\n")
    
    # Display first job
    if jobs:
        job = jobs[0]
        print("=" * 80)
        print("SAMPLE JOB (Raw):")
        print("=" * 80)
        print(f"ID: {job['id']}")
        print(f"Title: {job['title']}")
        print(f"Company: {job['company']}")
        print(f"Location: {job['location']}")
        print(f"Type: {job['employment_type']}")
        print(f"Remote: {job['is_remote']}")
        print(f"Description: {job['description'][:200]}...")
        print()
        
        # Test cleaning
        print("=" * 80)
        print("CLEANED TEXT FOR EMBEDDING:")
        print("=" * 80)
        cleaner = JobCleaner()
        clean_text = cleaner.create_embedding_text(job)
        print(clean_text[:500])
        print()
        
        # Extract keywords
        keywords = cleaner.extract_keywords(job)
        print(f"Keywords: {keywords[:10]}")
        print()
    
    # Save to file for inspection
    # Create data directory if it doesn't exist
    data_dir = project_root / "data"
    data_dir.mkdir(exist_ok=True)
    
    output_file = data_dir / "sample_jobs.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(jobs[:5], f, indent=2, ensure_ascii=False)
    
    print(f"✅ Saved sample jobs to {output_file}")


if __name__ == "__main__":
    main()