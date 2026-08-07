import hashlib
import logging
import re
from datetime import datetime
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from enum import Enum

import requests
from bs4 import BeautifulSoup
from tenacity import retry, stop_after_attempt, wait_exponential

from backend.utils.database import get_db_session

logger = logging.getLogger(__name__)


class SourceType(str, Enum):
    GAZETTE = "gazette"
    DGT = "dgt"
    MINISTRY = "ministry"
    COURT = "court"
    RBI = "rbi"
    SEBI = "sebi"
    MCA = "mca"
    OTHER = "other"


class DocumentType(str, Enum):
    ACT = "act"
    RULE = "rule"
    NOTIFICATION = "notification"
    ORDER = "order"
    CIRCULAR = "circular"
    GUIDELINE = "guideline"
    SCHEME = "scheme"
    AMENDMENT = "amendment"
    JUDGMENT = "judgment"
    OTHER = "other"


@dataclass
class ScraperConfig:
    """Configuration for a government website scraper."""
    name: str
    base_url: str
    source_type: SourceType
    selectors: Dict[str, str] = field(default_factory=dict)
    headers: Dict[str, str] = field(default_factory=lambda: {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    })
    timeout: int = 30
    rate_limit_seconds: float = 2.0


@dataclass
class ScrapedDocument:
    """Represents a scraped government document."""
    title: str
    document_type: DocumentType
    source_type: SourceType
    source_url: str
    source_name: str
    content: str
    summary: Optional[str] = None
    jurisdiction: str = "India"
    ministry: Optional[str] = None
    act_number: Optional[str] = None
    gazette_date: Optional[datetime] = None
    effective_date: Optional[datetime] = None
    keywords: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    content_hash: Optional[str] = None
    scraped_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


class BaseGovtScraper:
    """Base class for government website scrapers."""

    def __init__(self, config: ScraperConfig):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update(config.headers)
        self._last_request_time = 0

    def _rate_limit(self):
        """Apply rate limiting between requests."""
        import time
        elapsed = time.time() - self._last_request_time
        if elapsed < self.config.rate_limit_seconds:
            time.sleep(self.config.rate_limit_seconds - elapsed)
        self._last_request_time = time.time()

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def _fetch(self, url: str, params: Optional[Dict] = None) -> requests.Response:
        """Fetch a URL with retry logic."""
        self._rate_limit()
        response = self.session.get(
            url,
            params=params,
            timeout=self.config.timeout
        )
        response.raise_for_status()
        return response

    def _parse_html(self, html: str) -> BeautifulSoup:
        """Parse HTML content."""
        return BeautifulSoup(html, "html.parser")

    def _extract_content(self, soup: BeautifulSoup, selector: str) -> Optional[str]:
        """Extract text content using CSS selector."""
        element = soup.select_one(selector)
        return element.get_text(strip=True) if element else None

    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """Extract all links from page."""
        links = []
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if href.startswith("http"):
                links.append(href)
            elif href.startswith("/"):
                links.append(f"{base_url.rstrip('/')}{href}")
        return links

    def _compute_hash(self, content: str) -> str:
        """Compute SHA256 hash of content."""
        return hashlib.sha256(content.encode()).hexdigest()

    def scrape(self) -> List[ScrapedDocument]:
        """Main scraping method - to be implemented by subclasses."""
        raise NotImplementedError

    def save_to_database(self, documents: List[ScrapedDocument]) -> int:
        """Save scraped documents to database."""
        session = get_db_session()
        saved_count = 0

        for doc in documents:
            doc.content_hash = self._compute_hash(doc.content)

            existing = session.query(GovtDocument).filter_by(
                content_hash=doc.content_hash
            ).first()

            if not existing:
                db_doc = GovtDocument(
                    title=doc.title,
                    document_type=doc.document_type.value,
                    source_type=doc.source_type.value,
                    source_url=doc.source_url,
                    source_name=doc.source_name,
                    content=doc.content,
                    summary=doc.summary,
                    jurisdiction=doc.jurisdiction,
                    ministry=doc.ministry,
                    act_number=doc.act_number,
                    gazette_date=doc.gazette_date,
                    effective_date=doc.effective_date,
                    keywords=",".join(doc.keywords),
                    metadata=doc.metadata,
                    content_hash=doc.content_hash,
                    scraped_at=doc.scraped_at,
                )
                session.add(db_doc)
                saved_count += 1
            else:
                existing.content = doc.content
                existing.summary = doc.summary
                existing.updated_at = datetime.utcnow()

        session.commit()
        return saved_count


class IndiaGazetteScraper(BaseGovtScraper):
    """Scraper for The Gazette of India."""

    def __init__(self):
        config = ScraperConfig(
            name="The Gazette of India",
            base_url="https://egazette.nic.in",
            source_type=SourceType.GAZETTE,
            selectors={
                "title": "h1.title",
                "content": "div.content",
                "date": "span.date",
            }
        )
        super().__init__(config)

    def scrape(self) -> List[ScrapedDocument]:
        """Scrape recent notifications from Gazette of India."""
        documents = []
        try:
            response = self._fetch(f"{self.config.base_url}/SearchAct.aspx")
            soup = self._parse_html(response.text)

            for item in soup.select(".act-list .act-item"):
                title = self._extract_content(item, ".act-title")
                link = item.select_one("a")["href"]

                if title and link:
                    doc_response = self._fetch(link)
                    doc_soup = self._parse_html(doc_response.text)
                    content = self._extract_content(doc_soup, self.config.selectors["content"]) or ""

                    documents.append(ScrapedDocument(
                        title=title,
                        document_type=self._detect_document_type(title),
                        source_type=self.config.source_type,
                        source_url=link,
                        source_name=self.config.name,
                        content=content,
                        content_hash=self._compute_hash(content),
                    ))

        except Exception as e:
            logger.error(f"Error scraping Gazette of India: {e}")

        return documents

    def _detect_document_type(self, title: str) -> DocumentType:
        """Detect document type from title."""
        title_lower = title.lower()
        if "act" in title_lower:
            return DocumentType.ACT
        elif "notification" in title_lower:
            return DocumentType.NOTIFICATION
        elif "order" in title_lower:
            return DocumentType.ORDER
        elif "rule" in title_lower:
            return DocumentType.RULE
        elif "amendment" in title_lower:
            return DocumentType.AMENDMENT
        return DocumentType.OTHER


class DGTScraper(BaseGovtScraper):
    """Scraper for Directorate General of Trade Remedies."""

    def __init__(self):
        config = ScraperConfig(
            name="DGTR",
            base_url="https://www.dgtr.gov.in",
            source_type=SourceType.DGT,
            selectors={
                "notice": ".views-row .notice-title",
                "content": ".field-name-body",
            }
        )
        super().__init__(config)

    def scrape(self) -> List[ScrapedDocument]:
        """Scrape anti-dumping and safeguard notices."""
        documents = []
        try:
            for page in ["anti-dumping", "safeguard", "countervailing"]:
                response = self._fetch(
                    f"{self.config.base_url}/notices/{page}",
                    params={"page": 1}
                )
                soup = self._parse_html(response.text)

                for notice in soup.select(".notice-item"):
                    title = self._extract_content(notice, "h3")
                    link = notice.select_one("a")["href"]

                    if title:
                        doc = ScrapedDocument(
                            title=title,
                            document_type=DocumentType.NOTIFICATION,
                            source_type=self.config.source_type,
                            source_url=link,
                            source_name=self.config.name,
                            content="",
                        )
                        documents.append(doc)

        except Exception as e:
            logger.error(f"Error scraping DGTR: {e}")

        return documents


class MinistryOfLawScraper(BaseGovtScraper):
    """Scraper for Ministry of Law and Justice."""

    def __init__(self):
        config = ScraperConfig(
            name="Ministry of Law and Justice",
            base_url="https://legalaffairs.gov.in",
            source_type=SourceType.MINISTRY,
        )
        super().__init__(config)

    def scrape(self) -> List[ScrapedDocument]:
        """Scrape acts and bills from Ministry website."""
        documents = []
        try:
            response = self._fetch(f"{self.config.base_url}/acts")
            soup = self._parse_html(response.text)

            for link in self._extract_links(soup, self.config.base_url):
                if any(x in link.lower() for x in ["act", "bill", "ordinance"]):
                    try:
                        doc_response = self._fetch(link)
                        doc_soup = self._parse_html(doc_response.text)
                        content = self._extract_content(doc_soup, "article") or ""

                        title = self._extract_content(doc_soup, "h1") or link.split("/")[-1]

                        documents.append(ScrapedDocument(
                            title=title,
                            document_type=DocumentType.ACT,
                            source_type=self.config.source_type,
                            source_url=link,
                            source_name=self.config.name,
                            content=content,
                            content_hash=self._compute_hash(content),
                        ))
                    except Exception as e:
                        logger.warning(f"Failed to fetch {link}: {e}")

        except Exception as e:
            logger.error(f"Error scraping Ministry of Law: {e}")

        return documents


class RBIScraper(BaseGovtScraper):
    """Scraper for Reserve Bank of India circulars and notifications."""

    def __init__(self):
        config = ScraperConfig(
            name="Reserve Bank of India",
            base_url="https://www.rbi.org.in",
            source_type=SourceType.RBI,
            selectors={
                "circular": ".CircularsList .item",
                "content": ".content-area",
            }
        )
        super().__init__(config)

    def scrape(self) -> List[ScrapedDocument]:
        """Scrape RBI circulars and master directions."""
        documents = []
        try:
            response = self._fetch(f"{self.config.base_url}/Scripts/Circulars.aspx")
            soup = self._parse_html(response.text)

            for item in soup.select(".circular-item"):
                title = self._extract_content(item, ".circular-title")
                link = item.select_one("a")["href"]
                date_text = self._extract_content(item, ".circular-date")

                if title:
                    gazette_date = self._parse_date(date_text) if date_text else None

                    documents.append(ScrapedDocument(
                        title=title,
                        document_type=DocumentType.CIRCULAR,
                        source_type=self.config.source_type,
                        source_url=link,
                        source_name=self.config.name,
                        content="",
                        gazette_date=gazette_date,
                    ))

        except Exception as e:
            logger.error(f"Error scraping RBI: {e}")

        return documents

    def _parse_date(self, date_text: str) -> Optional[datetime]:
        """Parse date from Indian format."""
        formats = ["%d-%m-%Y", "%d/%m/%Y", "%B %d, %Y"]
        for fmt in formats:
            try:
                return datetime.strptime(date_text.strip(), fmt)
            except ValueError:
                continue
        return None


class SEBIScraper(BaseGovtScraper):
    """Scraper for SEBI circulars and regulations."""

    def __init__(self):
        config = ScraperConfig(
            name="SEBI",
            base_url="https://www.sebi.gov.in",
            source_type=SourceType.SEBI,
        )
        super().__init__(config)

    def scrape(self) -> List[ScrapedDocument]:
        """Scrape SEBI circulars and regulations."""
        documents = []
        try:
            for section in ["circulars", "regulations"]:
                response = self._fetch(f"{self.config.base_url}/{section}")
                soup = self._parse_html(response.text)

                for item in soup.select(".document-item"):
                    title = self._extract_content(item, "h3") or self._extract_content(item, "a")
                    link = item.select_one("a")["href"]

                    if title:
                        doc_type = DocumentType.CIRCULAR if section == "circulars" else DocumentType.ACT

                        documents.append(ScrapedDocument(
                            title=title,
                            document_type=doc_type,
                            source_type=self.config.source_type,
                            source_url=link,
                            source_name=self.config.name,
                            content="",
                        ))

        except Exception as e:
            logger.error(f"Error scraping SEBI: {e}")

        return documents


class MCAScraper(BaseGovtScraper):
    """Scraper for Ministry of Corporate Affairs."""

    def __init__(self):
        config = ScraperConfig(
            name="MCA",
            base_url="https://www.mca.gov.in",
            source_type=SourceType.MCA,
        )
        super().__init__(config)

    def scrape(self) -> List[ScrapedDocument]:
        """Scrape MCA notifications and forms."""
        documents = []
        try:
            response = self._fetch(f"{self.config.base_url}/content/mca/forms.html")
            soup = self._parse_html(response.text)

            for item in soup.select(".links-list a"):
                title = item.get_text(strip=True)
                link = item["href"]

                if title and link:
                    documents.append(ScrapedDocument(
                        title=title,
                        document_type=DocumentType.NOTIFICATION,
                        source_type=self.config.source_type,
                        source_url=link,
                        source_name=self.config.name,
                        content="",
                    ))

        except Exception as e:
            logger.error(f"Error scraping MCA: {e}")

        return documents


class GovtScraperFactory:
    """Factory to create government scrapers."""

    SCRAPERS = {
        "gazette": IndiaGazetteScraper,
        "dgtr": DGTScraper,
        "mca": MCAScraper,
        "rbi": RBIScraper,
        "sebi": SEBIScraper,
        "minlaw": MinistryOfLawScraper,
    }

    @classmethod
    def create_scraper(cls, source: str) -> Optional[BaseGovtScraper]:
        """Create a scraper for the given source."""
        scraper_class = cls.SCRAPERS.get(source.lower())
        return scraper_class() if scraper_class else None

    @classmethod
    def get_available_sources(cls) -> List[str]:
        """Get list of available scraper sources."""
        return list(cls.SCRAPERS.keys())

    @classmethod
    def create_all_scrapers(cls) -> List[BaseGovtScraper]:
        """Create instances of all available scrapers."""
        return [scraper_class() for scraper_class in cls.SCRAPERS.values()]


def run_full_scrape() -> Dict[str, List[ScrapedDocument]]:
    """Run all scrapers and return collected documents."""
    results = {}
    scrapers = GovtScraperFactory.create_all_scrapers()

    for scraper in scrapers:
        logger.info(f"Running {scraper.config.name} scraper...")
        try:
            documents = scraper.scrape()
            results[scraper.config.name] = documents
            logger.info(f"  Found {len(documents)} documents")
        except Exception as e:
            logger.error(f"  Failed: {e}")
            results[scraper.config.name] = []

    return results
