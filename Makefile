.PHONY: install test lint format clean run help

help:
	@echo "Available commands:"
	@echo "  make install  - Install dependencies using uv"
	@echo "  make test     - Run all tests with coverage"
	@echo "  make lint     - Run linting checks"
	@echo "  make format   - Format code with black"
	@echo "  make clean    - Remove build artifacts"
	@echo "  make run      - Start the web application"

install:
	uv sync --all-extras

test:
	uv run pytest -n auto

test-coverage:
	uv run pytest --cov=src/scrum_capacity_calculator --cov-report=html --cov-report=term

lint:
	uv run ruff check src/ tests/

format:
	uv run black src/ tests/
	uv run ruff check --fix src/ tests/

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

run:
	uv run python app.py
