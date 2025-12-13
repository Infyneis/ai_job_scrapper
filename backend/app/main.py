from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .database import init_db
from .routers import jobs, analysis


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    init_db()
    yield
    # Shutdown


app = FastAPI(
    title="Job Scraper API",
    description="Search jobs from LinkedIn and Glassdoor with AI-powered resume matching",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(jobs.router)
app.include_router(analysis.router)


@app.get("/")
async def root():
    return {
        "message": "Job Scraper API",
        "docs": "/docs",
        "endpoints": {
            "search_jobs": "POST /api/jobs/search",
            "get_job": "GET /api/jobs/{job_id}",
            "analyze_resume": "POST /api/analysis/match",
        },
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}
