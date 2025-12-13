from openai import OpenAI
import json
import re
import httpx
from ..config import get_settings


def repair_json(text: str) -> str:
    """Attempt to fix common JSON errors from LLMs."""
    # Fix: array ending with } instead of ]
    # Pattern: ["item1", "item2"}  ->  ["item1", "item2"]
    text = re.sub(r'("\s*)\}(\s*[,\}])', r'\1]\2', text)

    # Fix: missing comma between array items
    text = re.sub(r'"\s*\n\s*"', '", "', text)

    # Fix: trailing comma before closing bracket/brace
    text = re.sub(r',\s*\]', ']', text)
    text = re.sub(r',\s*\}', '}', text)

    return text


def truncate_text(text: str, max_chars: int = 4000) -> str:
    """Truncate text to reduce token usage while keeping important content."""
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "\n... [truncated for length]"


def is_ollama_running() -> bool:
    """Check if Ollama is running locally."""
    try:
        response = httpx.get("http://localhost:11434/api/tags", timeout=2)
        return response.status_code == 200
    except Exception:
        return False


class AIService:
    def __init__(self):
        self.ollama_available = is_ollama_running()

        if self.ollama_available:
            print("Using Ollama (local) for AI")
            self.client = OpenAI(
                base_url="http://localhost:11434/v1",
                api_key="ollama",  # Ollama doesn't need a real key
            )
            self.model = "llama3.2"
        else:
            print("Ollama not available, using OpenRouter")
            settings = get_settings()
            api_key = settings.open_router_api_key

            if not api_key:
                raise ValueError("OPEN_ROUTER_API_KEY is not set and Ollama is not running")

            self.client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=api_key,
            )
            self.model = "google/gemini-2.0-flash-exp:free"

    async def analyze_resume_match(
        self,
        resume_text: str,
        job_description: str,
        job_title: str,
    ) -> dict:
        # Truncate inputs to reduce token usage
        resume_truncated = truncate_text(resume_text, 3500)
        job_truncated = truncate_text(job_description, 2500)

        prompt = f"""You are an expert HR analyst. Analyze how well this resume matches the job posting.

JOB TITLE: {job_title}

JOB DESCRIPTION:
{job_truncated}

RESUME:
{resume_truncated}

Respond with ONLY a valid JSON object (no markdown, no explanation, no text before or after):
{{
    "match_percentage": <number 0-100>,
    "matching_skills": ["skill1", "skill2", ...],
    "missing_skills": ["skill1", "skill2", ...],
    "recommendations": ["actionable tip 1", "actionable tip 2", "actionable tip 3"]
}}"""

        result_text = None
        try:
            print(f"Calling AI with model: {self.model}")
            print(f"Prompt length: {len(prompt)} chars")

            extra_headers = {}
            extra_kwargs = {}

            if not self.ollama_available:
                extra_headers = {
                    "HTTP-Referer": "http://localhost:3000",
                    "X-Title": "Job Scraper",
                }
                extra_kwargs["extra_headers"] = extra_headers
            else:
                # Ollama: longer timeout for complex prompts
                extra_kwargs["timeout"] = 120.0

            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                **extra_kwargs,
            )

            result_text = completion.choices[0].message.content
            if result_text is None:
                raise ValueError("AI returned empty response")

            result_text = result_text.strip()
            print(f"AI response received: {len(result_text)} chars")
            print(f"Response preview: {result_text[:200]}...")

            # Clean up markdown if present
            if result_text.startswith("```"):
                parts = result_text.split("```")
                if len(parts) >= 2:
                    result_text = parts[1]
                    if result_text.startswith("json"):
                        result_text = result_text[4:]
                    result_text = result_text.strip()

            # Try to find JSON in the response
            if not result_text.startswith("{"):
                # Look for JSON object in the text
                start = result_text.find("{")
                end = result_text.rfind("}") + 1
                if start != -1 and end > start:
                    result_text = result_text[start:end]

            # Try to repair common JSON errors from LLMs
            result_text = repair_json(result_text)

            result = json.loads(result_text)

            return {
                "match_percentage": min(100, max(0, int(result.get("match_percentage", 0)))),
                "matching_skills": result.get("matching_skills", [])[:10],
                "missing_skills": result.get("missing_skills", [])[:10],
                "recommendations": result.get("recommendations", [])[:5],
            }

        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            print(f"Raw response: {result_text[:1000] if result_text else 'N/A'}")
            return {
                "match_percentage": 0,
                "matching_skills": [],
                "missing_skills": [],
                "recommendations": ["Unable to parse AI response. Please try again."],
            }

        except Exception as e:
            error_str = str(e)
            error_type = type(e).__name__
            print(f"AI error ({error_type}): {error_str}")
            if result_text:
                print(f"Partial response: {result_text[:500]}")

            return {
                "match_percentage": 0,
                "matching_skills": [],
                "missing_skills": [],
                "recommendations": [f"AI error: {error_str[:100]}"],
            }
