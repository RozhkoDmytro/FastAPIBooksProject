# Environment file
ENV_FILE = .env

# Run the FastAPI server
run:
	uvicorn books:app --host 0.0.0.0 --port 8000 --reload --reload-exclude "env/*"

# Install dependencies
install:
	pip install -r requirements.txt

# Create and activate a virtual environment
venv:
	python -m venv venv && source venv/bin/activate

# Run tests
test:
	pytest -v tests/

# Format code using Black
format:
	black app/ tests/

# Lint code using Flake8
lint:
	flake8 app/ tests/

# Apply database migrations
migrate:
	alembic upgrade head

# Create a new database migration
makemigrations:
	alembic revision --autogenerate -m "New migration"

# Clean Python cache
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +

# Update dependencies
update:
	pip install --upgrade -r requirements.txt

# Build a Docker image
docker-build:
	docker build -t fastapi-app .

# Run the Docker container
docker-run:
	docker run -p 8000:8000 --env-file $(ENV_FILE) fastapi-app
