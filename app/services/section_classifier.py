
SECTION_KEYWORDS = {
    "skills": [
        "skill", "technologies", "tools", "frameworks", 
        "languages", "proficiencies", "technical", "programming"
    ],
    "projects": [
        "project", "application", "system", "platform", 
        "developed", "built", "created"
    ],
    "experience": [
        "experience", "work", "intern", "employment", 
        "position", "role", "job"
    ],
    "education": [
        "education", "university", "degree", "school", 
        "college", "bachelor", "master", "phd"
    ],
    "coursework": [
        "coursework", "courses", "subjects", "curriculum", 
        "classes", "relevant coursework"
    ],
    "certifications": [
        "certification", "certificate", "licensed", "accredited"
    ],
    "activities": [
        "activities", "leadership", "extracurricular", "extra-curricular",
        "volunteer", "involvement"
    ]
}


def classify_section(header: str, content: str) -> str:
    """
    Classify a section by analyzing both header and content.
    
    Returns one of: skills, projects, experience, education, coursework, 
                    certifications, activities, or 'other'.
    """
    # Combine header and content for analysis
    text = (header + " " + content).lower()
    
    # Special case: if header contains "coursework" directly, it's coursework
    if "coursework" in header.lower():
        return "coursework"
    
    # Score each section type
    scores = {}
    for section_type, keywords in SECTION_KEYWORDS.items():
        scores[section_type] = sum(1 for keyword in keywords if keyword in text)
    
    # Get highest scoring type
    best_match = max(scores, key=scores.get)
    
    # Return best match only if score > 0, otherwise 'other'
    return best_match if scores[best_match] > 0 else "other"