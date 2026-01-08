import requests
import time
from typing import List, Dict, Optional
from app.core.config import settings

class JobFetcher:
    def __init__(self):
        self.api_key = settings.RAPIDAPI_KEY
        self.api_host = settings.RAPIDAPI_HOST
        self.base_url = "https://jsearch.p.rapidapi.com"
        
        if not self.api_key or self.api_key == "":
            raise ValueError("RAPIDAPI_KEY not configured")
    
    def fetch_jobs(
        self, 
        query: str = "software engineer",
        location: Optional[str] = None,
        num_pages: int = 1,
        employment_types: Optional[str] = None,
        experience_level: Optional[str] = None
    ) -> List[Dict]:
        if experience_level == "student":
            query = f"{query} intern OR internship OR student"
        elif experience_level == "entry":
            query = f"{query} junior OR entry level OR graduate"
        elif experience_level == "senior":
            query = f"{query} senior OR lead"
        elif experience_level == "lead":
            query = f"{query} lead OR principal OR staff"
        
        url = f"{self.base_url}/search"
        
        headers = {
            "X-RapidAPI-Key": self.api_key,
            "X-RapidAPI-Host": self.api_host
        }
        
        all_jobs = []
        
        for page in range(1, num_pages + 1):
            params = {
                "query": query,
                "page": str(page),
                "num_pages": "1"
            }
            
            if location:
                params["location"] = location
            
            if employment_types:
                params["employment_types"] = employment_types
            
            try:
                response = requests.get(url, headers=headers, params=params, timeout=30)
                response.raise_for_status()
                
                data = response.json()
                jobs = data.get("data", [])
                
                normalized_jobs = [self._normalize_job(job) for job in jobs]
                all_jobs.extend(normalized_jobs)
                
                print(f"Fetched {len(jobs)} jobs from page {page}")
                
                if page < num_pages:
                    time.sleep(1)
                
            except requests.exceptions.Timeout:
                print(f"Timeout on page {page}, continuing...")
                continue
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 429:
                    print(f"Rate limit reached. Stopping.")
                    break
                elif e.response.status_code >= 500:
                    print(f"Server error on page {page}: {e}")
                    continue
                else:
                    print(f"HTTP Error on page {page}: {e}")
                    break
            except requests.exceptions.RequestException as e:
                print(f"Request error on page {page}: {e}")
                continue
            except Exception as e:
                print(f"Unexpected error on page {page}: {e}")
                continue
        
        return all_jobs
    
    def _normalize_job(self, raw_job: Dict) -> Dict:
        from app.services.job_cleaner import JobCleaner
        
        try:
            normalized = {
                "id": raw_job.get("job_id", ""),
                "title": raw_job.get("job_title", ""),
                "company": raw_job.get("employer_name", ""),
                "location": self._format_location(raw_job),
                "description": raw_job.get("job_description", ""),
                "requirements": self._extract_requirements(raw_job),
                "employment_type": raw_job.get("job_employment_type", "FULLTIME"),
                "url": raw_job.get("job_apply_link", ""),
                "posted_date": raw_job.get("job_posted_at_datetime_utc", ""),
                "min_salary": raw_job.get("job_min_salary"),
                "max_salary": raw_job.get("job_max_salary"),
                "is_remote": raw_job.get("job_is_remote", False),
                "raw": raw_job
            }
            
            normalized["experience_level"] = JobCleaner.classify_job_level(normalized)
            return normalized
        except Exception as e:
            print(f"Error normalizing job: {e}")
            return None
    
    def _format_location(self, job: Dict) -> str:
        city = job.get("job_city", "")
        state = job.get("job_state", "")
        country = job.get("job_country", "")
        
        parts = [p for p in [city, state, country] if p]
        return ", ".join(parts) if parts else "Remote"
    
    def _extract_requirements(self, job: Dict) -> str:
        highlights = job.get("job_highlights", {})
        qualifications = highlights.get("Qualifications", [])
        
        if qualifications:
            return "\n".join(qualifications)
        
        return ""