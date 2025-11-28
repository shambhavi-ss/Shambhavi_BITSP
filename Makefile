.PHONY: help install run test docker-build docker-run docker-stop clean samples

help:
	@echo "Available commands:"
	@echo "  make install        - Install dependencies"
	@echo "  make run           - Run the API server locally"
	@echo "  make test          - Test the API with a sample document"
	@echo "  make evaluate      - Run batch evaluation"
	@echo "  make docker-build  - Build Docker image"
	@echo "  make docker-run    - Run with Docker Compose"
	@echo "  make docker-stop   - Stop Docker Compose"
	@echo "  make samples       - Download training samples"
	@echo "  make clean         - Clean temporary files"

install:
	pip install -r requirements.txt

run:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8080

test:
	python test_api.py

evaluate:
	python evaluate_batch.py

docker-build:
	docker build -t bill-extraction-api .

docker-run:
	docker-compose up -d
	@echo "API running at http://localhost:8080"
	@echo "Check logs: docker-compose logs -f"

docker-stop:
	docker-compose down

samples:
	python download_samples.py

clean:
	rm -rf tmp/*
	rm -rf __pycache__
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.log" -delete
