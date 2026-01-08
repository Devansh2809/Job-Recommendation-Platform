import re

def is_heading(line: str) -> bool:
    """
    Detect if a line is a section heading using format heuristics.
    Works regardless of what the heading says.
    
    More strict rules to avoid false positives.
    """
    stripped = line.strip()
    
    if not stripped:
        return False
    
    # Remove bullet points for analysis
    cleaned = re.sub(r'^[•\-\*]\s*', '', stripped)
    
    # Skip if it's a bullet point (even after cleaning, if it has : at end it's likely content)
    if stripped.startswith(('•', '-', '*')) and ':' in stripped:
        return False
    
    # Too long to be a heading (most headings are 1-5 words)
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
    
    # Check for common heading keywords (strong signal)
    heading_keywords = [
        "experience", "education", "skills", "projects", 
        "coursework", "certifications", "activities", "summary",
        "objective", "awards", "publications", "leadership",
        "extra-curricular", "extracurricular", "technical"
    ]
    
    lower_text = cleaned.lower()
    has_keyword = any(keyword in lower_text for keyword in heading_keywords)
    
    # ALL CAPS (e.g., "EDUCATION", "TECHNICAL SKILLS")
    if cleaned.isupper() and word_count <= 4:
        return True
    
    # Title Case with heading keyword
    if cleaned.istitle() and has_keyword:
        return True
    
    # Just the keyword itself in various cases
    if lower_text in heading_keywords:
        return True
    
    return False