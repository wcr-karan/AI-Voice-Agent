.PHONY: run dev install lint test clean setup-sheets seed-faq demo

# Install dependencies
install:
	python3 -m pip install -r requirements.txt

# Run development server with auto-reload
dev:
	python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run production server
run:
	python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000

# Lint with ruff
lint:
	python3 -m ruff check app/ tests/
	python3 -m ruff format --check app/ tests/

# Format code
format:
	python3 -m ruff format app/ tests/

# Run tests
test:
	python3 -m pytest tests/ -v

# Run tests with coverage
test-cov:
	python3 -m pytest tests/ -v --cov=app --cov-report=html

# Clean build artifacts
clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .coverage htmlcov

# Setup Google Sheets structure
setup-sheets:
	python3 scripts/setup_google_sheets.py

# Seed FAQ data
seed-faq:
	python3 scripts/seed_faq_data.py

# Run interactive demo simulation
demo:
	python3 scripts/demo_simulation.py
