from pydantic import (
    BaseModel,
    EmailStr,
    Field
)

from typing import Optional, List, Dict
from datetime import datetime



class ContactInfoSchema(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    linkedin: Optional[str] = None
    github: Optional[str] = None
    portfolio_url: Optional[str] = None


class WorkExperienceItemSchema(BaseModel):
    company: Optional[str] = None
    role: Optional[str] = None
    location: Optional[str] = None
    start_date: Optional[str] = None  
    end_date: Optional[str] = None    
    duration_months: Optional[int] = None
    responsibilities: List[str] = Field(default_factory=list)
    description: Optional[str] = None


class EducationItemSchema(BaseModel):
    institution: Optional[str] = None
    degree: Optional[str] = None
    major: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    gpa: Optional[str] = None
    location: Optional[str] = None
    relevant_coursework: List[str] = Field(default_factory=list)

class SkillItemSchema(BaseModel):
    name: str
    proficiency: Optional[str] = None

class SkillSetSchema(BaseModel):
    technical: List[SkillItemSchema] = Field(default_factory=list)
    soft: List[str] = Field(default_factory=list)
    tools: List[SkillItemSchema] = Field(default_factory=list)
    languages: List[str] = Field(default_factory=list)


class ProjectItemSchema(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    technologies_used: List[str] = Field(default_factory=list)
    link: Optional[str] = None
    repo_link: Optional[str] = None


class CertificationItemSchema(BaseModel):
    name: Optional[str] = None
    issuer: Optional[str] = None
    issue_date: Optional[str] = None
    expiration_date: Optional[str] = None
    credential_id: Optional[str] = None
    credential_url: Optional[str] = None


class AwardItemSchema(BaseModel):
    name: Optional[str] = None
    issuer: Optional[str] = None
    date: Optional[str] = None
    description: Optional[str] = None

class ResumeExtractedData(BaseModel):
    contact_info: Optional[ContactInfoSchema] = None
    summary: Optional[str] = None
    work_experience: List[WorkExperienceItemSchema] = Field(default_factory=list)
    education: List[EducationItemSchema] = Field(default_factory=list)
    skills: Optional[SkillSetSchema] = None
    projects: List[ProjectItemSchema] = Field(default_factory=list)
    certifications: List[CertificationItemSchema] = Field(default_factory=list)
    awards: List[AwardItemSchema] = Field(default_factory=list)


class UpskillSuggestionItemSchema(BaseModel):
    skill: str
    reason: str
    resources: List[str] = Field(default_factory=list)

class LLMAnalysisSchema(BaseModel):
    resume_rating: Optional[float] = Field(None, ge=1, le=10)
    overall_feedback: Optional[str] = None
    strength_areas: List[str] = Field(default_factory=list)
    improvement_areas: List[str] = Field(default_factory=list)
    upskill_suggestions: List[UpskillSuggestionItemSchema] = Field(default_factory=list)
    suggested_keywords_for_ats: List[str] = Field(default_factory=list)
    potential_roles: List[str] = Field(default_factory=list)


class ResumeReadSchema(BaseModel):
    id: int
    file_name: str
    uploaded_at: datetime
    raw_text: Optional[str] = None

    contact_info: Optional[ContactInfoSchema] = None
    summary: Optional[str] = None
    work_experience: List[WorkExperienceItemSchema] = Field(default_factory=list)
    education: List[EducationItemSchema] = Field(default_factory=list)
    skills: Optional[SkillSetSchema] = None
    projects: List[ProjectItemSchema] = Field(default_factory=list)
    certifications: List[CertificationItemSchema] = Field(default_factory=list)
    awards: List[AwardItemSchema] = Field(default_factory=list)
    llm_analysis: Optional[LLMAnalysisSchema] = None

    class Config:
        from_attributes = True

class ResumeListDetailSchema(BaseModel):
    id: int
    file_name: str
    uploaded_at: datetime
    name: Optional[str] = None
    email: Optional[EmailStr] = None

    class Config:
        from_attributes = True