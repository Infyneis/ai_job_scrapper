from typing import Optional
from .base import BaseScraper
import urllib.parse


class GlassdoorScraper(BaseScraper):
    BASE_URL = "https://www.glassdoor.com/Job/jobs.htm"

    def _build_search_url(
        self,
        query: str,
        location: Optional[str] = None,
        job_type: Optional[str] = None,
    ) -> str:
        params = {
            "sc.keyword": query,
        }

        if location:
            params["locT"] = "C"
            params["locKeyword"] = location

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

            # Handle cookie consent if present
            try:
                cookie_btn = await self.page.query_selector("#onetrust-accept-btn-handler")
                if cookie_btn:
                    await cookie_btn.click()
                    await self.random_delay(1, 2)
            except Exception:
                pass

            # Handle potential signup modal
            try:
                close_btn = await self.page.query_selector("[data-test='close-modal']")
                if close_btn:
                    await close_btn.click()
                    await self.random_delay(0.5, 1)
            except Exception:
                pass

            # Scroll to load jobs
            for _ in range(2):
                await self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await self.random_delay(1, 2)

            # Get job cards - Glassdoor uses various selectors
            job_cards = await self.page.query_selector_all("[data-test='jobListing']")

            if not job_cards:
                # Try alternative selector
                job_cards = await self.page.query_selector_all(".JobCard_jobCard__")

            for card in job_cards[:20]:  # Limit to 20 jobs
                try:
                    title_elem = await card.query_selector("[data-test='job-title']")
                    if not title_elem:
                        title_elem = await card.query_selector(".JobCard_jobTitle__")

                    company_elem = await card.query_selector("[data-test='employer-short-name']")
                    if not company_elem:
                        company_elem = await card.query_selector(".EmployerProfile_companyName__")

                    location_elem = await card.query_selector("[data-test='emp-location']")
                    if not location_elem:
                        location_elem = await card.query_selector(".JobCard_location__")

                    salary_elem = await card.query_selector("[data-test='detailSalary']")

                    link_elem = await card.query_selector("a")

                    title = await title_elem.inner_text() if title_elem else ""
                    company = await company_elem.inner_text() if company_elem else ""
                    job_location = await location_elem.inner_text() if location_elem else ""
                    salary = await salary_elem.inner_text() if salary_elem else None
                    link = await link_elem.get_attribute("href") if link_elem else ""

                    if title and link:
                        full_url = link if link.startswith("http") else f"https://www.glassdoor.com{link}"
                        jobs.append({
                            "title": title.strip(),
                            "company": company.strip(),
                            "location": job_location.strip(),
                            "url": full_url.split("?")[0],
                            "posted_date": None,
                            "platform": "glassdoor",
                            "job_type": job_type if job_type != "all" else None,
                            "salary_range": salary.strip() if salary else None,
                            "description": None,
                        })
                except Exception:
                    continue

        except Exception as e:
            print(f"Glassdoor scraping error: {e}")
        finally:
            await self.close_browser()

        return jobs

    async def get_job_details(self, job_url: str) -> dict:
        details = {}

        try:
            await self.init_browser()
            await self.page.goto(job_url, wait_until="domcontentloaded")
            await self.random_delay(2, 3)

            # Handle modals
            try:
                close_btn = await self.page.query_selector("[data-test='close-modal']")
                if close_btn:
                    await close_btn.click()
            except Exception:
                pass

            # Get job description
            desc_elem = await self.page.query_selector("[data-test='jobDescriptionContent']")
            if not desc_elem:
                desc_elem = await self.page.query_selector(".JobDetails_jobDescription__")

            if desc_elem:
                details["description"] = await desc_elem.inner_text()

        except Exception as e:
            print(f"Error getting Glassdoor job details: {e}")
        finally:
            await self.close_browser()

        return details
