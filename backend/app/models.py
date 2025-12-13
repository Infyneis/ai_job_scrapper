from sqlalchemy import Column, String, Integer, DateTime, Text
from sqlalchemy.sql import func
from .database import Base
import uuid


class Job(Base):
    __tablename__ = "jobs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False)
    company = Column(String, nullable=False)
    location = Column(String)
    job_type = Column(String)  # remote, onsite, hybrid
    salary_range = Column(String)
    description = Column(Text)
    url = Column(String, unique=True)
    platform = Column(String)  # linkedin, glassdoor
    posted_date = Column(String)
    created_at = Column(DateTime, default=func.now())
