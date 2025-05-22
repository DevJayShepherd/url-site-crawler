#!/usr/bin/env python3
"""
Zego Site Crawler - Main Entry Point

This script provides a user-friendly way to start the crawler by prompting for inputs
rather than requiring command-line arguments.
"""

import os
import sys
import time
import argparse
import re
import requests
from typing import Tuple, Optional, List, Dict, Any, Union, Callable
from urllib.parse import urlparse
from datetime import datetime
from application.logger import get_logger, setup_logging
from application.async_crawler import AsyncWebCrawler, CrawlerConfig
from application.file_manager import FileManager

# Initialize logger
logger = get_logger("start_crawler")


def is_valid_url_format(url: str) -> bool:
    """
    Check if the URL has a valid format.

    Args:
        url: The URL to validate

    Returns:
        True if the URL has a valid format, False otherwise
    """
    # Simple regex pattern for URL validation
    pattern = re.compile(
        r"^(?:http|https)://"  # http:// or https://
        r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|"  # domain
        r"localhost|"  # localhost
        r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # or IPv4
        r"(?::\d+)?"  # optional port
        r"(?:/?|[/?]\S+)$",
        re.IGNORECASE,
    )

    return bool(pattern.match(url))


def check_url_accessibility(
    url: str, timeout: int = 5
) -> Tuple[bool, Optional[int], Optional[str]]:
    """
    Check if the URL is accessible by making a HEAD request.

    Args:
        url: The URL to check
        timeout: Timeout in seconds

    Returns:
        Tuple containing (is_accessible, status_code, error_message)
    """
    try:
        # Use the same headers as the main crawler
        headers = CrawlerConfig.HEADERS

        response = requests.head(
            url, timeout=timeout, allow_redirects=True, headers=headers
        )
        return (response.status_code == 200, response.status_code, None)
    except requests.exceptions.ConnectTimeout:
        return (False, None, "Connection timed out")
    except requests.exceptions.ConnectionError:
        return (False, None, "Connection error")
    except requests.exceptions.RequestException as e:
        return (False, None, str(e))


def validate_url(url: str) -> Tuple[bool, Optional[str]]:
    """
    Validate URL format and accessibility.

    Args:
        url: The URL to validate

    Returns:
        Tuple containing (is_valid, error_message)
    """
    # Check URL format
    if not is_valid_url_format(url):
        return (
            False,
            f"Invalid URL format: {url}\nURL must start with http:// or https:// and contain a valid domain.",
        )

    # Check if URL is accessible
    is_accessible, status_code, error_message = check_url_accessibility(url)
    if not is_accessible:
        if status_code:
            return (False, f"URL returned status code {status_code}: {url}")
        else:
            return (False, f"URL is not accessible: {url}\nError: {error_message}")

    return (True, None)


def get_valid_url() -> str:
    """Prompt the user for a valid URL and normalize it."""
    while True:
        url = input("Enter the website URL to crawl: ").strip()

        # Add protocol if missing
        if not url.startswith(("http://", "https://")):
            url = f"https://{url}"
            print(f"Protocol added: {url}")

        # Validate URL format
        try:
            parsed = urlparse(url)
            if not all([parsed.scheme, parsed.netloc]):
                print("Invalid URL format. Please enter a valid website URL.")
                continue
            return url
        except Exception:
            print("Invalid URL format. Please enter a valid website URL.")


def get_yes_no_input(prompt: str) -> bool:
    """
    Get a yes/no input from the user.

    Args:
        prompt: The prompt to show the user

    Returns:
        True if yes, False if no

    Note:
        Will exit the program if user types 'exit'
    """
    while True:
        response = input(f"{prompt} ").strip().lower()

        if response == "exit":
            print("\nExiting Zego Site Crawler. Goodbye!")
            sys.exit(0)

        if response in ["y", "yes"]:
            return True
        elif response in ["n", "no"]:
            return False
        else:
            print("Please enter 'y' or 'n' (or 'exit' to quit)")


def get_output_file() -> Optional[str]:
    """Prompt the user for an output file."""
    # Define supported file extensions
    supported_extensions = (".txt", ".text", ".csv", ".json")
    # Ensure output directory exists
    output_dir = os.path.join(os.getcwd(), "output")
    os.makedirs(output_dir, exist_ok=True)

    # Generate a default filename based on current time
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    default_filename = f"links_{timestamp}.txt"
    default_path = os.path.join(output_dir, default_filename)

    while True:
        output = input(
            f"Enter output file path (.txt, .text, .csv, or .json) or press Enter for default [{default_path}]: "
        ).strip()

        # Use default if empty
        if not output:
            print(f"Using default output file: {default_path}")
            return default_path

        # If the path doesn't have a directory component, place it in the output directory
        if not os.path.dirname(output):
            output = os.path.join(output_dir, output)
            print(f"File will be saved to: {output}")

        # Get the directory part of the path
        directory = os.path.dirname(output)
        if directory and not os.path.exists(directory):
            try_create = get_yes_no_input(
                f"Directory '{directory}' doesn't exist. Create it?"
            )
            if try_create:
                try:
                    os.makedirs(directory, exist_ok=True)
                except Exception as e:
                    print(f"Error creating directory: {e}")
                    continue
            else:
                continue

        # Check file extension - strictly enforce supported types
        is_supported = False
        for ext in supported_extensions:
            if output.lower().endswith(ext):
                is_supported = True
                break

        if not is_supported:
            print(
                f"Error: Unsupported file format. Please use one of: {', '.join(supported_extensions)}"
            )
            continue

        return output


def get_concurrency() -> int:
    """Prompt the user for concurrency level."""
    while True:
        try:
            concurrency = input(
                "Enter maximum concurrent requests (3-10, default is 3): "
            ).strip()
            if not concurrency:
                return 3

            concurrency = int(concurrency)
            if 1 <= concurrency <= 20:
                return concurrency
            else:
                print("Please enter a number between 1 and 20.")
        except ValueError:
            print("Please enter a valid number.")


def prompt_for_url() -> str:
    """Prompt the user for a valid URL and normalize it."""
    while True:
        url = input("Enter the website URL to crawl: ").strip()

        # Add protocol if missing
        if not url.startswith(("http://", "https://")):
            url = f"https://{url}"
            print(f"Protocol added: {url}")

        # Validate URL format
        try:
            parsed = urlparse(url)
            if not all([parsed.scheme, parsed.netloc]):
                print("Invalid URL format. Please enter a valid website URL.")
                continue
            return url
        except Exception:
            print("Invalid URL format. Please enter a valid website URL.")


def prompt_for_output_path() -> str:
    """Prompt the user for an output file."""
    # Define supported file extensions
    supported_extensions = (".txt", ".text", ".csv", ".json")
    # Ensure output directory exists
    output_dir = os.path.join(os.getcwd(), "output")
    os.makedirs(output_dir, exist_ok=True)

    # Generate a default filename based on current time
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    default_filename = f"links_{timestamp}.txt"
    default_path = os.path.join(output_dir, default_filename)

    while True:
        output = input(
            f"Enter output file path (.txt, .text, .csv, or .json) or press Enter for default [{default_path}]: "
        ).strip()

        # Use default if empty
        if not output:
            print(f"Using default output file: {default_path}")
            return default_path

        # If the path doesn't have a directory component, place it in the output directory
        if not os.path.dirname(output):
            output = os.path.join(output_dir, output)
            print(f"File will be saved to: {output}")

        # Get the directory part of the path
        directory = os.path.dirname(output)
        if directory and not os.path.exists(directory):
            try_create = get_yes_no_input(
                f"Directory '{directory}' doesn't exist. Create it?"
            )
            if try_create:
                try:
                    os.makedirs(directory, exist_ok=True)
                except Exception as e:
                    print(f"Error creating directory: {e}")
                    continue
            else:
                continue

        # Check file extension - strictly enforce supported types
        is_supported = False
        for ext in supported_extensions:
            if output.lower().endswith(ext):
                is_supported = True
                break

        if not is_supported:
            print(
                f"Error: Unsupported file format. Please use one of: {', '.join(supported_extensions)}"
            )
            continue

        return output


def run_crawler(
    url: str,
    output: Optional[str] = None,
    verbose: bool = False,
    use_async: bool = True,
    concurrency: int = 10,
) -> int:
    """
    Run the crawler with the specified options.

    Args:
        url: URL to crawl
        output: Path to output file (optional)
        verbose: Enable verbose output
        use_async: Use asynchronous crawler
        concurrency: Maximum concurrent requests

    Returns:
        Exit code (0 for success)
    """
    try:
        # Ensure output directory exists if provided
        if output:
            # Make sure output is in the output directory if not specified with a path
            if not os.path.dirname(output):
                output = os.path.join("output", output)

            # Create output directory if it doesn't exist
            output_dir = os.path.dirname(output)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
                logger.info(f"Created directory: {output_dir}")

        logger.info("=" * 50)
        logger.info(f"Starting crawler for: {url}")
        logger.info(f"Verbose mode: {'Enabled' if verbose else 'Disabled'}")
        logger.info(f"Output: {output}")
        logger.info(
            f"Using {'async' if use_async else 'sync'} mode with concurrency {concurrency}"
        )
        logger.info("=" * 50)

        start_time = time.time()

        # Initialize crawler
        if use_async:
            crawler = AsyncWebCrawler(url, max_concurrency=concurrency, verbose=verbose)
        else:
            # Fallback to sync mode by setting concurrency to 1
            crawler = AsyncWebCrawler(url, max_concurrency=1, verbose=verbose)

        # Track links found on each page
        page_links = {}

        # Callback for when a page is processed
        def page_processed_callback(page_url: str, links: List[str]) -> None:
            page_links[page_url] = links

            # Always print page information (required by project specs)
            print(f"\nPage: {page_url}")
            print("Links found:")
            for link in links:
                print(f"  - {link}")
            print("-" * 40)

            # Save to file if output is specified
            if output:
                FileManager.save_page_links(page_url, set(links), output)

        # Set callbacks
        crawler.set_page_callback(page_processed_callback)

        # Start the crawl
        links = crawler.crawl_domain()

        # Print summary
        elapsed_time = time.time() - start_time

        print("\n" + "=" * 50)
        print(f"Crawl completed in {elapsed_time:.2f} seconds")
        print(f"Found {len(links)} unique links across {len(page_links)} pages")
        if output:
            print(f"Results saved to: {output}")
        print("=" * 50 + "\n")

        # Log summary to logger as well
        logger.info("Crawl completed in %.2f seconds", elapsed_time)
        logger.info(
            "Found %d unique links across %d pages", len(links), len(page_links)
        )
        if output:
            logger.info("Results saved to: %s", output)

        return 0
    except KeyboardInterrupt:
        print("\nCrawl interrupted by user")
        logger.warning("Crawl interrupted by user")
        return 1
    except Exception as e:
        print(f"\nError during crawl: {e}")
        logger.error("Error during crawl: %s", e)
        return 1


def interactive_mode() -> int:
    """
    Run the crawler in interactive mode, allowing users to try multiple URLs.

    Returns:
        Exit code (0 for success)
    """
    print("\nZego Site Crawler - Interactive Mode")
    print("===================================")
    print("Type 'exit' at any time to quit the application.\n")

    while True:
        # Get URL from user
        url = input("\nEnter URL to crawl (or 'exit' to quit): ")

        if url.lower() == "exit":
            print("\nExiting Zego Site Crawler. Goodbye!")
            return 0

        # Validate URL format and accessibility
        is_valid, error_message = validate_url(url)
        if not is_valid:
            print(error_message)
            print("\nPlease try again with a valid URL or type 'exit' to quit.")
            continue

        # Get output options
        save_results = get_yes_no_input("Save results to a file? (y/n): ")
        if save_results:
            output_path = input("Enter output file path: ").strip()
            if not output_path:
                output_path = f"output/{urlparse(url).netloc}.txt"
                print(f"Using default output path: {output_path}")

            # Ensure output path is in the output directory if no directory specified
            if not os.path.dirname(output_path):
                output_path = os.path.join("output", output_path)
                print(f"Using path: {output_path}")
        else:
            output_path = None

        # Get verbosity option
        verbose = get_yes_no_input("Enable verbose logging? (y/n): ")

        # Get concurrency options
        use_async = True  # Default to async crawler
        concurrency = input("Enter max concurrent requests (default: 10): ").strip()
        concurrency = int(concurrency) if concurrency.isdigit() else 10

        # Run the crawler
        result = run_crawler(
            url=url,
            output=output_path,
            verbose=verbose,
            use_async=use_async,
            concurrency=concurrency,
        )

        # Ask if user wants to crawl another site
        another = get_yes_no_input("\nCrawl another site? (y/n): ")
        if not another:
            print("\nExiting Zego Site Crawler. Goodbye!")
            return result


def main() -> int:
    """
    Main entry point for the crawler.

    Returns:
        Exit code (0 for success)
    """
    parser = argparse.ArgumentParser(description="Crawl a website and extract links.")
    parser.add_argument("url", nargs="?", help="URL to crawl")
    parser.add_argument("-o", "--output", help="Output file path")
    parser.add_argument(
        "-i", "--interactive", action="store_true", help="Run in interactive mode"
    )
    parser.add_argument(
        "-a",
        "--async",
        dest="use_async",
        action="store_true",
        help="Use asynchronous crawler",
    )
    parser.add_argument(
        "-c",
        "--concurrency",
        type=int,
        default=10,
        help="Maximum concurrent requests (default: 10)",
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable verbose logging"
    )

    args = parser.parse_args()

    # Configure logging
    setup_logging(verbose=args.verbose)

    # Interactive mode if requested or no URL provided
    if args.interactive or not args.url:
        return interactive_mode()

    # Validate URL
    is_valid, error_message = validate_url(args.url)
    if not is_valid:
        print(error_message)
        return 1

    # Set default output path if none provided
    if args.output:
        output_path = args.output
    else:
        output_path = f"output/{urlparse(args.url).netloc}.txt"
        print(f"Using default output path: {output_path}")

    # Ensure output directory exists
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created directory: {output_dir}")

    # Run the crawler
    return run_crawler(
        url=args.url,
        output=output_path,
        verbose=args.verbose,
        use_async=args.use_async,
        concurrency=args.concurrency,
    )


if __name__ == "__main__":
    sys.exit(main())
