import re

def is_heading(line: str) -> bool:
    stripped = line.strip()
    
    if not stripped:
        return False
    
    # Remove bullet points for analysis
    cleaned = re.sub(r'^[•\-\*]\s*', '', stripped)
    
    # Skip if it's a bullet point 
    if stripped.startswith(('•', '-', '*')) and ':' in stripped:
        return False
    
    word_count = len(cleaned.split())
    if word_count > 5:
        return False
    
    # Skip if it's just a date or date range
    date_pattern = r'^[A-Z][a-z]{2,8}\.?\s+\d{4}|^\d{4}|\d{4}\s*[–-]\s*\d{4}|\d{4}\s*[–-]\s*[A-Z]'
    if re.search(date_pattern, stripped):
        return False
    
    # Skip if it contains common non-heading patterns
    if re.search(r'[@\+\(\)]', stripped):  # Email, phone, parentheses
        return False
    
    # Ends with punctuation → likely a sentence, not a heading
    if re.search(r"[.,;]$", stripped):
        return False
    
    # Check for common heading keywords
    heading_keywords = [
        "experience", "education", "skills", "projects", 
        "coursework", "certifications", "activities", "summary",
        "objective", "awards", "publications", "leadership",
        "extra-curricular", "extracurricular", "technical"
    ]
    
    lower_text = cleaned.lower()
    has_keyword = any(keyword in lower_text for keyword in heading_keywords)
    
    if cleaned.isupper() and word_count <= 4:
        return True
    
    if cleaned.istitle() and has_keyword:
        return True
    
    if lower_text in heading_keywords:
        return True
    
    return False