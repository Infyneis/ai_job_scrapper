from openai import OpenAI, APIError, AuthenticationError, RateLimitError
import json
from ..config import get_settings


def truncate_text(text: str, max_chars: int = 4000) -> str:
    """Truncate text to reduce token usage while keeping important content."""
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "\n... [truncated for length]"


class OpenRouterService:
    # List of free models to try in order
    FREE_MODELS = [
        "google/gemini-2.0-flash-exp:free",
        "meta-llama/llama-3.2-3b-instruct:free",
        "qwen/qwen-2-7b-instruct:free",
        "mistralai/mistral-7b-instruct:free",
    ]

    def __init__(self):
        settings = get_settings()
        api_key = settings.open_router_api_key

        if not api_key:
            raise ValueError("OPEN_ROUTER_API_KEY is not set in .env file")

        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        )

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

Respond with ONLY a valid JSON object (no markdown, no explanation):
{{
    "match_percentage": <number 0-100>,
    "matching_skills": ["skill1", "skill2", ...],
    "missing_skills": ["skill1", "skill2", ...],
    "recommendations": ["actionable tip 1", "actionable tip 2", "actionable tip 3"]
}}"""

        # Try each model until one works
        last_error = None
        for model in self.FREE_MODELS:
            try:
                print(f"Trying model: {model}")

                completion = self.client.chat.completions.create(
                    extra_headers={
                        "HTTP-Referer": "http://localhost:3000",
                        "X-Title": "Job Scraper",
                    },
                    model=model,
                    messages=[
                        {
                            "role": "user",
                            "content": prompt,
                        }
                    ],
                )

                result_text = completion.choices[0].message.content.strip()
                print(f"Success with {model}! Response: {len(result_text)} chars")

                # Clean up markdown if present
                if result_text.startswith("```"):
                    result_text = result_text.split("```")[1]
                    if result_text.startswith("json"):
                        result_text = result_text[4:]
                    result_text = result_text.strip()

                result = json.loads(result_text)

                return {
                    "match_percentage": min(100, max(0, int(result.get("match_percentage", 0)))),
                    "matching_skills": result.get("matching_skills", [])[:10],
                    "missing_skills": result.get("missing_skills", [])[:10],
                    "recommendations": result.get("recommendations", [])[:5],
                }

            except json.JSONDecodeError as e:
                print(f"JSON parsing error with {model}: {e}")
                # Try next model, maybe it formats better
                last_error = str(e)
                continue

            except RateLimitError as e:
                print(f"Rate limit on {model}, trying next...")
                last_error = str(e)
                continue

            except AuthenticationError as e:
                print(f"Authentication error: {e}")
                return {
                    "match_percentage": 0,
                    "matching_skills": [],
                    "missing_skills": [],
                    "recommendations": [
                        "API authentication failed. Check your OPEN_ROUTER_API_KEY."
                    ],
                }

            except APIError as e:
                error_msg = str(e)
                if "429" in error_msg or "rate" in error_msg.lower():
                    print(f"Rate limit on {model}, trying next...")
                    last_error = error_msg
                    continue
                print(f"API error: {e}")
                return {
                    "match_percentage": 0,
                    "matching_skills": [],
                    "missing_skills": [],
                    "recommendations": [f"API error: {error_msg[:150]}"],
                }

            except Exception as e:
                error_str = str(e)
                error_type = type(e).__name__
                print(f"Unexpected error ({error_type}): {error_str}")
                last_error = error_str
                continue

        # All models failed
        return {
            "match_percentage": 0,
            "matching_skills": [],
            "missing_skills": [],
            "recommendations": [
                "All free AI models are currently rate-limited.",
                "Please try again in a few minutes, or add credits at openrouter.ai/settings/credits"
            ],
        }
