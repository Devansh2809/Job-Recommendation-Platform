"""
Domain-agnostic skill extraction using NLP and linguistic patterns.
"""
import spacy
from spacy.matcher import Matcher
import re
from typing import List, Set, Dict

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

# Comprehensive blacklist of non-skill terms
NON_SKILL_TERMS = {
    # Months
    'january', 'february', 'march', 'april', 'may', 'june', 'july',
    'august', 'september', 'october', 'november', 'december',
    'jan', 'feb', 'mar', 'apr', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec',
    
    # Days
    'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday',
    'mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun',
    
    # Common locations (can be expanded)
    'karnataka', 'pradesh', 'uttar', 'delhi', 'mumbai', 'bangalore', 'chennai',
    'manipal', 'lucknow', 'city', 'state', 'country',
    
    # Resume sections
    'experience', 'education', 'projects', 'summary', 'objective',
    'profile', 'background', 'qualifications', 'certifications', 'awards',
    'references', 'activities', 'coursework', 'relevant',
    'extra-curricular', 'extracurricular',
    
    # Common resume words
    'present', 'intern', 'internship', 'bachelor', 'master', 'degree',
    'university', 'college', 'school', 'institute',
    'cgpa', 'gpa', 'percentage', 'place', 'first', 'second', 'third',
    
    # Generic descriptors
    'end-to-end', 'real-time', 'low-latency', 'format-agnostic',
    'multi-class', 'best', 'good', 'excellent', 'strong', 'weak',
    'high', 'low', 'big', 'small', 'large', 'new', 'old',
    
    # Platform names that aren't skills (roles/titles)
    'student', 'campus', 'ambassador', 'coordinator',
    'hackathon', 'national', 'level', 'qualified', 'competitions',
    
    # Category headers that might leak through
    'programming languages', 'developer tools', 'data science',
}


def is_date_or_location_fragment(text: str) -> bool:
    """
    Check if text is a date fragment or location.
    """
    text_lower = text.lower().strip()
    
    # Month names or abbreviations
    months = ['january', 'february', 'march', 'april', 'may', 'june', 'july',
              'august', 'september', 'october', 'november', 'december',
              'jan', 'feb', 'mar', 'apr', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']
    
    if text_lower in months:
        return True
    
    # Date patterns (2023, 2023-2024, Aug 2023, etc.)
    if re.match(r'^\d{4}$', text_lower):  # Just a year
        return True
    
    if re.search(r'\d{4}', text_lower) and len(text_lower.split()) <= 3:  # Contains year
        return True
    
    # Location patterns (contains location indicators)
    location_indicators = ['pradesh', 'karnataka', 'city', 'district', 'state']
    if any(ind in text_lower for ind in location_indicators):
        return True
    
    # Specific location patterns like "Aug 2023" or "Karnataka Aug"
    if re.match(r'^[a-z]+\s+(aug|sep|oct|nov|dec|jan|feb|mar|apr|may|jun|jul)\.?$', text_lower):
        return True
    
    return False


def extract_from_explicit_skill_listings(text: str) -> Set[str]:
    """
    Extract skills from explicit skill listing patterns.
    Handles common resume formats like "Category: skill1, skill2, skill3"
    """ 
    skills = set()
    
    # Split text into lines for line-by-line processing
    lines = text.split('\n')
    
    for line in lines:
        # Match pattern: "Something: items, items, items"
        # Very broad to catch any category with colon followed by comma-separated values
        match = re.match(r'^([^:]+):\s*(.+)$', line.strip())
        
        if match:
            category = match.group(1).strip()
            items_str = match.group(2).strip()
            
            # Check if this looks like a skills category
            skill_category_keywords = [
                'skill', 'language', 'tool', 'platform', 'technology', 'technologie',
                'framework', 'library', 'software', 'certification', 'qualification',
                'competenc', 'proficienc', 'expertise', 'programming', 'developer',
                'data science', 'ml', 'method', 'technique'
            ]
            
            category_lower = category.lower()
            is_skill_category = any(keyword in category_lower for keyword in skill_category_keywords)
            
            if is_skill_category and items_str:
                # Split by comma or semicolon
                parts = re.split(r',|;', items_str)
                
                for part in parts:
                    cleaned = part.strip()
                    # Remove bullets and extra whitespace
                    cleaned = re.sub(r'^[•◦\-\*]\s*', '', cleaned)
                    cleaned = re.sub(r'\s+', ' ', cleaned)
                    
                    # Skip empty
                    if not cleaned:
                        continue
                    
                    # Accept reasonable length (1-5 words for skills)
                    word_count = len(cleaned.split())
                    if 1 <= word_count <= 5:
                        # Additional validation
                        if not is_date_or_location_fragment(cleaned):
                            skills.add(cleaned.lower())
    
    return skills


def extract_proper_nouns_in_skill_context(text: str) -> Set[str]:
    """
    Extract proper nouns ONLY when they appear in skill-related contexts.
    """
    doc = nlp(text)
    skills = set()
    
    # Define skill context indicators
    skill_context_patterns = [
        r'(?:proficient|skilled|experienced|expert|knowledge)\s+(?:in|with|of)',
        r'(?:using|utilizing|applying|working with|implemented)',
        r'(?:skills?|tools?|technologies?|platforms?):\s*',
        r'(?:certified|trained|licensed)\s+(?:in|for)',
    ]
    
    # Find sentences that contain skill contexts
    skill_sentences = []
    for sent in doc.sents:
        sent_text = sent.text
        if any(re.search(pattern, sent_text, re.IGNORECASE) for pattern in skill_context_patterns):
            skill_sentences.append(sent)
    
    # Extract proper nouns only from these sentences
    for sent in skill_sentences:
        for chunk in sent.noun_chunks:
            chunk_text = chunk.text.strip()
            chunk_lower = chunk_text.lower()
            
            # Skip if in blacklist
            if chunk_lower in NON_SKILL_TERMS:
                continue
            
            # Skip if date/location
            if is_date_or_location_fragment(chunk_text):
                continue
            
            # Skip very long phrases
            if len(chunk_text.split()) > 4:
                continue
            
            # Capitalized terms (not at sentence start)
            is_capitalized = chunk_text[0].isupper()
            is_sentence_start = chunk.start == sent.start
            
            if is_capitalized and not is_sentence_start and len(chunk_text) > 2:
                skills.add(chunk_lower)
            
            # All caps acronyms (2-8 chars for things like FAISS, OpenCV)
            if chunk_text.isupper() and 2 <= len(chunk_text) <= 8:
                skills.add(chunk_lower)
    
    return skills


def extract_skills_from_action_contexts(text: str) -> Set[str]:
    """
    Extract skills mentioned in explicit action contexts.
    """
    skills = set()
    
    # Specific patterns for skill mentions
    skill_phrases = [
        r'(?:proficient|skilled|experienced|expert)\s+(?:in|with)\s+([A-Z][A-Za-z0-9\+\#\s\-\.]+?)(?=\s*[,;.]|\s+and\s+|\s+or\s+|$)',
        r'(?:experience|expertise|knowledge)\s+(?:in|with|of)\s+([A-Z][A-Za-z0-9\+\#\s\-\.]+?)(?=\s*[,;.]|\s+and\s+|$)',
        r'(?:using|utilizing|implemented)\s+([A-Z][A-Za-z0-9\+\#\s\-\.]+?)(?=\s*[,;.]|\s+and\s+|\s+for\s+|\s+to\s+|$)',
        r'(?:certified|trained)\s+(?:in|for)\s+([A-Z][A-Za-z0-9\s\-\.]+?)(?=\s*[,;.]|$)',
    ]
    
    for pattern in skill_phrases:
        matches = re.finditer(pattern, text)
        for match in matches:
            skill = match.group(1).strip().lower()
            
            # Validate
            if not is_date_or_location_fragment(skill):
                if skill not in NON_SKILL_TERMS:
                    if 1 <= len(skill.split()) <= 5:
                        skills.add(skill)
    
    return skills


def extract_named_entities(text: str) -> Set[str]:
    """
    Extract named entities that represent skills/tools.
    """
    doc = nlp(text)
    skills = set()
    
    for ent in doc.ents:
        # Only PRODUCT entities (tools, software, equipment)
        if ent.label_ == "PRODUCT":
            ent_text = ent.text.strip()
            ent_lower = ent_text.lower()
            
            # Skip if blacklisted
            if ent_lower in NON_SKILL_TERMS:
                continue
            
            # Skip if date/location
            if is_date_or_location_fragment(ent_text):
                continue
            
            # Skip very long entities
            if len(ent_text.split()) > 5:
                continue
            
            # Must be at least 2 characters
            if len(ent_text) >= 2:
                skills.add(ent_lower)
    
    return skills


def extract_technical_acronyms(text: str) -> Set[str]:
    """
    Extract all-caps acronyms that are likely skills.
    """
    skills = set()
    
    # Find all caps words (2-8 characters to catch things like SQL, API, FAISS, OpenCV)
    acronyms = re.findall(r'\b[A-Z]{2,8}\b', text)
    
    for acronym in acronyms:
        acronym_lower = acronym.lower()
        
        # Skip if blacklisted
        if acronym_lower in NON_SKILL_TERMS:
            continue
        
        # Skip if it's just a month abbreviation
        if acronym_lower in ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']:
            continue
        
        # Look for it near skill keywords or in skill section context
        pattern = r'(?:skills?|tools?|technologies?|platforms?|languages?|using|with|implemented|science|ml|developer)[\s\w,&:]*\b' + re.escape(acronym) + r'\b'
        if re.search(pattern, text, re.IGNORECASE):
            skills.add(acronym_lower)
    
    return skills


def extract_camelcase_and_special_terms(text: str) -> Set[str]:
    """
    Extract CamelCase terms and special naming patterns.
    """
    skills = set()
    camelcase = re.findall(r'\b[A-Z][a-z]*[A-Z][A-Za-z]*\b', text)
    
    for term in camelcase:
        term_lower = term.lower()
        
        # Skip if blacklisted
        if term_lower in NON_SKILL_TERMS:
            continue
        
        # Skip if date/location
        if is_date_or_location_fragment(term):
            continue
        
        # Reasonable length
        if 2 <= len(term) <= 20:
            skills.add(term_lower)
    
    return skills


def clean_and_filter_skills(skills: Set[str]) -> List[str]:
    """
    Final cleaning and filtering to remove noise.
    """
    cleaned = set()
    
    for skill in skills:
        # Remove newlines and extra whitespace
        skill = re.sub(r'\s+', ' ', skill.strip())
        
        # Skip if empty
        if not skill:
            continue
        
        # Skip if in blacklist
        if skill.lower() in NON_SKILL_TERMS:
            continue
        
        # Skip if date or location
        if is_date_or_location_fragment(skill):
            continue
        
        # Skip if contains problematic special characters (but allow +, #, -, /, .)
        if re.search(r'[§•()\[\]{}@$%^&*]', skill):
            continue
        
        # Skip if too long (likely a sentence fragment)
        if len(skill.split()) > 6:
            continue
        
        # Skip if empty or no letters
        if not re.search(r'[a-zA-Z]', skill):
            continue
        
        # Skip pure numbers or years
        if re.match(r'^\d+$', skill) or re.match(r'^\d{4}$', skill):
            continue
        
        # Skip single letters (unless it's known like 'c' or 'r')
        if len(skill) == 1 and skill.lower() not in ['c', 'r']:
            continue
        
        # Common known skills that should always be included (even if lowercase)
        known_skills = {
            'python', 'java', 'javascript', 'c++', 'c#', 'c', 'r', 'html', 'css', 'php', 'sql',
            'ruby', 'go', 'rust', 'swift', 'kotlin', 'scala', 'perl', 'bash', 'shell',
            'git', 'github', 'gitlab', 'linux', 'unix', 'windows', 'docker', 'kubernetes',
            'hadoop', 'spark', 'kafka', 'redis', 'mongodb', 'postgresql', 'mysql', 'oracle',
            'numpy', 'pandas', 'scipy', 'matplotlib', 'sklearn', 'tensorflow', 'pytorch', 'keras',
            'opencv', 'pyspark', 'fastapi', 'flask', 'django', 'react', 'angular', 'vue',
            'node.js', 'express', 'spring', 'hibernate', 'aws', 'azure', 'gcp',
            'faiss', 'streamlit', 'tableau', 'powerbi', 'excel', 'jira', 'confluence'
        }
        
        skill_lower = skill.lower()
        
        # If it's a known skill, add it
        if skill_lower in known_skills:
            cleaned.add(skill_lower)
            continue
        
        # For unknown skills, apply stricter rules
        # Skip if starts with lowercase (likely a fragment) unless it has special chars
        if skill[0].islower() and '-' not in skill and '/' not in skill and '.' not in skill:
            continue
        
        cleaned.add(skill_lower)
    
    return sorted(cleaned)


def extract_skills_dynamic(text: str) -> List[str]:
    """
    Main function for domain-agnostic skill extraction.
    Balanced approach - extracts skills without being too restrictive.
    """
    all_skills = set()
    
    # Strategy 1: Extract from explicit skill listings (most reliable)
    all_skills.update(extract_from_explicit_skill_listings(text))
    
    # Strategy 2: Extract proper nouns in skill contexts
    all_skills.update(extract_proper_nouns_in_skill_context(text))
    
    # Strategy 3: Extract from action contexts
    all_skills.update(extract_skills_from_action_contexts(text))
    
    # Strategy 4: Extract named entities (PRODUCT only)
    all_skills.update(extract_named_entities(text))
    
    # Strategy 5: Extract technical acronyms in context
    all_skills.update(extract_technical_acronyms(text))
    
    # Strategy 6: Extract CamelCase and special terms
    all_skills.update(extract_camelcase_and_special_terms(text))
    
    # Clean and filter
    return clean_and_filter_skills(all_skills)


def extract_skills_with_context_dynamic(text: str) -> Dict[str, List[str]]:
    """
    Extract skills with context (sentences where they appear).
    """
    skills = extract_skills_dynamic(text)
    skills_context = {}
    
    doc = nlp(text)
    
    for skill in skills:
        # Find sentences containing this skill (case-insensitive)
        skill_pattern = re.compile(r'\b' + re.escape(skill) + r'\b', re.IGNORECASE)
        
        for sent in doc.sents:
            if skill_pattern.search(sent.text):
                if skill not in skills_context:
                    skills_context[skill] = []
                # Limit to 3 contexts per skill to avoid bloat
                if len(skills_context[skill]) < 3:
                    skills_context[skill].append(sent.text.strip())
    
    return skills_context