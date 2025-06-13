.PHONY: help install dev-install test test-verbose run run-safe clean build lint format check-format docs

# Default target
help:
	@echo "Ghost Forest Watcher - Development Commands"
	@echo "==========================================="
	@echo ""
	@echo "Available commands:"
	@echo "  install      - Install the package and dependencies"
	@echo "  dev-install  - Install in development mode with dev dependencies"
	@echo "  test         - Run the test suite"
	@echo "  test-verbose - Run tests with verbose output"
	@echo "  run          - Start the main application"
	@echo "  run-safe     - Start the application in safe mode"
	@echo "  lint         - Run code linting"
	@echo "  format       - Format code with black and isort"
	@echo "  check-format - Check code formatting"
	@echo "  clean        - Clean build artifacts and cache"
	@echo "  build        - Build the package"
	@echo "  docs         - Generate documentation"
	@echo ""

# Installation targets
install:
	pip install -r requirements.txt

dev-install: install
	pip install -e .[dev]

# Testing targets
test:
	python -m pytest tests/ -q

test-verbose:
	python -m pytest tests/ -v --tb=short

# Running targets
run:
	python main.py

run-safe:
	python main.py --safe

# Code quality targets
lint:
	flake8 ghost_forest_watcher/ tests/ scripts/
	pylint ghost_forest_watcher/ --disable=C0111,R0903

format:
	black ghost_forest_watcher/ tests/ scripts/ main.py setup.py
	isort ghost_forest_watcher/ tests/ scripts/ main.py setup.py

check-format:
	black --check ghost_forest_watcher/ tests/ scripts/ main.py setup.py
	isort --check-only ghost_forest_watcher/ tests/ scripts/ main.py setup.py

# Build and documentation targets
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete

build: clean
	python setup.py sdist bdist_wheel

docs:
	@echo "Documentation generation would go here"
	@echo "Consider using Sphinx for comprehensive docs"

# Development environment setup
setup-dev: dev-install
	@echo "Development environment setup complete!"
	@echo "Run 'make run' to start the application" 