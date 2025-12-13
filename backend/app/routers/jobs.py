from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import asyncio
import uuid
import json

from ..database import get_db, SessionLocal
from ..models import Job
from ..schemas import JobSearchRequest, JobSearchResponse, JobResponse, Platform
from ..scrapers.linkedin import LinkedInScraper
from ..scrapers.glassdoor import GlassdoorScraper

router = APIRouter(prefix="/api/jobs", tags=["jobs"])


@router.post("/search", response_model=JobSearchResponse)
async def search_jobs(request: JobSearchRequest, db: Session = Depends(get_db)):
    all_jobs = []
    tasks = []

    job_type = request.job_type.value if request.job_type else "all"

    # Create scraping tasks based on selected platforms
    if Platform.LINKEDIN in request.platforms:
        tasks.append(scrape_linkedin(request.query, request.location, job_type))

    if Platform.GLASSDOOR in request.platforms:
        tasks.append(scrape_glassdoor(request.query, request.location, job_type))

    # Run scrapers concurrently
    results = await asyncio.gather(*tasks, return_exceptions=True)

    for result in results:
        if isinstance(result, list):
            all_jobs.extend(result)
        elif isinstance(result, Exception):
            print(f"Scraping error: {result}")

    # Save jobs to database and prepare response
    job_responses = []
    for job_data in all_jobs:
        # Check if job already exists
        existing = db.query(Job).filter(Job.url == job_data["url"]).first()

        if existing:
            job = existing
        else:
            job = Job(
                id=str(uuid.uuid4()),
                title=job_data["title"],
                company=job_data["company"],
                location=job_data.get("location"),
                job_type=job_data.get("job_type"),
                salary_range=job_data.get("salary_range"),
                description=job_data.get("description"),
                url=job_data["url"],
                platform=job_data["platform"],
                posted_date=job_data.get("posted_date"),
            )
            db.add(job)

        job_responses.append(JobResponse.model_validate(job))

    db.commit()

    return JobSearchResponse(jobs=job_responses, total=len(job_responses))


@router.post("/search/stream")
async def search_jobs_stream(request: JobSearchRequest):
    """Stream job results as they're found using Server-Sent Events"""

    async def event_generator():
        job_type = request.job_type.value if request.job_type else "all"
        db = SessionLocal()

        try:
            # Send start event
            yield f"data: {json.dumps({'type': 'start', 'platforms': [p.value for p in request.platforms]})}\n\n"

            async def scrape_and_stream(platform: str, scraper_func):
                try:
                    jobs = await scraper_func(request.query, request.location, job_type)
                    return platform, jobs
                except Exception as e:
                    print(f"{platform} error: {e}")
                    return platform, []

            tasks = []
            if Platform.LINKEDIN in request.platforms:
                tasks.append(scrape_and_stream("linkedin", scrape_linkedin))
            if Platform.GLASSDOOR in request.platforms:
                tasks.append(scrape_and_stream("glassdoor", scrape_glassdoor))

            # Process results as they complete
            for coro in asyncio.as_completed(tasks):
                platform, jobs = await coro

                # Save to database and send results
                saved_jobs = []
                for job_data in jobs:
                    existing = db.query(Job).filter(Job.url == job_data["url"]).first()

                    if existing:
                        job = existing
                    else:
                        job = Job(
                            id=str(uuid.uuid4()),
                            title=job_data["title"],
                            company=job_data["company"],
                            location=job_data.get("location"),
                            job_type=job_data.get("job_type"),
                            salary_range=job_data.get("salary_range"),
                            description=job_data.get("description"),
                            url=job_data["url"],
                            platform=job_data["platform"],
                            posted_date=job_data.get("posted_date"),
                        )
                        db.add(job)

                    saved_jobs.append(JobResponse.model_validate(job).model_dump())

                db.commit()

                # Send platform results
                yield f"data: {json.dumps({'type': 'jobs', 'platform': platform, 'jobs': saved_jobs, 'count': len(saved_jobs)})}\n\n"

            # Send completion event
            yield f"data: {json.dumps({'type': 'done'})}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
        finally:
            db.close()

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )


async def scrape_linkedin(query: str, location: str | None, job_type: str) -> list[dict]:
    scraper = LinkedInScraper()
    return await scraper.search_jobs(query, location, job_type)


async def scrape_glassdoor(query: str, location: str | None, job_type: str) -> list[dict]:
    scraper = GlassdoorScraper()
    return await scraper.search_jobs(query, location, job_type)


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(job_id: str, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # If no description, try to fetch it
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

    return JobResponse.model_validate(job)
