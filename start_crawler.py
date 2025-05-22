#!/usr/bin/env python3
"""
Zego Site Crawler - Main Entry Point

This script provides a user-friendly way to start the crawler by prompting for inputs
rather than requiring command-line arguments.
"""

import os
import sys
import time
from datetime import datetime
from urllib.parse import urlparse
import argparse

from application.async_crawler import AsyncWebCrawler
from application.file_manager import FileManager
from application.logger import setup_logging, get_logger


def get_valid_url():
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


def get_yes_no_input(prompt):
    """Get a yes/no response from the user."""
    while True:
        response = input(f"{prompt} (y/n): ").strip().lower()
        if response in ["y", "yes"]:
            return True
        if response in ["n", "no"]:
            return False
        print("Please enter 'y' or 'n'.")


def get_output_file():
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


def get_concurrency():
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


def prompt_for_url():
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


def prompt_for_output_path():
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


def run_crawler(url, output=None, verbose=False, use_async=True, concurrency=10):
    """
    Run the crawler with the specified options.

    Args:
        url (str): URL to crawl
        output (str, optional): Output file path
        verbose (bool, optional): Enable verbose logging
        use_async (bool, optional): Use async crawler
        concurrency (int, optional): Max concurrent requests
    """
    # Set up logging
    setup_logging(verbose=verbose)
    logger = get_logger("Interactive")

    try:
        print("\n" + "=" * 50)
        print(f"Starting crawler for: {url}")
        print(f"Verbose mode: {'Enabled' if verbose else 'Disabled'}")
        print(f"Output: {output}")
        print(f"Concurrency: {concurrency}")
        print("=" * 50 + "\n")

        start_time = time.time()
        logger.info("Starting crawler for %s", url)
        logger.info("Using asynchronous crawler with concurrency=%d", concurrency)

        # Create the crawler with default configuration
        crawler = AsyncWebCrawler(url, verbose=verbose, max_concurrency=concurrency)

        if output:
            # Setup link callback for incremental saving
            logger.info("Incremental saving enabled, writing to %s", output)

            def save_link_callback(link):
                try:
                    FileManager.append_link(link, output)
                    if verbose:
                        logger.debug("Incrementally saved: %s", link)
                except Exception as e:
                    logger.warning("Failed to save link incrementally: %s", e)

            crawler.set_link_callback(save_link_callback)

        # Start the crawl
        links = crawler.crawl_domain()

        # If no output was specified, print links to stdout
        if not output:
            print("\nDiscovered links:")
            for link in links:
                print(link)

        # Print summary
        elapsed_time = time.time() - start_time
        print("\n" + "=" * 50)
        print(f"Crawl completed in {elapsed_time:.2f} seconds")
        print(f"Found {len(links)} unique links")
        if output:
            print(f"Results saved to: {output}")
        print("=" * 50 + "\n")

        logger.info("Crawl completed in %.2f seconds", elapsed_time)
        logger.info("Found %d unique links", len(links))

    except KeyboardInterrupt:
        print("\nCrawl interrupted by user")
        logger.warning("Crawl interrupted by user")
        return 1
    except Exception as e:
        print(f"\nError during crawl: {e}")
        logger.error("Error during crawl: %s", e)
        return 1

    return 0


def run_interactive_mode():
    """Run the crawler in interactive mode, prompting for all options."""
    print("=== Zego Site Crawler - Interactive Mode ===")

    # Get required inputs
    url = prompt_for_url()

    # Get output options
    save_results = get_yes_no_input("Save results to a file?")
    if save_results:
        output = prompt_for_output_path()
    else:
        output = None

    # Ask for concurrency
    concurrency = int(
        input("Enter max concurrent requests (recommended: 10): ") or "10"
    )

    # Ask for verbosity
    verbose = get_yes_no_input("Enable verbose logging?")

    # Run the crawler with only the essential options
    run_crawler(url, output, verbose, True, concurrency)


def main():
    """Main entry point for the crawler."""
    parser = argparse.ArgumentParser(description="Web Crawler CLI")
    parser.add_argument("-u", "--url", help="URL to crawl")
    parser.add_argument("-o", "--output", help="Output file path")
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable verbose logging"
    )
    parser.add_argument(
        "-a", "--async", action="store_true", dest="use_async", help="Use async crawler"
    )
    parser.add_argument(
        "-c", "--concurrency", type=int, default=10, help="Max concurrent requests"
    )
    parser.add_argument(
        "--interactive", action="store_true", help="Run in interactive mode"
    )

    args = parser.parse_args()

    # Interactive mode
    if args.interactive or (not args.url):
        run_interactive_mode()
        return

    # Extract arguments
    url = args.url
    output = args.output
    verbose = args.verbose
    use_async = args.use_async
    concurrency = args.concurrency

    # Ensure output directory exists if output is specified
    if output:
        output_dir = os.path.dirname(output)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)

    run_crawler(url, output, verbose, use_async, concurrency)


if __name__ == "__main__":
    sys.exit(main())
