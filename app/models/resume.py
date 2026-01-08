from pydantic import BaseModel
from typing import List, Optional, Dict


class Project(BaseModel):
    title: str
    technologies: str = ""
    description: str = ""


class Education(BaseModel):
    institution: str
    degree: str = ""
    details: str = ""


class ResumeProfile(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    skills: List[str] = []
    projects: List[Project] = []
    education: List[Education] = []
    coursework: List[str] = []
    raw_sections: Dict[str, Dict] = {}  # For debugging
    raw_text: str