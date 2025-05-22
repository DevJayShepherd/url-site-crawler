"""Unit tests for the link extraction functionality."""

import pytest
from unittest.mock import patch, MagicMock
from bs4 import BeautifulSoup

from application.async_crawler import AsyncWebCrawler


class TestLinkExtraction:
    """Test cases for the link extraction functionality."""

    @pytest.fixture
    def crawler(self):
        """Create a crawler instance for testing."""
        return AsyncWebCrawler("https://example.com", verbose=False)

    def test_get_same_domain_links(self, crawler):
        """Test the extraction of same-domain links from HTML content."""
        # Create a simple HTML document with various link types
        html = """
        <html>
            <body>
                <a href="https://example.com/page1">Link 1</a>
                <a href="https://example.com/page2">Link 2</a>
                <a href="https://other-domain.com/page">External Link</a>
                <a href="/relative-path">Relative Link</a>
                <a href="mailto:user@example.com">Email Link</a>
                <a href="javascript:void(0)">JavaScript Link</a>
                <a href="#section">Fragment Link</a>
                <a href="">Empty Link</a>
            </body>
        </html>
        """

        # Mock the is_same_domain method to control its behavior
        with patch.object(crawler, "is_same_domain") as mock_is_same_domain:
            # Set up the mock to return True for same domain links and False for others
            def side_effect(url):
                return "example.com" in url and not url.startswith(
                    ("mailto:", "javascript:", "#")
                )

            mock_is_same_domain.side_effect = side_effect

            # Call the method being tested
            links = crawler.get_same_domain_links(html, "https://example.com")

            # Verify the results
            assert "https://example.com/page1" in links
            assert "https://example.com/page2" in links
            assert (
                "https://example.com/relative-path" in links
            )  # Normalized relative path
            assert "https://other-domain.com/page" not in links
            assert "mailto:user@example.com" not in links
            assert "javascript:void(0)" not in links
            assert "#section" not in links
            assert "" not in links

    def test_normalize_url(self, crawler):
        """Test URL normalization with different types of URLs."""
        base_url = "https://example.com/dir/"

        # Test case: absolute URL
        assert (
            crawler._normalize_url("https://example.com/page")
            == "https://example.com/page"
        )

        # Test case: relative URL with base
        assert (
            crawler._normalize_url("page.html", base_url)
            == "https://example.com/dir/page.html"
        )
        assert (
            crawler._normalize_url("/page.html", base_url)
            == "https://example.com/page.html"
        )

        # Test case: URL with fragments
        assert (
            crawler._normalize_url("https://example.com/page#section", base_url)
            == "https://example.com/page"
        )
        assert (
            crawler._normalize_url("page#section", base_url)
            == "https://example.com/dir/page"
        )

        # Test case: URL with query parameters
        assert (
            crawler._normalize_url("https://example.com/page?param=value", base_url)
            == "https://example.com/page?param=value"
        )

        # Test case: invalid URLs
        assert crawler._normalize_url("javascript:alert('test')", base_url) is None
        assert crawler._normalize_url("mailto:user@example.com", base_url) is None
        assert crawler._normalize_url("tel:1234567890", base_url) is None
