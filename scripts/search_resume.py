"""
Search jobs using an actual resume file.
"""
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.services.embedder import get_embedder
from app.services.vector_store import VectorStore
from app.services.resume_parser import parse_resume
from app.services.text_extractor import extract_text_from_pdf
from app.utils.cleaners import clean_text


def main():
    print("🔍 Resume-Based Job Search\n")
    
    # Load your resume
    resume_path = project_root / "Devansh_Resume.pdf"
    
    if not resume_path.exists():
        print(f"❌ Resume not found at {resume_path}")
        print("Place your resume PDF in the project root.")
        return
    
    print(f"📄 Loading resume: {resume_path.name}")
    
    # Extract and parse resume
    raw_text = extract_text_from_pdf(str(resume_path))
    resume_text = clean_text(raw_text)
    parsed = parse_resume(resume_text)
    
    # Get experience level
    exp_level = parsed.get('experience_level', {})
    level = exp_level.get('level', 'entry')
    is_student = exp_level.get('is_student', False)
    seeking_internship = exp_level.get('seeking_internship', False)
    
    print(f"✅ Parsed resume for: {parsed.get('name', 'Unknown')}")
    print(f"   Experience Level: {level.upper()}")
    print(f"   Is Student: {is_student}")
    print(f"   Seeking Internship: {seeking_internship}")
    print(f"   Years of Experience: {exp_level.get('years_experience', 0)}")
    print(f"   Skills found: {len(parsed.get('skills', []))}")
    print(f"   Projects: {len(parsed.get('projects', []))}")
    print()
    
    # Create resume summary for embedding
    resume_summary = f"""
    {parsed.get('name', '')}
    
    Skills: {', '.join(parsed.get('skills', [])[:20])}
    
    Projects:
    {' '.join([p.get('title', '') + ': ' + p.get('technologies', '') for p in parsed.get('projects', [])[:3]])}
    
    Education:
    {' '.join([e.get('degree', '') + ' at ' + e.get('institution', '') for e in parsed.get('education', [])])}
    """
    
    print("📝 Resume Summary for Matching:")
    print("-" * 80)
    print(resume_summary[:500] + "...")
    print("-" * 80)
    print()
    
    # Load vector store
    print("📂 Loading job index...")
    embedder = get_embedder()
    vector_store = VectorStore(dimension=embedder.get_embedding_dim())
    
    try:
        vector_store.load()
    except FileNotFoundError:
        print("❌ Job index not found!")
        print("Run this first: python -m scripts.ingest_jobs")
        return
    
    print()
    
    # Generate resume embedding
    print("🤖 Generating resume embedding...")
    resume_embedding = embedder.embed_text(resume_summary)
    print(f"✅ Embedding generated\n")
    
    # Smart search with level filtering
    print(f"🎯 Finding {level}-level jobs...\n")
    
    # Adjust search parameters based on level
    if is_student or seeking_internship:
        # For students: prioritize internships, but also show entry-level
        results_intern = vector_store.search(
            resume_embedding, 
            k=15,
            filters={"experience_level": "student"}
        )
        
        results_entry = vector_store.search(
            resume_embedding,
            k=5,
            filters={"experience_level": "entry"}
        )
        
        results = results_intern + results_entry
        results = sorted(results, key=lambda x: x[1], reverse=True)[:10]
        
    else:
        # For experienced candidates: filter by their level
        allowed_levels = []
        if level == "entry":
            allowed_levels = ["entry", "mid"]
        elif level == "mid":
            allowed_levels = ["entry", "mid", "senior"]
        elif level == "senior":
            allowed_levels = ["mid", "senior", "lead"]
        else:
            allowed_levels = ["senior", "lead"]
        
        # Get more results and filter
        all_results = vector_store.search(resume_embedding, k=50)
        results = [
            (job, score) for job, score in all_results 
            if job.get('experience_level', 'mid') in allowed_levels
        ][:10]
    
    print("=" * 80)
    print(f"TOP 10 JOB MATCHES FOR {parsed.get('name', 'YOU')}")
    print("=" * 80)
    print()
    
    for rank, (job, score) in enumerate(results, 1):
        job_level = job.get('experience_level', 'N/A').upper()
        print(f"#{rank} - [{job_level}] {job['title']}")
        print(f"     Company: {job['company']}")
        print(f"     Location: {job['location']}")
        print(f"     Type: {job['employment_type']}")
        print(f"     Match Score: ⭐ {score*100:.1f}%")
        
        # Show why it matched (if available)
        if job.get('requirements'):
            req_preview = job['requirements'][:150].replace('\n', ' ')
            print(f"     Requirements: {req_preview}...")
        
        print(f"     Apply: {job['url']}")
        print()
    
    # Save results
    output_file = project_root / "data" / "my_job_matches.txt"
    output_file.parent.mkdir(exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"Job Recommendations for {parsed.get('name', 'Candidate')}\n")
        f.write(f"Experience Level: {level.upper()}\n")
        f.write("=" * 80 + "\n\n")
        
        for rank, (job, score) in enumerate(results, 1):
            job_level = job.get('experience_level', 'N/A').upper()
            f.write(f"#{rank} - [{job_level}] {job['title']} at {job['company']}\n")
            f.write(f"Location: {job['location']}\n")
            f.write(f"Match: {score*100:.1f}%\n")
            f.write(f"URL: {job['url']}\n")
            f.write("-" * 80 + "\n\n")
    
    print(f"✅ Results saved to {output_file}")


if __name__ == "__main__":
    main()