python-developer-test
Zego
About Us

At Zego, we understand that traditional motor insurance holds good drivers back. It's too complicated, too expensive, and it doesn't reflect how well you actually drive. Since 2016, we have been on a mission to change that by offering the lowest priced insurance for good drivers.

From van drivers and gig economy workers to everyday car drivers, our customers are the driving force behind everything we do. We've sold tens of millions of policies and raised over $200 million in funding. And we’re only just getting started.
Our Values

Zego is thoroughly committed to our values, which are the essence of our culture. Our values defined everything we do and how we do it. They are the foundation of our company and the guiding principles for our employees. Our values are:
Blaze a trail	Blaze a trail	Emphasize curiosity and creativity to disrupt the industry through experimentation and evolution.
Drive to win	Drive to win	Strive for excellence by working smart, maintaining well-being, and fostering a safe, productive environment.
Take the wheel	Take the wheel	Encourage ownership and trust, empowering individuals to fulfil commitments and prioritize customers.
Zego before ego	Zego before ego	Promote unity by working as one team, celebrating diversity, and appreciating each individual's uniqueness.
The Engineering Team

Zego puts technology first in its mission to define the future of the insurance industry. By focusing on our customers' needs we're building the flexible and sustainable insurance products and services that they deserve. And we do that by empowering a diverse, resourceful, and creative team of engineers that thrive on challenge and innovation.
How We Work

    Collaboration & Knowledge Sharing - Engineers at Zego work closely with cross-functional teams to gather requirements, deliver well-structured solutions, and contribute to code reviews to ensure high-quality output.
    Problem Solving & Innovation - We encourage analytical thinking and a proactive approach to tackling complex problems. Engineers are expected to contribute to discussions around optimization, scalability, and performance.
    Continuous Learning & Growth - At Zego, we provide engineers with abundant opportunities to learn, experiment and advance. We positively encourage the use of AI in our solutions as well as harnessing AI-powered tools to automate workflows, boost productivity and accelerate innovation. You'll have our full support to refine your skills, stay ahead of best practices and explore the latest technologies that drive our products and services forward.
    Ownership & Accountability - Our team members take ownership of their work, ensuring that solutions are reliable, scalable, and aligned with business needs. We trust our engineers to take initiative and drive meaningful progress.

Who should be taking this test?

This test has been created for all levels of developer, Junior through to Staff Engineer and everyone in between. Ideally you have hands-on experience developing Python solutions using Object Oriented Programming methodologies in a commercial setting. You have good problem-solving abilities, a passion for writing clean and generally produce efficient, maintainable scaleable code.
The test 

Create a Python app that can be run from the command line that will accept a base URL to crawl the site. For each page it finds, the script will print the URL of the page and all the URLs it finds on that page. The crawler will only process that single domain and not crawl URLs pointing to other domains or subdomains. Please employ patterns that will allow your crawler to run as quickly as possible, making full use any patterns that might boost the speed of the task, whilst not sacrificing accuracy and compute resources. Do not use tools like Scrapy or Playwright. You may use libraries for other purposes such as making HTTP requests, parsing HTML and other similar tasks.
The objective

This exercise is intended to allow you to demonstrate how you design software and write good quality code. We will look at how you have structured your code and how you test it. We want to understand how you have gone about solving this problem, what tools you used to become familiar with the subject matter and what tools you used to produce the code and verify your work. Please include detailed information about your IDE, the use of any interactive AI (such as Copilot) as well as any other AI tools that form part of your workflow.

You might also consider how you would extend your code to handle more complex scenarios, such a crawling multiple domains at once, thinking about how a command line interface might not be best suited for this purpose and what alternatives might be more suitable. Also, feel free to set the repo up as you would a production project.

Extend this README to include a detailed discussion about your design decisions, the options you considered and the trade-offs you made during the development process, and aspects you might have addressed or refined if not constrained by time.
Instructions

    Create a repo.
    Tackle the test.
    Push the code back.
    Add us (@2014klee, @danyal-zego, @bogdangoie and @cypherlou) as collaborators and tag us to review.
    Notify your TA so they can chase the reviewers.


---- 

## Development Notes & Design Decisions

### Core Environment & Structure
- Installed expected core libraries (`aiohttp`, `beautifulsoup4`) for web crawling.
- Created an `application/` directory to organize main app logic and encourage modularity.
- Added `requirements.txt` for reproducible environments.
- Introduced a `Makefile` for quick execution of common developer tasks.

### Code Quality & Tooling
- Installed and configured `black` (auto-formatting) and `pylint` (linting) for code consistency.
- Included a `pylintrc` file to suppress common false positives and tailor linting to project needs.
- Used GitHub Copilot to help with docstrings and basic exception handling, always manually reviewed.

### Crawler Architecture
- Developed a `WebCrawler` class as the main interface for crawling logic, starting with single-URL handling and expanding to full domain traversal.
- Switched from `requests` to `aiohttp` for non-blocking async requests, boosting speed and resource efficiency for large crawls.
- Added a file manager utility for saving crawl results locally in multiple formats (e.g., plain text, JSON), designed for scalability with large output sets.
- **When saving links to a file, links are written in chunks**—this approach allows the crawler to handle massive sites without excessive memory usage, ensuring Python's memory footprint remains stable even when crawling hundreds of thousands of links.

### CLI & User Experience
- Added a robust command-line interface using `argparse` for flexible configuration and easy terminal use.
- Implemented input validation to prevent crawling invalid or malformed URLs.
- Included user-agent headers in requests to mimic real-world browsers and minimize blocking by target domains.
- Considered and noted rate-limiting strategies to avoid overwhelming servers.

### Testing & Reliability
- Began a basic `pytest` test suite to cover primary crawler functionality (unit tests for core features).
- Centralized logging and configured output directories for clean organization and easy troubleshooting.

### Scalability & Maintainability
- Designed file saving and log handling to work efficiently even with a large volume of discovered URLs.
- Adopted type hints throughout for improved readability and maintainability.
- Regularly updated the `Makefile` to streamline tasks (e.g., install dependencies, run linter, run tests).


## Future Improvements (mix of tech debt and new features)

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

## Getting Started

This guide will help you get up and running with the Zego Site Crawler quickly.

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/zego-site-crawler.git
   cd zego-site-crawler
   ```

2. Set up the environment:
   ```bash
   make install
   ```

### Running the Crawler

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

### Output Formats

The crawler supports multiple output formats based on the file extension:

- `.txt`: Plain text format
- `.csv`: CSV format with page URLs and their links
- `.json`: JSON format with structured data