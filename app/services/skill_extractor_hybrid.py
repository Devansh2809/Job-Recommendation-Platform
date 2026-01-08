import spacy
from spacy.matcher import PhraseMatcher
from typing import List, Set, Dict
import re

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

# Load skill dictionary
try:
    with open("app/data/skills.txt", encoding="utf-8") as f:
        SKILL_PATTERNS = [line.strip() for line in f if line.strip()]
except FileNotFoundError:
    SKILL_PATTERNS = []


def build_skill_matcher():
    """
    Build a PhraseMatcher for known skills.
    This matches exact phrases from skills.txt regardless of case.
    """
    matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
    patterns = [nlp.make_doc(skill) for skill in SKILL_PATTERNS]
    matcher.add("SKILLS", patterns)
    return matcher


# Initialize matcher once at module load
skill_matcher = build_skill_matcher()


def is_valid_skill(skill: str) -> bool:
    """
    Filter out invalid skills (too long, contains newlines, etc.)
    """
    # Remove any skill with newlines or tabs
    if '\n' in skill or '\t' in skill:
        return False
    
    # Skip if too long (likely a sentence, not a skill)
    if len(skill.split()) > 5:
        return False
    
    # Skip if contains special characters that shouldn't be in skills
    if re.search(r'[§•\(\)\[\]]', skill):
        return False
    
    # Skip if it's just punctuation
    if not re.search(r'[a-zA-Z]', skill):
        return False
    
    return True


def extract_skills_hybrid(text: str) -> List[str]:
    """
    Extract skills using hybrid approach with strict filtering.
    
    Returns sorted list of unique, clean skills.
    """
    doc = nlp(text)
    found_skills = set()
    
    # Method 1: PhraseMatcher for known skills (most reliable)
    matches = skill_matcher(doc)
    for match_id, start, end in matches:
        skill = doc[start:end].text.lower().strip()
        
        # Only add if it passes validation
        if is_valid_skill(skill):
            found_skills.add(skill)
    
    # Method 2: Extract noun chunks that look like technical skills
    for chunk in doc.noun_chunks:
        chunk_text = chunk.text.lower().strip()
        
        # Must pass validation
        if not is_valid_skill(chunk_text):
            continue
        
        # Check if it's in our known skills
        if chunk_text in [s.lower() for s in SKILL_PATTERNS]:
            found_skills.add(chunk_text)
    
    # Method 3: Extract entities that could be technical skills
    for ent in doc.ents:
        if ent.label_ in ["ORG", "PRODUCT"]:
            ent_lower = ent.text.lower().strip()
            
            # Must pass validation and be in known skills
            if is_valid_skill(ent_lower) and ent_lower in [s.lower() for s in SKILL_PATTERNS]:
                found_skills.add(ent_lower)
    
    return sorted(found_skills)


def extract_skills_with_context(text: str) -> Dict[str, List[str]]:
    """
    Extract skills with context showing where they appear.
    
    Returns: {skill: [list of sentences where it appears]}
    """
    doc = nlp(text)
    skills_with_context = {}
    
    matches = skill_matcher(doc)
    for match_id, start, end in matches:
        skill = doc[start:end].text.lower().strip()
        
        # Only process valid skills
        if not is_valid_skill(skill):
            continue
        
        # Get the sentence containing this skill
        try:
            sentence = doc[start:end].sent.text.strip()
            # Clean the sentence
            sentence = re.sub(r'\s+', ' ', sentence)
        except:
            # Fallback: get surrounding context
            context_start = max(0, start - 10)
            context_end = min(len(doc), end + 10)
            sentence = doc[context_start:context_end].text.strip()
        
        if skill not in skills_with_context:
            skills_with_context[skill] = []
        
        skills_with_context[skill].append(sentence)
    
    return skills_with_context