import re
from typing import List, Optional
from .section_splitter import split_into_sections
from .section_classifier import classify_section
from .skill_extractor_dynamic import extract_skills_dynamic, extract_skills_with_context_dynamic
from .extractors import (
    extract_projects_from_section,
    extract_education_from_section,
    extract_coursework
)


EMAIL_REGEX = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
PHONE_REGEX = r"(?:\+?\d{1,3}[\s\-]?)?\(?\d{3,4}\)?[\s\-]?\d{3,4}[\s\-]?\d{3,4}"


def extract_contact_info(text: str) -> dict:
    """
    Extract email and phone from the entire text.
    """
    email_match = re.search(EMAIL_REGEX, text)
    
    # Clean text from PDF artifacts before phone extraction
    cleaned_text = re.sub(r'\(cid:\d+\)', '', text)
    
    # Find phone numbers
    phone_matches = re.findall(PHONE_REGEX, cleaned_text)
    # Filter out invalid matches 
    valid_phones = []
    for phone in phone_matches:
        # Remove all non-digits to count
        digits_only = re.sub(r'\D', '', phone)
        # Valid phone should have 10+ digits
        if len(digits_only) >= 10:
            valid_phones.append(phone.strip())
    
    phone = valid_phones[0] if valid_phones else None
    
    # Try to extract name from first line
    first_line = text.split("\n")[0].strip()
    name = first_line if len(first_line.split()) <= 4 else None
    
    return {
        "name": name,
        "email": email_match.group(0) if email_match else None,
        "phone": phone
    }

def detect_experience_level(text: str, education: List[dict]) -> dict:
    """
    Detect candidate's experience level and career stage.
    """
    text_lower = text.lower()
    
    student_indicators = [
        r'\bcurrent(ly)?\s+(?:studying|pursuing|enrolled)',
        r'\b(?:undergraduate|bachelor|btech|b\.tech)\s+student',
        r'\bexpected\s+graduation',
        r'\bseek(?:ing)?\s+internship',
        r'\bfresher\b',
        r'\bcgpa\s*[:=]\s*\d',
    ]
    
    is_student = any(re.search(pattern, text_lower) for pattern in student_indicators)
    
    # Check for internship seeking
    internship_indicators = [
        r'\bseek(?:ing)?\s+(?:summer\s+)?internship',
        r'\bintern(?:ship)?\s+(?:position|role|opportunity)',
        r'\bsummer\s+(?:intern|internship)',
    ]
    
    seeking_internship = any(re.search(pattern, text_lower) for pattern in internship_indicators)
    
    # Extract years of experience
    years_patterns = [
        r'(\d+)\+?\s*years?\s+(?:of\s+)?experience',
        r'experience\s*:\s*(\d+)\+?\s*years?',
    ]
    
    years_experience = 0
    for pattern in years_patterns:
        match = re.search(pattern, text_lower)
        if match:
            years_experience = int(match.group(1))
            break
    
    if is_student or years_experience == 0:
        current_year = 2026  
        for edu in education:
            # Look for expected graduation or recent graduation
            degree_text = edu.get('degree', '') + ' ' + edu.get('details', '')
            year_match = re.search(r'20(\d{2})', degree_text)
            if year_match:
                grad_year = int('20' + year_match.group(1))
                if grad_year >= current_year - 1:  # Graduated within last year or future
                    is_student = True
                    seeking_internship = seeking_internship or (grad_year > current_year)
    
    if is_student or seeking_internship:
        level = "student"
    elif years_experience == 0:
        level = "entry"
    elif years_experience <= 2:
        level = "entry"
    elif years_experience <= 5:
        level = "mid"
    elif years_experience <= 8:
        level = "senior"
    else:
        level = "lead"
    
    return {
        "level": level,
        "years_experience": years_experience,
        "is_student": is_student,
        "seeking_internship": seeking_internship
    }

def parse_resume(text: str) -> dict:
    # Extract contact info from full text
    contact = extract_contact_info(text)
    
    # Split into sections
    sections = split_into_sections(text)
    
    # Initialize result
    parsed = {
        **contact,
        "skills": [],
        "skills_with_context": {},  
        "projects": [],
        "education": [],
        "coursework": [],
        "raw_sections": {},  # For debugging
        "raw_text": text
    }
    
    # Extract skills from entire document using dynamic extraction
    parsed["skills"] = extract_skills_dynamic(text)
    parsed["skills_with_context"] = extract_skills_with_context_dynamic(text)
    
    # Classify and extract from each section
    for header, content in sections.items():
        section_type = classify_section(header, content)
        
        # Store raw section for debugging 
        parsed["raw_sections"][header] = {
            "type": section_type,
            "content_preview": content[:150] + "..." if len(content) > 150 else content
        }
        
        # Apply specialized extractors for non-skill sections
        if section_type == "projects":
            parsed["projects"].extend(extract_projects_from_section(content))
        
        elif section_type == "education":
            parsed["education"].extend(extract_education_from_section(content))
        
        elif section_type == "coursework":
            parsed["coursework"].extend(extract_coursework(content))
    experience_info = detect_experience_level(text, parsed["education"])
    parsed["experience_level"] = experience_info
    
    return parsed

