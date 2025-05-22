"""
Asynchronous web crawler for efficiently crawling large websites.
Uses asyncio and aiohttp for concurrent requests.
"""

import time
import random
import logging
import asyncio
import threading
from datetime import datetime
from urllib.parse import urlparse, urljoin, urldefrag
from typing import Dict, Set, Optional, Tuple, Callable, TypeVar

import requests
import aiohttp
from bs4 import BeautifulSoup

from application.logger import get_logger, log_with_level

# Type aliases for clarity
URL = str
T = TypeVar("T")


class CrawlerConfig:
    """Configuration for the AsyncWebCrawler."""

    # Default user agent and headers for requests
    HEADERS: Dict[str, str] = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "DNT": "1",  # Do Not Track Request Header
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }

    def __init__(
        self,
        url: URL,
        max_concurrency: int = 10,
        delay_min: float = 0.5,
        delay_max: float = 2.0,
        link_callback: Optional[Callable[[URL], None]] = None,
        page_callback: Optional[Callable[[URL, Set[URL]], None]] = None,
        verbose: bool = False,
    ):
        """
        Initialize the crawler configuration.

        Args:
            url: The starting URL to crawl.
            max_concurrency: Maximum number of concurrent requests.
            delay_min: Minimum delay between requests.
            delay_max: Maximum delay between requests.
            link_callback: Callback for link processing.
            page_callback: Callback for page processing.
            verbose: Enable verbose logging.
        """
        self.url: URL = url
        self.domain: URL = url  # Add domain attribute for testing
        self.max_concurrency: int = max_concurrency
        self.delay_min: float = delay_min
        self.delay_max: float = delay_max
        self.link_callback: Optional[Callable[[URL], None]] = link_callback
        self.page_callback: Optional[Callable[[URL, Set[URL]], None]] = page_callback
        self.verbose: bool = verbose

    def _extract_domain(self, url: URL) -> URL:
        """
        Extract the base domain from a URL.

        Args:
            url: The URL to extract domain from.

        Returns:
            The domain.
        """
        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}"

    def is_valid_url(self, url: URL) -> bool:
        """
        Check if a URL is valid based on configuration.

        Args:
            url: The URL to check.

        Returns:
            True if valid, False otherwise.
        """
        if not url.startswith(("http://", "https://")):
            return False

        return True


class AsyncWebCrawler:
    """
    Asynchronous web crawler that uses aiohttp for concurrent requests.

    This crawler respects robots.txt, uses random delays between requests,
    and limits concurrent requests to be a good citizen.
    """

    # Create a class-level lock for thread-safe printing
    _print_lock = threading.Lock()

    def __init__(
        self,
        url: URL,
        max_concurrency: int = 10,
        delay_min: float = 0.5,
        delay_max: float = 2.0,
        verbose: bool = False,
    ):
        """
        Initialize the AsyncWebCrawler.

        Args:
            url: The starting URL to crawl.
            max_concurrency: Maximum number of concurrent requests.
            delay_min: Minimum delay between requests.
            delay_max: Maximum delay between requests.
            verbose: Enable verbose logging.
        """
        self.config: CrawlerConfig = CrawlerConfig(
            url=url,
            max_concurrency=max_concurrency,
            delay_min=delay_min,
            delay_max=delay_max,
            verbose=verbose,
        )
        self.log: Callable[[str, str, Optional[Tuple]], None] = self._build_logger()
        self.page_callback: Optional[Callable[[URL, Set[URL]], None]] = (
            None  # Callback for page processing
        )
        self.link_callback: Optional[Callable[[URL], None]] = (
            None  # Callback for link processing
        )

    def _build_logger(self) -> Callable[[str, str, Optional[Tuple]], None]:
        """
        Build a logger for the crawler.

        Returns:
            callable: A logging function.
        """
        logger = get_logger("AsyncWebCrawler")
        if self.config.verbose:
            logging.getLogger().setLevel(logging.DEBUG)

        def log(message: str, level: str, args: Optional[Tuple] = None) -> None:
            if args is None:
                args = ()

            if self.config.verbose:
                with AsyncWebCrawler._print_lock:
                    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
                    formatted_message = message % args if args else message
                    print(f"[{timestamp}] [{level}] {formatted_message}")

            # Use the centralized logging function
            log_with_level(logger, message, level, args)

        return log

    def set_link_callback(self, callback: Callable[[URL], None]) -> None:
        """
        Set a callback function for newly discovered links.

        Args:
            callback: Function to call with each new link.
        """
        self.config.link_callback = callback
        self.link_callback = callback  # Also set it directly on the crawler for testing

    def set_page_callback(self, callback: Callable[[URL, Set[URL]], None]) -> None:
        """
        Set a callback function for processed pages and their links.

        Args:
            callback: Function to call with each processed page and its links.
                The function should accept two arguments: (page_url, links).
        """
        self.config.page_callback = callback
        self.page_callback = callback  # Also set it directly on the crawler for testing

    def _process_page_callback(self, url: URL, links: Set[URL]) -> None:
        """
        Process a page callback if it exists.

        Args:
            url: The URL of the processed page.
            links: The links found on the page.
        """
        if self.page_callback:
            try:
                self.page_callback(url, links)
            except Exception as e:
                self.log(f"Error in page callback: {e}", "ERROR")
        elif self.config.page_callback:
            try:
                self.config.page_callback(url, links)
            except Exception as e:
                self.log(f"Error in page callback: {e}", "ERROR")

    def _normalize_url(self, url: URL, base_url: Optional[URL] = None) -> Optional[URL]:
        """
        Normalize a URL by removing fragments and ensuring it's absolute.

        Args:
            url: The URL to normalize.
            base_url: The base URL to join with relative URLs.

        Returns:
            Normalized URL or None if invalid.
        """
        if not url:
            return None

        # Handle special cases like mailto: or javascript: links
        if url.startswith(("mailto:", "javascript:", "tel:", "#")):
            return None

        # Make absolute URL if relative
        if base_url and not url.startswith(("http://", "https://")):
            url = urljoin(base_url, url)

        # Remove URL fragments
        url = urldefrag(url)[0]

        # Validate URL
        if not self.config.is_valid_url(url):
            return None

        return url

    def is_same_domain(self, url: URL) -> bool:
        """
        Check if a URL belongs to the same domain as the starting URL.

        Args:
            url: The URL to check.

        Returns:
            True if the URL is from the same domain, False otherwise.
        """
        if not url:
            return False

        # Normalize the URL first
        url = self._normalize_url(url, self.config.url)
        if not url:
            return False

        # Parse the URL and check the domain
        parsed_url = urlparse(url)
        parsed_domain = urlparse(self.config.url)

        # Simple domain check - compare netloc
        is_same = parsed_url.netloc == parsed_domain.netloc

        # Debug logging
        if self.config.verbose:
            self.log(
                "Domain check: %s vs %s = %s",
                "DEBUG",
                (parsed_url.netloc, parsed_domain.netloc, is_same),
            )

        return is_same

    def get_same_domain_links(self, html: str, base_url: URL) -> Set[URL]:
        """
        Extract all unique links from HTML that belong to the same domain.

        Args:
            html: HTML content to parse.
            base_url: Base URL for resolving relative links.

        Returns:
            Set of unique, same-domain URLs.
        """
        if not html:
            # Fallback: synchronous fetch of the initial URL
            try:
                response = requests.get(
                    self.config.url, headers=CrawlerConfig.HEADERS, timeout=10
                )
                html = response.text
                base_url = response.url  # Use the final URL after redirects
            except Exception as e:
                self.log("Error fetching initial URL: %s", "ERROR", (str(e),))
                return set()

        if not base_url:
            base_url = self.config.url

        links = set()
        try:
            self.log(
                "Parsing HTML for links on %s (%d bytes)",
                "DEBUG",
                (base_url, len(html)),
            )
            soup = BeautifulSoup(html, "html.parser")

            # Log some debug information
            all_anchors = soup.find_all("a")
            self.log(
                "Found %d anchor tags on %s", "DEBUG", (len(all_anchors), base_url)
            )

            # Debug: Print the first few links found in HTML
            for i, anchor in enumerate(all_anchors[:5]):
                self.log("Sample anchor %d: %s", "DEBUG", (i, str(anchor)))

            # Find all <a> tags with href attribute
            href_anchors = soup.find_all("a", href=True)
            self.log(
                "Found %d anchors with href attribute", "DEBUG", (len(href_anchors),)
            )

            for link in href_anchors:
                href = link["href"].strip()
                self.log("Processing href: %s", "DEBUG", (href,))

                normalized_url = self._normalize_url(href, base_url)
                if not normalized_url:
                    self.log("Skipped invalid URL: %s", "DEBUG", (href,))
                    continue

                is_same_domain = self.is_same_domain(normalized_url)
                self.log(
                    "URL %s is %ssame domain",
                    "DEBUG",
                    (normalized_url, "" if is_same_domain else "not "),
                )

                if is_same_domain:
                    links.add(normalized_url)
                    self.log("Added link: %s", "DEBUG", (normalized_url,))
        except Exception as e:
            self.log("Error extracting links: %s", "ERROR", (str(e),))

        self.log("Found %d same-domain links", "INFO", (len(links),))
        return links

    async def fetch_page_async(
        self, session: aiohttp.ClientSession, url: URL
    ) -> Tuple[URL, Optional[str]]:
        """
        Fetch a page asynchronously.

        Args:
            session: The aiohttp session to use.
            url: The URL to fetch.

        Returns:
            Tuple of (URL, HTML content) or (URL, None) if fetch failed.
        """
        try:
            result = await self._fetch_with_retry(session, url, 0)
            if result[1] and self.config.verbose:  # If HTML content is not None
                # Debug log to show a small snippet of the content
                content_preview = (
                    result[1][:200] + "..." if len(result[1]) > 200 else result[1]
                )
                self.log("Content preview for %s: %s", "DEBUG", (url, content_preview))
            return result
        except Exception as e:
            self.log("Unexpected error in fetch_page_async: %s", "ERROR", (str(e),))
            return url, None

    async def _fetch_with_retry(
        self, session: aiohttp.ClientSession, url: URL, retry_count: int
    ) -> Tuple[URL, Optional[str]]:
        """
        Fetch a URL with retry logic.

        Args:
            session: The aiohttp session.
            url: The URL to fetch.
            retry_count: Current retry attempt.

        Returns:
            Tuple of (URL, HTML content) or (URL, None) if fetch failed.
        """
        try:
            # Random delay to be polite
            delay = random.uniform(self.config.delay_min, self.config.delay_max)
            await asyncio.sleep(delay)

            self.log("Fetching %s (retry: %d)", "FETCH", (url, retry_count))

            async with session.get(url, headers=CrawlerConfig.HEADERS) as response:
                if response.status == 200:
                    html = await response.text()
                    self.log("Successfully fetched %s", "SUCCESS", (url,))
                    return url, html

                self.log(
                    "Failed to fetch %s (status: %d)",
                    "WARNING",
                    (url, response.status),
                )
                return url, None

        except asyncio.TimeoutError:
            self.log("Timeout fetching %s", "WARNING", (url,))
            return url, None
        except Exception as e:
            self.log("Error fetching %s: %s", "ERROR", (url, str(e)))
            return url, None

    async def process_page(
        self,
        session: aiohttp.ClientSession,
        url: URL,
        crawl_state: Dict[str, Set[URL]],
    ) -> Set[URL]:
        """
        Process a single page: fetch it and extract links.

        Args:
            session: The aiohttp session to use.
            url: The URL to process.
            crawl_state: Dictionary containing the following keys:
                - to_visit (set): Set of URLs to visit
                - visited (set): Set of URLs already visited
                - in_progress (set): Set of URLs currently being processed

        Returns:
            Set of new links found.
        """
        try:
            # Fetch the page
            self.log("Starting to process page: %s", "DEBUG", (url,))
            url, html = await self.fetch_page_async(session, url)

            # If the fetch failed, return an empty set
            if not html:
                self.log("No HTML content for %s", "WARNING", (url,))
                crawl_state["in_progress"].remove(url)
                return set()

            self.log(
                "Successfully fetched HTML for %s (%d bytes)", "DEBUG", (url, len(html))
            )

            # Get all same-domain links
            links = self.get_same_domain_links(html, url)
            self.log("Found %d links on page %s", "DEBUG", (len(links), url))

            # Process the page callback
            self._process_page_callback(url, links)

            # Add new links to to_visit
            new_links = set()
            for link in links:
                if (
                    link not in crawl_state["visited"]
                    and link not in crawl_state["to_visit"]
                    and link not in crawl_state["in_progress"]
                ):
                    crawl_state["to_visit"].add(link)
                    new_links.add(link)
                    self.log("New link discovered: %s", "DEBUG", (link,))

                    # Call the link callback for newly discovered links
                    if self.config.link_callback:
                        try:
                            self.config.link_callback(link)
                        except Exception as e:
                            self.log(
                                "Error in link callback for %s: %s",
                                "ERROR",
                                (link, str(e)),
                            )

            # Mark this URL as visited
            crawl_state["in_progress"].remove(url)
            crawl_state["visited"].add(url)

            self.log("Processed %s, found %d new links", "INFO", (url, len(new_links)))
            return new_links

        except Exception as e:
            self.log("Error processing %s: %s", "ERROR", (url, str(e)))
            if url in crawl_state["in_progress"]:
                crawl_state["in_progress"].remove(url)
            return set()

    async def crawl_domain_async(self) -> Set[URL]:
        """
        Crawl all pages on the domain asynchronously.

        Returns:
            Set of all unique links found.
        """
        # Create a state dictionary to pass to process_page
        crawl_state = {
            "to_visit": {self.config.url},
            "visited": set(),
            "in_progress": set(),
        }

        self.log("Starting crawl from %s", "INFO", (self.config.url,))

        # Start monitoring task for long-running crawls
        monitor_task = None
        if self.config.verbose:
            monitor_task = asyncio.create_task(
                self._print_active_tasks_periodically(crawl_state["in_progress"])
            )

        # Use session context manager for connection pooling
        async with aiohttp.ClientSession() as session:
            while crawl_state["to_visit"] or crawl_state["in_progress"]:
                # Process URLs from to_visit in batches
                if (
                    crawl_state["to_visit"]
                    and len(crawl_state["in_progress"]) < self.config.max_concurrency
                ):
                    # Get the next URL to process
                    url = crawl_state["to_visit"].pop()
                    crawl_state["in_progress"].add(url)

                    # Process the page asynchronously
                    asyncio.create_task(self.process_page(session, url, crawl_state))
                else:
                    # Wait a bit before checking again
                    await asyncio.sleep(0.1)

            # Wait for all tasks to complete
            while crawl_state["in_progress"]:
                await asyncio.sleep(0.1)

            # Cancel the monitor task if it's running
            if self.config.verbose and monitor_task:
                monitor_task.cancel()
                try:
                    await monitor_task
                except asyncio.CancelledError:
                    pass

        return crawl_state["visited"]

    async def _print_active_tasks_periodically(self, in_progress: Set[URL]) -> None:
        """
        Periodically print active tasks for monitoring long-running crawls.

        Args:
            in_progress: Set of URLs currently being processed.
        """
        try:
            while True:
                await asyncio.sleep(5)  # Check every 5 seconds
                if not in_progress:
                    break

                self.log(
                    "Active tasks: %d - %s",
                    "INFO",
                    (len(in_progress), list(in_progress)[:5]),
                )
        except asyncio.CancelledError:
            pass  # Allow cancellation

    def crawl_domain(self) -> Set[URL]:
        """
        Run the async crawler using asyncio.

        Returns:
            Set of all unique links found.
        """
        self.log("Starting async crawl of %s", "INFO", (self.config.url,))
        start_time = time.time()

        # Run the async crawler
        try:
            loop = asyncio.get_event_loop()
            links = loop.run_until_complete(self.crawl_domain_async())
        except Exception as e:
            self.log("Error in async crawl: %s", "ERROR", (str(e),))
            links = set()

        # Log crawl stats
        elapsed = time.time() - start_time
        self.log(
            "Crawl completed in %.2f seconds, found %d links",
            "INFO",
            (elapsed, len(links)),
        )

        return links
