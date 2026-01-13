"""
Job text cleaning and normalization for embeddings.
"""
import re
from typing import Dict
from bs4 import BeautifulSoup


class JobCleaner:
    
    @staticmethod
    def clean_html(text: str) -> str:
        """Remove HTML tags and entities"""
        if not text:
            return ""
        
        # Parse HTML
        soup = BeautifulSoup(text, "html.parser")
        
        # Get text
        text = soup.get_text()
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    @staticmethod
    def normalize_whitespace(text: str) -> str:
        """Normalize all whitespace"""
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text.strip()
    
    @staticmethod
    def remove_special_chars(text: str) -> str:
        """Remove special characters but keep important punctuation"""
        text = re.sub(r'[^a-zA-Z0-9\s.,\-+#/]', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    @staticmethod
    def classify_job_level(job: Dict) -> str:
        """
        Classify job experience level from title and description.
        """
        title = job.get('title', '').lower()
        description = job.get('description', '').lower()
        
        text = title + ' ' + description
        
        # Student/Intern level
        if any(keyword in title for keyword in ['intern', 'internship', 'student', 'co-op']):
            return "student"
        
        # Entry level
        entry_keywords = ['junior', 'entry', 'graduate', 'associate', 'new grad', '0-2 years']
        if any(keyword in text for keyword in entry_keywords):
            return "entry"
        
        # Senior level
        senior_keywords = ['senior', 'sr.', 'sr ', 'lead', 'principal', 'staff', '7+ years', '8+ years']
        if any(keyword in title for keyword in senior_keywords):
            return "senior"
        
        # Lead level
        lead_keywords = ['lead', 'principal', 'staff', 'architect', 'director', '10+ years']
        if any(keyword in title for keyword in lead_keywords):
            return "lead"
        
        # Default to mid-level
        return "mid"
    @staticmethod
    def create_embedding_text(job: Dict) -> str:
        """
        Create clean, structured text for embedding generation.
        """
        parts = []
        
        # Title 
        if job.get("title"):
            parts.append(f"Job Title: {job['title']}")
        
        # Company
        if job.get("company"):
            parts.append(f"Company: {job['company']}")
        
        # Location
        if job.get("location"):
            parts.append(f"Location: {job['location']}")
        
        # Employment Type
        if job.get("employment_type"):
            parts.append(f"Type: {job['employment_type']}")
        
        # Clean description
        if job.get("description"):
            clean_desc = JobCleaner.clean_html(job["description"])
            clean_desc = JobCleaner.normalize_whitespace(clean_desc)
            # Limit description length for embedding 
            if len(clean_desc) > 1000:
                clean_desc = clean_desc[:1000] + "..."
            parts.append(f"Description: {clean_desc}")
        
        # Requirements
        if job.get("requirements"):
            clean_req = JobCleaner.clean_html(job["requirements"])
            clean_req = JobCleaner.normalize_whitespace(clean_req)
            parts.append(f"Requirements: {clean_req}")
        
        # Join all parts
        full_text = "\n\n".join(parts)
        
        return JobCleaner.normalize_whitespace(full_text)
    
    @staticmethod
    def extract_keywords(job: Dict) -> list:
        """
        Extract important keywords from job for later filtering/ranking.
        """
        text = job.get("description", "") + " " + job.get("requirements", "")
        text = JobCleaner.clean_html(text).lower()
        
        # Common skill patterns
        skill_patterns = [
            r'\b(?:python|java|javascript|c\+\+|sql|react|node\.js)\b',
            r'\b(?:aws|azure|gcp|docker|kubernetes)\b',
            r'\b(?:machine learning|ml|ai|data science)\b',
            r'\b(?:bachelor|master|phd|degree)\b',
        ]
        
        keywords = set()
        for pattern in skill_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            keywords.update(matches)
        
        return list(keywords)