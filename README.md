# 🔍 Job Scraper

A full-stack job scraping application that searches LinkedIn and Glassdoor, with AI-powered resume matching to help you find your perfect job.

![Tech Stack](https://img.shields.io/badge/Backend-FastAPI-009688?style=flat-square&logo=fastapi)
![Tech Stack](https://img.shields.io/badge/Frontend-Next.js-000000?style=flat-square&logo=next.js)
![Tech Stack](https://img.shields.io/badge/AI-Ollama-white?style=flat-square)
![Tech Stack](https://img.shields.io/badge/Scraping-Playwright-2EAD33?style=flat-square&logo=playwright)

## ✨ Features

- **🔎 Multi-platform Job Search** - Search jobs simultaneously on LinkedIn and Glassdoor
- **🎯 Smart Filters** - Filter by job type (remote/onsite/hybrid), salary range, and location
- **📄 Resume Analysis** - Upload your resume and get AI-powered matching insights
- **📊 Match Percentage** - See how well your skills match each job posting
- **💡 Recommendations** - Get actionable tips to improve your application
- **🦙 Local AI** - Uses Ollama for free, private, local AI processing
- **⚡ Progressive Loading** - Results stream in as they're found

## 🏗️ Architecture

```
job_scrapper/
├── 🐍 backend/              # FastAPI Python backend
│   ├── app/
│   │   ├── main.py          # App entry point
│   │   ├── config.py        # Configuration
│   │   ├── database.py      # SQLite setup
│   │   ├── models.py        # SQLAlchemy models
│   │   ├── schemas.py       # Pydantic schemas
│   │   ├── routers/
│   │   │   ├── jobs.py      # Job search endpoints
│   │   │   └── analysis.py  # Resume analysis endpoint
│   │   ├── scrapers/
│   │   │   ├── base.py      # Base scraper class
│   │   │   ├── linkedin.py  # LinkedIn scraper
│   │   │   └── glassdoor.py # Glassdoor scraper
│   │   └── services/
│   │       ├── ai_service.py     # AI integration (Ollama/OpenRouter)
│   │       └── resume_parser.py  # PDF/DOCX parsing
│   └── requirements.txt
│
├── ⚛️ frontend/             # Next.js React frontend
│   ├── src/
│   │   ├── app/
│   │   │   └── page.tsx     # Main search page
│   │   ├── components/
│   │   │   ├── SearchFilters.tsx
│   │   │   ├── JobCard.tsx
│   │   │   ├── JobList.tsx
│   │   │   ├── JobDrawer.tsx    # Job details drawer
│   │   │   └── ResumeAnalysis.tsx
│   │   └── lib/
│   │       └── api.ts       # API client
│   └── package.json
│
├── 🚀 start.sh              # One-click startup script
└── 📖 README.md
```

## 🚀 Quick Start

### Prerequisites

- **Python 3.12+** - [Download Python](https://www.python.org/downloads/)
- **Node.js 18+** - [Download Node.js](https://nodejs.org/)
- **Homebrew** (macOS) - [Install Homebrew](https://brew.sh/)

### One-Command Launch 🎯

```bash
./start.sh
```

This script automatically:
1. 🦙 Installs and starts Ollama (local AI)
2. 📦 Downloads the llama3.2 model if needed
3. 🐍 Sets up Python virtual environment
4. 📚 Installs all dependencies
5. 🚀 Starts backend on http://localhost:8000
6. ⚛️ Starts frontend on http://localhost:3000
7. 🌐 Opens your browser

Press `Ctrl+C` to stop all services.

### Manual Setup

<details>
<summary>Click to expand manual setup instructions</summary>

#### 1. Install Ollama

```bash
# macOS
brew install ollama

# Linux
curl -fsSL https://ollama.ai/install.sh | sh
```

Start Ollama and download the model:
```bash
ollama serve &
ollama pull llama3.2
```

#### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium

# Copy environment file
cp .env.example .env

# Start the server
uvicorn app.main:app --reload --port 8000
```

#### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start the development server
npm run dev
```

</details>

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the `backend/` directory:

```env
# Optional: OpenRouter API key for cloud AI fallback
OPEN_ROUTER_API_KEY=your_key_here

# Database path (default: SQLite)
DATABASE_URL=sqlite:///./jobs.db
```

### AI Providers

The app uses a fallback chain for AI processing:

1. **🦙 Ollama (Primary)** - Free, local, private
   - Model: `llama3.2` (3.2B parameters)
   - Runs entirely on your machine
   - No API costs or rate limits

2. **☁️ OpenRouter (Fallback)** - Cloud API
   - Used if Ollama is not available
   - Requires API key from [openrouter.ai](https://openrouter.ai)
   - Free tier available with rate limits

## 📖 Usage

### 1. Search for Jobs

- Enter a job title or keywords (e.g., "Software Engineer")
- Select location (e.g., "France", "Remote")
- Choose job type: Remote, On-site, or Hybrid
- Optionally set salary range
- Click **Search**

Jobs will stream in progressively as each platform responds.

### 2. View Job Details

Click on any job card to open the details drawer showing:
- Full job description
- Company information
- Salary range (if available)
- Direct link to apply

### 3. Analyze Resume Match

1. Click on a job to open the drawer
2. Upload your resume (PDF or DOCX)
3. Click **Analyze Match**
4. View your results:
   - **Match Percentage** - How well you fit
   - **Matching Skills** - Skills you have
   - **Missing Skills** - Skills to develop
   - **Recommendations** - Tips to improve your application

## 🛠️ API Endpoints

### Job Search

```http
POST /api/jobs/search
Content-Type: application/json

{
  "query": "Software Engineer",
  "location": "France",
  "job_type": "remote",
  "salary_min": 50000,
  "salary_max": 100000,
  "platforms": ["linkedin", "glassdoor"]
}
```

### Streaming Search

```http
POST /api/jobs/search/stream
Content-Type: application/json

# Returns Server-Sent Events (SSE)
```

### Resume Analysis

```http
POST /api/analysis/match
Content-Type: multipart/form-data

job_id: <uuid>
resume: <file>
```

### API Documentation

Interactive API docs available at: http://localhost:8000/docs

## 🐛 Troubleshooting

### Ollama not starting

```bash
# Check if port 11434 is in use
lsof -i :11434

# Restart Ollama
brew services restart ollama
```

### Scraping timeouts

The scrapers use Playwright with headless Chromium. If you experience timeouts:

1. Check your internet connection
2. Some job sites may block automated access
3. Try reducing the number of results

### Resume parsing issues

Supported formats:
- PDF (text-based, not scanned images)
- DOCX (Microsoft Word)

For best results, use a text-based PDF resume.

## 📁 Logs

Logs are stored in the `logs/` directory:
- `ollama.log` - Ollama service logs
- `backend.log` - FastAPI backend logs
- `frontend.log` - Next.js frontend logs

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is for personal/educational use. Be mindful of the terms of service of job platforms when scraping.

---

<p align="center">
  Made with ❤️ for job seekers everywhere
</p>
