# FRAMEWORK PLACEHOLDER
# DO NOT DELETE
# IMPLEMENT IN FUTURE PHASE: Phase 4

"""
Web Tools Module

Utilities for web scraping and data extraction.
"""

import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional


class WebScraper:
    """Generic web scraper."""

    def __init__(self, headers: Optional[Dict] = None):
        self.session = requests.Session()
        self.session.headers.update(headers or {
            "User-Agent": "Mozilla/5.0"
        })

    def fetch(self, url: str) -> Optional[str]:
        """Fetch HTML content from URL."""
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return response.text
        except Exception:
            return None

    def parse(self, html: str) -> BeautifulSoup:
        """Parse HTML content."""
        return BeautifulSoup(html, "html.parser")

    def extract_links(self, soup: BeautifulSoup) -> List[str]:
        """Extract all links from parsed HTML."""
        return [a["href"] for a in soup.find_all("a", href=True)]

    def extract_text(self, soup: BeautifulSoup, selector: str) -> Optional[str]:
        """Extract text using CSS selector."""
        element = soup.select_one(selector)
        return element.get_text(strip=True) if element else None
