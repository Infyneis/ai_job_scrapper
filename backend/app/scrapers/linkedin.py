from typing import Optional
from .base import BaseScraper
import urllib.parse


class LinkedInScraper(BaseScraper):
    BASE_URL = "https://www.linkedin.com/jobs/search"

    def _build_search_url(
        self,
        query: str,
        location: Optional[str] = None,
        job_type: Optional[str] = None,
    ) -> str:
        params = {
            "keywords": query,
            "trk": "public_jobs_jobs-search-bar_search-submit",
            "position": 1,
            "pageNum": 0,
        }

        if location:
            params["location"] = location

        if job_type and job_type != "all":
            job_type_map = {
                "remote": "2",
                "onsite": "1",
                "hybrid": "3",
            }
            if job_type in job_type_map:
                params["f_WT"] = job_type_map[job_type]

        return f"{self.BASE_URL}?{urllib.parse.urlencode(params)}"

    async def search_jobs(
        self,
        query: str,
        location: Optional[str] = None,
        job_type: Optional[str] = None,
    ) -> list[dict]:
        jobs = []

        try:
            await self.init_browser()
            url = self._build_search_url(query, location, job_type)
            await self.page.goto(url, wait_until="domcontentloaded")
            await self.random_delay(2, 4)

            # Scroll to load more jobs
            for _ in range(3):
                await self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await self.random_delay(1, 2)

            # Get job cards
            job_cards = await self.page.query_selector_all(".base-card")

            for card in job_cards[:20]:  # Limit to 20 jobs
                try:
                    title_elem = await card.query_selector(".base-search-card__title")
                    company_elem = await card.query_selector(".base-search-card__subtitle")
                    location_elem = await card.query_selector(".job-search-card__location")
                    link_elem = await card.query_selector("a.base-card__full-link")
                    date_elem = await card.query_selector("time")

                    title = await title_elem.inner_text() if title_elem else ""
                    company = await company_elem.inner_text() if company_elem else ""
                    job_location = await location_elem.inner_text() if location_elem else ""
                    link = await link_elem.get_attribute("href") if link_elem else ""
                    posted_date = await date_elem.get_attribute("datetime") if date_elem else ""

                    if title and link:
                        jobs.append({
                            "title": title.strip(),
                            "company": company.strip(),
                            "location": job_location.strip(),
                            "url": link.split("?")[0] if link else "",
                            "posted_date": posted_date,
                            "platform": "linkedin",
                            "job_type": job_type if job_type != "all" else None,
                            "salary_range": None,
                            "description": None,
                        })
                except Exception:
                    continue

        except Exception as e:
            print(f"LinkedIn scraping error: {e}")
        finally:
            await self.close_browser()

        return jobs

    async def get_job_details(self, job_url: str) -> dict:
        details = {}

        try:
            await self.init_browser()
            await self.page.goto(job_url, wait_until="domcontentloaded")
            await self.random_delay(2, 3)

            # Try to get job description
            desc_elem = await self.page.query_selector(".description__text")
            if desc_elem:
                details["description"] = await desc_elem.inner_text()

            # Try to get salary if available
            salary_elem = await self.page.query_selector(".salary")
            if salary_elem:
                details["salary_range"] = await salary_elem.inner_text()

        except Exception as e:
            print(f"Error getting job details: {e}")
        finally:
            await self.close_browser()

        return details
