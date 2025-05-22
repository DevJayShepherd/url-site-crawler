from urllib.parse import urlparse, urljoin

import requests
from bs4 import BeautifulSoup


class WebCrawler:
    """
    A simple web crawler that fetches a webpage and extracts all unique links
    that stay within the same domain as the initial URL.
    """

    def __init__(self, url):
        self.url = url
        self.parsed_url = urlparse(url)
        self.base_domain = self.parsed_url.netloc

    def fetch_main_page(self):
        """
        Fetch the main webpage content of the URL provided at initialization.
        Returns:
            str: HTML content of the main page, or None if failed.
        """
        try:
            response = requests.get(self.url, timeout=10)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"Error fetching {self.url}: {e}")
            return None

    def get_same_domain_links(self):
        """
        Crawl the main page and return all unique, same-domain links found.
        Returns:
            set: Set of unique, same-domain URLs found on the page.
        """
        html = self.fetch_main_page()
        if not html:
            return set()
        soup = BeautifulSoup(html, "html.parser")
        found_urls = set()
        for a_tag in soup.find_all("a", href=True):
            href = a_tag["href"]
            joined_url = urljoin(self.url, href)
            parsed_url = urlparse(joined_url)
            if parsed_url.netloc == self.base_domain:
                cleaned_url = (
                    parsed_url.scheme + "://" + parsed_url.netloc + parsed_url.path
                )
                found_urls.add(cleaned_url)
        return found_urls
