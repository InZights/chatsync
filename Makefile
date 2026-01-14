.PHONY: help install test lint format clean build deploy

help:
	@echo "Teams to Slack Migration Pipeline - Available Commands"
	@echo "======================================================="
	@echo "make install      - Install dependencies"
	@echo "make test         - Run all tests"
	@echo "make lint         - Run code quality checks"
	@echo "make format       - Auto-format code"
	@echo "make migrate      - Run migration pipeline"
	@echo "make build        - Build distribution package"
	@echo "make clean        - Clean build artifacts"
	@echo "make docs         - Generate documentation"

install:
	pip install -r requirements.txt
	pip install -e .

test:
	pytest tests/ -v --cov=src --cov-report=term-missing

lint:
	flake8 src tests
	black --check src tests

format:
	black src tests

migrate:
	python migrate.py

build:
	python setup.py sdist bdist_wheel

clean:
	rm -rf build/ dist/ *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

docs:
	@echo "Documentation available in docs/ directory"
	@echo "See docs/README.md for getting started"

.PHONY: validate
validate:
	python validate_solution.py
