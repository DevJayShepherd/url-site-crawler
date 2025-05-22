format:
	black .

lint:
	pylint application/

start:
	python start_crawler.py

run:
	python start_crawler.py
