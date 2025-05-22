format:
	. .venv/bin/activate && black .

lint:
	. .venv/bin/activate && pylint application/

start:
	. .venv/bin/activate && python start_crawler.py

run:
	. .venv/bin/activate && python start_crawler.py -i

test:
	. .venv/bin/activate && pytest

test-verbose:
	. .venv/bin/activate && pytest -v

install:
	@echo "Creating virtual environment..."
	@if command -v python3 >/dev/null 2>&1; then \
		python3 -m venv .venv; \
	elif command -v python >/dev/null 2>&1; then \
		python -m venv .venv; \
	else \
		echo "Error: Neither python3 nor python commands are available"; \
		exit 1; \
	fi
	@echo "Installing dependencies..."
	. .venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt
	@echo "Creating output and logs directories..."
	mkdir -p output logs
	@echo "Setup complete! You can now run the crawler with: make run"

help:
	@echo "Zego Site Crawler - Available Commands"
	@echo "-----------------------------------"
	@echo "make install      - Set up virtual environment and install dependencies"
	@echo "make run          - Run the crawler in interactive mode"
	@echo "make format       - Format code with black"
	@echo "make lint         - Run linting with pylint"
	@echo "make test         - Run tests"
	@echo "make test-verbose - Run tests with verbose output"
	@echo "make help         - Display this help message"

.PHONY: format lint start run test test-verbose install help
