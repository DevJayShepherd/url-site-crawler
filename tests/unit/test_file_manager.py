"""Unit tests for the FileManager class."""

import os
import pytest
import tempfile
import json
import csv
from unittest.mock import patch, mock_open

from application.file_manager import FileManager


class TestFileManager:
    """Test cases for the FileManager class."""

    def test_file_extension_handling(self):
        """Test how the class handles file extensions."""
        # Instead of testing a non-existent method, test the behavior through append_link
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as temp_file:
            txt_path = temp_file.name
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as temp_file:
            csv_path = temp_file.name
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as temp_file:
            # Initialize with an empty JSON array
            temp_file.write(b"[]")
            temp_file.flush()
            json_path = temp_file.name
        with tempfile.NamedTemporaryFile(suffix=".unknown", delete=False) as temp_file:
            unknown_path = temp_file.name

        try:
            # Test that each file type is handled correctly
            FileManager.append_link("https://example.com", txt_path)
            FileManager.append_link("https://example.com", csv_path)
            FileManager.append_link("https://example.com", json_path)
            FileManager.append_link(
                "https://example.com", unknown_path
            )  # Should default to text

            # Verify text files
            with open(txt_path, "r") as f:
                assert "https://example.com" in f.read()
            with open(unknown_path, "r") as f:
                assert "https://example.com" in f.read()

        finally:
            # Clean up
            for path in [txt_path, csv_path, json_path, unknown_path]:
                if os.path.exists(path):
                    os.remove(path)

    def test_append_link_txt(self):
        """Test appending links to a text file."""
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as temp_file:
            temp_path = temp_file.name

        try:
            # Test appending to an empty file
            FileManager.append_link("https://example.com", temp_path)

            with open(temp_path, "r") as f:
                content = f.read()
                assert "https://example.com" in content

            # Test appending another link
            FileManager.append_link("https://example.com/page", temp_path)

            with open(temp_path, "r") as f:
                content = f.read()
                assert "https://example.com" in content
                assert "https://example.com/page" in content
        finally:
            # Clean up
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def test_append_link_csv(self):
        """Test appending links to a CSV file."""
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as temp_file:
            temp_path = temp_file.name

        try:
            # Test appending to an empty file - our implementation adds a header
            FileManager.append_link("https://example.com", temp_path)

            with open(temp_path, "r", newline="") as f:
                reader = csv.reader(f)
                rows = list(reader)
                assert len(rows) == 2  # Header + one data row
                assert rows[0][0] == "url"  # Header
                assert rows[1][0] == "https://example.com"  # Link

            # Test appending another link
            FileManager.append_link("https://example.com/page", temp_path)

            with open(temp_path, "r", newline="") as f:
                reader = csv.reader(f)
                rows = list(reader)
                assert len(rows) == 3  # Header + two data rows
                assert rows[0][0] == "url"
                assert rows[1][0] == "https://example.com"
                assert rows[2][0] == "https://example.com/page"
        finally:
            # Clean up
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def test_append_link_json(self):
        """Test appending links to a JSON file."""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as temp_file:
            # Initialize with an empty JSON array
            temp_file.write(b"[]")
            temp_file.flush()
            temp_path = temp_file.name

        try:
            # Test appending to an initialized JSON file
            FileManager.append_link("https://example.com", temp_path)

            with open(temp_path, "r") as f:
                data = json.load(f)
                assert isinstance(data, list)
                assert len(data) == 1
                assert data[0] == "https://example.com"

            # Test appending another link
            FileManager.append_link("https://example.com/page", temp_path)

            with open(temp_path, "r") as f:
                data = json.load(f)
                assert len(data) == 2
                assert "https://example.com" in data
                assert "https://example.com/page" in data
        finally:
            # Clean up
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def test_unsupported_extension_handling(self):
        """Test handling of unsupported file extensions."""
        # The current implementation defaults to text for unknown extensions
        with tempfile.NamedTemporaryFile(
            suffix=".unsupported", delete=False
        ) as temp_file:
            temp_path = temp_file.name

        try:
            # Should default to text mode
            FileManager.append_link("https://example.com", temp_path)

            with open(temp_path, "r") as f:
                content = f.read()
                assert "https://example.com" in content
        finally:
            # Clean up
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def test_save_page_links_txt(self):
        """Test saving page links to a text file."""
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as temp_file:
            temp_path = temp_file.name

        try:
            # Test saving page links to an empty file
            page_url = "https://example.com"
            links = {"https://example.com/page1", "https://example.com/page2"}

            FileManager.save_page_links(page_url, links, temp_path)

            with open(temp_path, "r") as f:
                content = f.read()
                assert f"Page: {page_url}" in content
                assert "Links found:" in content
                # The spaces are removed when we call replace, so we need to check without the dash+space
                assert "https://example.com/page1" in content
                assert "https://example.com/page2" in content

            # Test appending another page
            second_page = "https://example.com/section"
            more_links = {
                "https://example.com/section/a",
                "https://example.com/section/b",
            }

            FileManager.save_page_links(second_page, more_links, temp_path)

            with open(temp_path, "r") as f:
                content = f.read()
                assert f"Page: {page_url}" in content
                assert f"Page: {second_page}" in content
                assert "https://example.com/section/a" in content
        finally:
            # Clean up
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def test_save_page_links_json(self):
        """Test saving page links to a JSON file."""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as temp_file:
            temp_path = temp_file.name

        try:
            # Test saving page links to an empty file
            page_url = "https://example.com"
            links = {"https://example.com/page1", "https://example.com/page2"}

            FileManager.save_page_links(page_url, links, temp_path)

            with open(temp_path, "r") as f:
                data = json.load(f)
                assert "pages" in data
                assert len(data["pages"]) == 1
                assert data["pages"][0]["page_url"] == page_url
                assert len(data["pages"][0]["links"]) == 2
                assert "https://example.com/page1" in data["pages"][0]["links"]
                assert "https://example.com/page2" in data["pages"][0]["links"]

            # Test appending another page
            second_page = "https://example.com/section"
            more_links = {
                "https://example.com/section/a",
                "https://example.com/section/b",
            }

            FileManager.save_page_links(second_page, more_links, temp_path)

            with open(temp_path, "r") as f:
                data = json.load(f)
                assert len(data["pages"]) == 2
                assert data["pages"][1]["page_url"] == second_page
                assert len(data["pages"][1]["links"]) == 2
        finally:
            # Clean up
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def test_save_page_links_csv(self):
        """Test saving page links to a CSV file."""
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as temp_file:
            temp_path = temp_file.name

        try:
            # Test saving page links to an empty file
            page_url = "https://example.com"
            links = {"https://example.com/page1", "https://example.com/page2"}

            FileManager.save_page_links(page_url, links, temp_path)

            with open(temp_path, "r", newline="") as f:
                reader = csv.reader(f)
                rows = list(reader)
                # No header in the current implementation
                assert len(rows) == 2  # 2 links without header
                # Check that both links are present with correct source page
                source_pages = [row[0] for row in rows]
                found_links = [row[1] for row in rows]
                assert all(sp == page_url for sp in source_pages)
                assert "https://example.com/page1" in found_links
                assert "https://example.com/page2" in found_links

            # Test appending another page
            second_page = "https://example.com/section"
            more_links = {
                "https://example.com/section/a",
                "https://example.com/section/b",
            }

            FileManager.save_page_links(second_page, more_links, temp_path)

            with open(temp_path, "r", newline="") as f:
                reader = csv.reader(f)
                rows = list(reader)
                assert len(rows) == 4  # 4 links without header
                # Check that the new links are present
                source_pages = [row[0] for row in rows]
                assert source_pages.count(second_page) == 2
        finally:
            # Clean up
            if os.path.exists(temp_path):
                os.remove(temp_path)
