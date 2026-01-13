import re
from typing import List, Dict


def extract_skills_from_section(content: str, skill_dict: set) -> List[str]:
    content_lower = content.lower()
    found = []
    
    for skill in skill_dict:
        # Match whole words or as part of compound terms
        if skill in content_lower:
            found.append(skill)
    
    return sorted(set(found))


def extract_projects_from_section(content: str) -> List[Dict[str, str]]:
    projects = []
    lines = content.split("\n")
    
    current_project = None
    seen_tech_stack = False
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        
        # Skip empty lines
        if not stripped:
            if current_project and current_project.get("title"):
                if not current_project.get("description"):
                    current_project["description"] = ""
                projects.append(current_project)
                current_project = None
                seen_tech_stack = False
            continue
        
        # Skip special chars
        if stripped in ['§', '(cid:239)']:
            continue
        
        is_bullet = stripped.startswith(('•', '◦', '-', '*'))
        
        # Check if it's an explicit tech stack line
        is_tech_stack_explicit = stripped.startswith(('Tech Stack:', 'Technologies:', 'Stack:', 'Built with:'))
        
        is_tech_stack_implicit = (
            not is_bullet and
            ',' in stripped and
            len(stripped) < 150 and  
            len(stripped.split(',')) >= 2 and
            not stripped.endswith('.')  
        )
        looks_like_title = (
            not is_bullet and
            not is_tech_stack_explicit and
            not is_tech_stack_implicit and
            stripped[0].isupper() and
            2 <= len(stripped.split()) <= 15 and
            not stripped.endswith('.') and
            not any(stripped.startswith(prefix) for prefix in ['Languages:', 'Programming', 'Data Science', 'Developer'])
        )
        
        # Decision logic
        if looks_like_title and current_project is None:
            # Start new project
            current_project = {
                "title": stripped,
                "technologies": "",
                "description": ""
            }
            seen_tech_stack = False
        
        elif is_tech_stack_explicit and current_project:
            # Explicit tech stack
            tech_line = re.sub(r'^(Tech Stack:|Technologies:|Stack:|Built with:)\s*', '', stripped)
            current_project["technologies"] = tech_line.strip()
            seen_tech_stack = True
        
        elif is_tech_stack_implicit and current_project and not seen_tech_stack:
            # Implicit tech stack (comma-separated line after title)
            current_project["technologies"] = stripped
            seen_tech_stack = True
        
        elif is_bullet and current_project:
            desc_line = re.sub(r'^[•◦\-\*]\s*', '', stripped)
            if current_project["description"]:
                current_project["description"] += " "
            current_project["description"] += desc_line
        
        elif current_project and current_project.get("description"):
            # Continuation of previous bullet 
            current_project["description"] += " " + stripped
    
    # Save last project
    if current_project and current_project.get("title"):
        if not current_project.get("description"):
            current_project["description"] = ""
        projects.append(current_project)
    
    # Final validation
    valid_projects = []
    for proj in projects:
        # Must have a reasonable title
        if len(proj["title"].split()) < 2:
            continue
        # Title shouldn't be all lowercase
        if proj["title"][0].islower():
            continue
        # Skip if title looks like a section header
        if proj["title"].lower() in ['projects', 'experience', 'technical skills']:
            continue
        
        valid_projects.append(proj)
    
    return valid_projects


def extract_education_from_section(content: str) -> List[Dict[str, str]]:
    education = []
    lines = content.split("\n")
    
    current_entry = None
    
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        
        # Check if line contains degree/score keywords
        degree_keywords = ["bachelor", "master", "phd", "b.tech", "m.tech", 
                          "b.s.", "m.s.", "b.a.", "m.a.", "cgpa", "gpa", "%"]
        has_degree_info = any(keyword in stripped.lower() for keyword in degree_keywords)
        
        # Check if it's a graduation year/expected graduation line
        is_graduation_info = (
            "graduation" in stripped.lower() or
            "expected" in stripped.lower() or
            re.match(r'^\d{4}$', stripped)  # Just a year
        )
       
        institution_keywords = ["institute", "university", "school", "college", "academy"]
        looks_like_institution = (
            any(keyword in stripped.lower() for keyword in institution_keywords) or
            (stripped.istitle() and len(stripped.split()) >= 2 and not has_degree_info)
        )
        
        if looks_like_institution and not current_entry:
            # Start new education entry
            current_entry = {
                "institution": stripped,
                "degree": "",
                "details": ""
            }
        
        elif current_entry and has_degree_info:
            # Add to degree field
            if current_entry["degree"]:
                current_entry["degree"] += " "
            current_entry["degree"] += stripped
        
        elif current_entry and is_graduation_info:
            # Add to details field
            if current_entry["details"]:
                current_entry["details"] += " "
            current_entry["details"] += stripped
        
        elif current_entry:
            # Additional info 
            if current_entry["details"]:
                current_entry["details"] += " "
            current_entry["details"] += stripped
    
    # Add last entry
    if current_entry:
        education.append(current_entry)
    
    return education


def extract_coursework(content: str) -> List[str]:
    
    courses = []
    
    content = re.sub(r'^Relevant Coursework:\s*', '', content, flags=re.IGNORECASE)
    
    if ',' in content:
        # Split by commas
        parts = content.split(',')
        for part in parts:
            cleaned = part.strip()
            # Remove bullet points
            cleaned = re.sub(r'^[•◦\-\*]\s*', '', cleaned)
            # Skip empty or very long (likely not course names)
            if cleaned and len(cleaned.split()) <= 10:
                courses.append(cleaned)
    else:
        # Split by newlines and bullets
        lines = content.split("\n")
        
        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue
            
            # Remove bullet points
            cleaned = re.sub(r'^[•◦\-\*]\s*', '', stripped)
            
            # Skip if it's empty after cleaning
            if not cleaned:
                continue
            
            # If line has multiple courses separated by tabs/spaces 
            if '\t' in cleaned or '  ' in cleaned:
                parts = re.split(r'\t+|\s{2,}', cleaned)
                for part in parts:
                    part = part.strip()
                    if part and len(part.split()) <= 10:
                        courses.append(part)
            else:
                # Single course per line
                if len(cleaned.split()) <= 10:
                    courses.append(cleaned)
    
    return courses