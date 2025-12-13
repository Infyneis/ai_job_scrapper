from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum


class JobType(str, Enum):
    REMOTE = "remote"
    ONSITE = "onsite"
    HYBRID = "hybrid"
    ALL = "all"


class Platform(str, Enum):
    LINKEDIN = "linkedin"
    GLASSDOOR = "glassdoor"


class JobSearchRequest(BaseModel):
    query: str
    location: Optional[str] = None
    job_type: JobType = JobType.ALL
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    platforms: list[Platform] = [Platform.LINKEDIN, Platform.GLASSDOOR]


class JobResponse(BaseModel):
    id: str
    title: str
    company: str
    location: Optional[str] = None
    job_type: Optional[str] = None
    salary_range: Optional[str] = None
    description: Optional[str] = None
    url: str
    platform: str
    posted_date: Optional[str] = None

    class Config:
        from_attributes = True


class JobSearchResponse(BaseModel):
    jobs: list[JobResponse]
    total: int


class ResumeAnalysisRequest(BaseModel):
    job_id: str


class SkillMatch(BaseModel):
    matching_skills: list[str]
    missing_skills: list[str]


class ResumeAnalysisResponse(BaseModel):
    match_percentage: int
    matching_skills: list[str]
    missing_skills: list[str]
    recommendations: list[str]
