from abc import ABC, abstractmethod
from typing import Optional
from playwright.async_api import async_playwright, Browser, Page
import asyncio


class BaseScraper(ABC):
    def __init__(self):
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None

    async def init_browser(self):
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(headless=True)
        self.page = await self.browser.new_page()
        self.page.set_default_timeout(60000)  # 60s timeout
        await self.page.set_viewport_size({"width": 1920, "height": 1080})
        await self.page.set_extra_http_headers({
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
        })

    async def close_browser(self):
        if self.browser:
            await self.browser.close()

    @abstractmethod
    async def search_jobs(
        self,
        query: str,
        location: Optional[str] = None,
        job_type: Optional[str] = None,
    ) -> list[dict]:
        pass

    @abstractmethod
    async def get_job_details(self, job_url: str) -> dict:
        pass

    async def random_delay(self, min_seconds: float = 1, max_seconds: float = 3):
        import random
        delay = random.uniform(min_seconds, max_seconds)
        await asyncio.sleep(delay)
