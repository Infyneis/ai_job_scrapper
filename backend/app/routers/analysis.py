from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Job
from ..schemas import ResumeAnalysisResponse
from ..services.ai_service import AIService
from ..services.resume_parser import extract_resume_text
from ..scrapers.linkedin import LinkedInScraper
from ..scrapers.glassdoor import GlassdoorScraper

router = APIRouter(prefix="/api/analysis", tags=["analysis"])


@router.post("/match", response_model=ResumeAnalysisResponse)
async def analyze_resume_match(
    job_id: str = Form(...),
    resume: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    # Get the job from database
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # If no description, fetch it
    if not job.description:
        if job.platform == "linkedin":
            scraper = LinkedInScraper()
            details = await scraper.get_job_details(job.url)
        else:
            scraper = GlassdoorScraper()
            details = await scraper.get_job_details(job.url)

        if details.get("description"):
            job.description = details["description"]
            db.commit()
        else:
            raise HTTPException(
                status_code=400,
                detail="Could not fetch job description for analysis"
            )

    # Parse resume
    try:
        file_content = await resume.read()
        resume_text = extract_resume_text(resume.filename, file_content)

        if not resume_text:
            raise HTTPException(
                status_code=400,
                detail="Could not extract text from resume"
            )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Analyze with AI (Ollama local or OpenRouter fallback)
    ai_service = AIService()
    result = await ai_service.analyze_resume_match(
        resume_text=resume_text,
        job_description=job.description,
        job_title=job.title,
    )

    return ResumeAnalysisResponse(**result)
