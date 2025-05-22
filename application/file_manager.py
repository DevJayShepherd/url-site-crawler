"""
File management module for saving crawler results efficiently.
"""

import json
import csv
import os
import shutil
from tempfile import NamedTemporaryFile
from typing import List, Set, Optional, TextIO, Iterator

from application.logger import get_logger

# Type aliases for clarity
FilePath = str
URL = str


class FileManager:
    """
    Handles saving output links in various formats: text, JSON, or CSV.
    Designed for scalability with streaming writes and incremental saves.
    """

    # Default chunk size for batch processing (number of links per write)
    DEFAULT_CHUNK_SIZE = 500
    logger = get_logger("FileManager")

    @staticmethod
    def save(
        links: Iterator[URL],
        output_path: FilePath,
        output_type: Optional[str] = None,
        chunk_size: int = DEFAULT_CHUNK_SIZE,
    ) -> None:
        """
        Save links to a file in the specified output_type format.
        This method is primarily used for the initial file creation or non-incremental saves.

        Args:
            links: The links to save.
            output_path: The file path to save to.
            output_type: 'json', 'csv', or 'text'. If None, inferred from extension.
            chunk_size: Number of links to process in memory at once.
        """
        # Create directory if it doesn't exist
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)

        if output_type is None:
            if output_path.endswith(".json"):
                output_type = "json"
            elif output_path.endswith(".csv"):
                output_type = "csv"
            else:
                output_type = "text"

        FileManager.logger.info("Saving links to %s as %s", output_path, output_type)

        # Use streaming methods for scalability
        if output_type == "json":
            FileManager.save_json_stream(links, output_path, chunk_size)
        elif output_type == "csv":
            FileManager.save_csv_stream(links, output_path, chunk_size)
        else:
            FileManager.save_text_stream(links, output_path, chunk_size)

    @staticmethod
    def save_text_stream(
        links: Iterator[URL],
        output_path: FilePath,
        chunk_size: int = DEFAULT_CHUNK_SIZE,
    ) -> None:
        """
        Save links as plain text, one per line, using a streaming approach.

        Args:
            links: The links to save.
            output_path: The file path to save to.
            chunk_size: Number of links to process in memory at once.
        """
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                batch = []
                total_saved = 0

                for link in links:
                    batch.append(link)

                    if len(batch) >= chunk_size:
                        for url in batch:
                            f.write(f"{url}\n")
                        total_saved += len(batch)
                        FileManager.logger.debug(
                            "Saved %d links to %s", total_saved, output_path
                        )
                        batch = []

                # Write any remaining links
                if batch:
                    for url in batch:
                        f.write(f"{url}\n")
                    total_saved += len(batch)
                    FileManager.logger.debug(
                        "Saved %d links to %s", total_saved, output_path
                    )
        except IOError as e:
            FileManager.logger.error("Error writing to %s: %s", output_path, e)
            raise

    @staticmethod
    def save_json_stream(
        links: Iterator[URL],
        output_path: FilePath,
        chunk_size: int = DEFAULT_CHUNK_SIZE,
    ) -> None:
        """
        Save links as a JSON array using a streaming approach to handle large datasets.

        Args:
            links: The links to save.
            output_path: The file path to save to.
            chunk_size: Number of links to process in memory at once.
        """
        try:
            # Create a temporary file with context manager
            with NamedTemporaryFile(
                mode="w", delete=False, encoding="utf-8"
            ) as temp_file:
                temp_path = temp_file.name

                # Write JSON opening bracket
                temp_file.write("[\n")

                # Process in batches
                first_item = True
                batch = []
                total_saved = 0

                # Process links in batches
                for link in links:
                    batch.append(link)

                    # When batch is full, write to file
                    if len(batch) >= chunk_size:
                        FileManager._write_json_batch(temp_file, batch, first_item)
                        first_item = False
                        total_saved += len(batch)
                        FileManager.logger.debug("Processed %d links", total_saved)
                        batch = []

                # Write any remaining links
                if batch:
                    FileManager._write_json_batch(temp_file, batch, first_item)
                    total_saved += len(batch)

                # Close the JSON array
                temp_file.write("\n]")

            # Move the temporary file to the final destination
            shutil.move(temp_path, output_path)
            FileManager.logger.info("Saved %d links to %s", total_saved, output_path)

        except Exception as e:
            FileManager.logger.error("Error saving JSON: %s", e)
            # Clean up temp file if it exists
            if "temp_path" in locals():
                try:
                    os.unlink(temp_path)
                except Exception:
                    pass
            raise

    @staticmethod
    def _write_json_batch(file: TextIO, batch: List[URL], first_item: bool) -> None:
        """
        Helper method to write a batch of links to a JSON file.

        Args:
            file: The file to write to.
            batch: The batch of links to write.
            first_item: Whether this is the first item in the JSON array.
        """
        for i, url in enumerate(batch):
            if not first_item or i > 0:
                file.write(",\n")
            file.write(f'  "{url}"')

    @staticmethod
    def save_csv_stream(
        links: Iterator[URL],
        output_path: FilePath,
        chunk_size: int = DEFAULT_CHUNK_SIZE,
    ) -> None:
        """
        Save links as a CSV file with a single 'url' column using a streaming approach.

        Args:
            links: The links to save.
            output_path: The file path to save to.
            chunk_size: Number of links to process in memory at once.
        """
        try:
            with open(output_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["url"])

                batch = []
                total_saved = 0

                for link in links:
                    batch.append([link])

                    if len(batch) >= chunk_size:
                        writer.writerows(batch)
                        total_saved += len(batch)
                        FileManager.logger.debug(
                            "Saved %d links to %s", total_saved, output_path
                        )
                        batch = []

                # Write any remaining links
                if batch:
                    writer.writerows(batch)
                    total_saved += len(batch)
                    FileManager.logger.debug(
                        "Saved %d links to %s", total_saved, output_path
                    )
        except IOError as e:
            FileManager.logger.error("Error writing to %s: %s", output_path, e)
            raise

    @staticmethod
    def _append_text_link(link: URL, output_path: FilePath) -> bool:
        """
        Append a link to a text file.

        Args:
            link: The link to append.
            output_path: Path to the text file.

        Returns:
            bool: True if the link was appended, False if it already existed.
        """
        # Check if link already exists in the file
        with open(output_path, "r", encoding="utf-8") as f:
            existing_links = set(line.strip() for line in f)

        # Only append if link is not already in the file
        if link not in existing_links:
            with open(output_path, "a", encoding="utf-8") as f:
                f.write(f"{link}\n")
            return True
        return False

    @staticmethod
    def _append_csv_link(link: URL, output_path: FilePath) -> bool:
        """
        Append a link to a CSV file.

        Args:
            link: The link to append.
            output_path: Path to the CSV file.

        Returns:
            bool: True if the link was appended, False if it already existed.
        """
        # Read existing links
        existing_links = set()
        if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            with open(output_path, "r", newline="", encoding="utf-8") as f:
                reader = csv.reader(f)
                for row in reader:
                    if row:  # Skip empty rows
                        existing_links.add(row[0])

        # Only append if link is not already in the file
        if link not in existing_links:
            with open(output_path, "a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([link])
            return True
        return False

    @staticmethod
    def _append_json_link(link: URL, output_path: FilePath) -> bool:
        """
        Append a link to a JSON file.

        Args:
            link: The link to append.
            output_path: Path to the JSON file.

        Returns:
            bool: True if the link was appended, False if it already existed.
        """
        temp_path = None
        try:
            # Use a temporary file for safe updates
            with NamedTemporaryFile(
                mode="w", delete=False, encoding="utf-8"
            ) as temp_file:
                temp_path = temp_file.name

                # Read existing JSON
                with open(output_path, "r", encoding="utf-8") as f:
                    links = json.load(f)

                # Check if link already exists
                if link in links:
                    # Remove the temporary file
                    os.unlink(temp_path)
                    return False

                # Append the new link
                links.append(link)

                # Write the updated JSON to the temporary file
                json.dump(links, temp_file, indent=2)

            # Replace the original file with the updated one
            shutil.move(temp_path, output_path)
            return True

        except Exception as e:
            # Clean up and re-raise
            if temp_path and os.path.exists(temp_path):
                os.unlink(temp_path)
            raise e

    @staticmethod
    def append_link(link: URL, output_path: FilePath) -> None:
        """
        Append a single link to an existing file.
        Creates the file if it doesn't exist.

        Args:
            link: The link to append.
            output_path: The file path to append to.
        """
        try:
            # Create directory if it doesn't exist
            output_dir = os.path.dirname(output_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)

            # Determine file type
            if output_path.endswith(".json"):
                FileManager._append_json(link, output_path)
            elif output_path.endswith(".csv"):
                FileManager._append_csv(link, output_path)
            else:
                # Default to text file
                with open(output_path, "a", encoding="utf-8") as f:
                    f.write(link + "\n")
        except Exception as e:
            FileManager.logger.error("Error appending link: %s", e)

    @staticmethod
    def _append_json(link: URL, output_path: FilePath) -> None:
        """
        Append a link to a JSON file.

        Args:
            link: The link to append.
            output_path: Path to the JSON file.
        """
        try:
            # If file doesn't exist or is empty, create it with an empty array
            if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
                with open(output_path, "w", encoding="utf-8") as f:
                    json.dump([], f)

            # Read existing data
            with open(output_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Append the new link
            data.append(link)

            # Write back to file using temporary file for safety
            with NamedTemporaryFile(
                mode="w", delete=False, encoding="utf-8"
            ) as temp_file:
                temp_path = temp_file.name
                json.dump(data, temp_file, indent=2)

            # Move the temporary file to the final destination
            shutil.move(temp_path, output_path)

        except Exception as e:
            FileManager.logger.error("Error appending to JSON: %s", e)
            # Clean up temp file if it exists
            if "temp_path" in locals():
                try:
                    os.unlink(temp_path)
                except:
                    pass

    @staticmethod
    def _append_csv(link: URL, output_path: FilePath) -> None:
        """
        Append a link to a CSV file.

        Args:
            link: The link to append.
            output_path: Path to the CSV file.
        """
        try:
            # Check if file exists to determine if header is needed
            file_exists = (
                os.path.exists(output_path) and os.path.getsize(output_path) > 0
            )

            with open(output_path, "a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)

                # Write header if file is new
                if not file_exists:
                    writer.writerow(["url"])

                # Write the link
                writer.writerow([link])

        except Exception as e:
            FileManager.logger.error("Error appending to CSV: %s", e)

    @staticmethod
    def save_page_links(page_url: URL, links: Set[URL], output_path: FilePath) -> None:
        """
        Save a page URL and its links in the specified format.
        This matches the project requirement to show each page URL followed by its links.

        Args:
            page_url: The URL of the page.
            links: The links found on the page.
            output_path: The file path to save to.
        """
        try:
            # Create directory if it doesn't exist
            output_dir = os.path.dirname(output_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)

            # Determine file type
            if output_path.endswith(".json"):
                FileManager._append_page_json(page_url, links, output_path)
            elif output_path.endswith(".csv"):
                FileManager._append_page_csv(page_url, links, output_path)
            else:
                # Default to text file
                with open(output_path, "a", encoding="utf-8") as f:
                    f.write(f"\nPage: {page_url}\n")
                    f.write("Links found:\n")
                    for link in links:
                        f.write(f"  - {link}\n")
                    f.write("-" * 40 + "\n")
        except Exception as e:
            FileManager.logger.error("Error saving page links: %s", e)

    @staticmethod
    def _append_page_json(
        page_url: URL, links: Set[URL], output_path: FilePath
    ) -> None:
        """
        Append a page and its links to a JSON file.
        Creates the file with proper structure if it doesn't exist.

        Args:
            page_url: The URL of the page.
            links: The links found on the page.
            output_path: The file path to append to.
        """
        # Create empty file with proper structure if it doesn't exist
        if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump({"pages": []}, f)

        try:
            # Read the existing data
            with open(output_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Add the new page and its links
            data["pages"].append({"page_url": page_url, "links": list(links)})

            # Write back the updated data
            with NamedTemporaryFile(
                mode="w", delete=False, encoding="utf-8"
            ) as temp_file:
                temp_path = temp_file.name
                json.dump(data, temp_file, indent=2)

            # Move the temporary file to the final destination
            shutil.move(temp_path, output_path)

        except Exception as e:
            FileManager.logger.error("Error appending page to JSON: %s", e)
            # Clean up temp file if it exists
            if "temp_path" in locals():
                try:
                    os.unlink(temp_path)
                except:
                    pass

    @staticmethod
    def _append_page_csv(page_url: URL, links: Set[URL], output_path: FilePath) -> None:
        """
        Append a page and its links to a CSV file.
        Creates the file with header if it doesn't exist.

        Args:
            page_url: The URL of the page.
            links: The links found on the page.
            output_path: The file path to append to.
        """
        file_exists = os.path.exists(output_path)

        try:
            with open(output_path, "a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)

                # Write header if file is new
                if not file_exists:
                    writer.writerow(["source_page", "found_link"])

                # Write each link with the source page
                for link in links:
                    writer.writerow([page_url, link])

        except Exception as e:
            FileManager.logger.error("Error appending page to CSV: %s", e)
