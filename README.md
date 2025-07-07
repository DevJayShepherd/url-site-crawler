# 🕸️ Site URL Crawler

> A fast, efficient web crawler built with Python

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Async Support](https://img.shields.io/badge/async-supported-green.svg)](https://docs.python.org/3/library/asyncio.html)

This crawler efficiently maps websites by identifying and traversing all links within a domain while ignoring external links and subdomains.

## ⭐ Key Features

- **🚄 Asynchronous Performance**: Uses `aiohttp` and `asyncio` for concurrent requests with configurable concurrency limits
- **💾 Efficient File Management**: Handles large-scale crawling through streaming writes and incremental saves
- **🔒 Same-Domain Focus**: Only processes links within the specified domain, ignoring external sites and subdomains
- **🧩 Multiple Output Formats**: Save results as TXT, CSV, or JSON with automatic file handling
- **👤 Interactive Mode**: User-friendly CLI interface for guided crawling operations
- **📝 Comprehensive Logging**: Detailed logs for troubleshooting and performance analysis

## ✨ Development Notes & Design Decisions

### 🛠️ Core Environment & Structure
- Installed expected core libraries (`aiohttp`, `beautifulsoup4`) for web crawling.
- Created an `application/` directory to organize main app logic and encourage modularity.
- Added `requirements.txt` for reproducible environments.
- Introduced a `Makefile` for quick execution of common developer tasks.

### 📊 Code Quality & Tooling
- Installed and configured `black` (auto-formatting) and `pylint` (linting) for code consistency.
- Included a `pylintrc` file to suppress common false positives and tailor linting to project needs.
- Used GitHub Copilot to help with docstrings and basic exception handling, always manually reviewed.

### 🔄 Crawler Architecture
- Developed a `WebCrawler` class as the main interface for crawling logic, starting with single-URL handling and expanding to full domain traversal.
- Switched from `requests` to `aiohttp` for non-blocking async requests, boosting speed and resource efficiency for large crawls.
- Added a file manager utility for saving crawl results locally in multiple formats (e.g., plain text, JSON), designed for scalability with large output sets.
- **When saving links to a file, links are written in chunks**—this approach allows the crawler to handle massive sites without excessive memory usage, ensuring Python's memory footprint remains stable even when crawling hundreds of thousands of links.

### 💻 CLI & User Experience
- Added a robust command-line interface using `argparse` for flexible configuration and easy terminal use.
- Implemented input validation to prevent crawling invalid or malformed URLs.
- Included user-agent headers in requests to mimic real-world browsers and minimize blocking by target domains.
- Considered and noted rate-limiting strategies to avoid overwhelming servers.

### 🧪 Testing & Reliability
- Began a basic `pytest` test suite to cover primary crawler functionality (unit tests for core features).
- Centralized logging and configured output directories for clean organization and easy troubleshooting.

### 📈 Scalability & Maintainability
- Designed file saving and log handling to work efficiently even with a large volume of discovered URLs.
- Adopted type hints throughout for improved readability and maintainability.
- Regularly updated the `Makefile` to streamline tasks (e.g., install dependencies, run linter, run tests).


## 🚀 Future Improvements (mix of tech debt and new features)

- Count the number of times each URL is seen across the website (to identify heavily linked content).
- Track HTTP response codes from pages as a health check to find bad links or pages.
- Track the time taken to crawl each page to help identify slow or heavy pages.
- Track the size of each page (in bytes/kilobytes) to help spot large or potentially problematic pages.
- Track the number of images on each page to help pinpoint content-heavy or slow-loading pages.
- Allow the async crawler to be started via an API, and expose crawling functionality via a template file for non-technical users.
- Add more tests to cover additional edge cases and increase overall test coverage.
- Continue refactoring according to `pylint` suggestions for style and best practices.
- Further refactor the code to improve readability and maintainability.
- Enhance CLI feedback for a better user experience.
- Improve logging for better monitoring and debugging.
- Improve exception and error handling to cover more edge cases.

## 🔧 Development Environment

This project was developed using the following tools and environment:

- **Operating System**: Ubuntu 24.04.2 LTS
- **IDE**: PyCharm
- **AI Assistance**:
  - GitHub Copilot for code suggestions, docstrings, and boilerplate code
  - Junie for architecture advice and debugging assistance

The combination of PyCharm's powerful Python tools and AI assistance helped streamline development, particularly for repetitive tasks like type hinting and documentation, while ensuring code quality and consistency throughout the project.

## 🏁 Getting Started

This guide will help you get up and running with the Zego Site Crawler quickly.

### 📥 Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/DevJayShepherd/zego-site-crawler.git
   ```

2. Set up the environment:
   ```bash
   make install
   ```

### 🔍 Running the Crawler

Run the crawler in interactive mode:
```bash
make run
```

The interactive mode will guide you through:
- Entering a URL to crawl
- Choosing whether to save results to a file
- Specifying the output file path
- Enabling/disabling verbose logging
- Setting the maximum number of concurrent requests

### 📄 Output Formats

The crawler supports multiple output formats based on the file extension:

- `.txt`: Plain text format
- `.csv`: CSV format with page URLs and their links
- `.json`: JSON format with structured data
