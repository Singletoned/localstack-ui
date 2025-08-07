# Format code with ruff
format:
    ruff format src/
    ruff check --fix src/

# Start development environment in foreground
dev:
    docker compose up --build

# Start development environment in background
dev-bg:
    docker compose up -d --build

# Stop all services
down:
    docker compose down

# View logs from all services
logs:
    docker compose logs -f

# View logs from specific service
logs-app:
    docker compose logs -f localstack-ui

logs-localstack:
    docker compose logs -f localstack

# Run end-to-end tests
test:
    docker compose -f tests/compose.yaml up --build --abort-on-container-exit playwright

# Build all containers
build:
    docker compose build

# Clean up Docker resources
clean:
    docker compose down -v --remove-orphans
    docker system prune -f

# Show application status
status:
    @echo "=== Application Status ==="
    @curl -s http://localhost:8000/health 2>/dev/null && echo " ✓ App is running" || echo " ✗ App is not responding"
    @echo "=== LocalStack Status ==="
    @curl -s http://localhost:4566/_localstack/health 2>/dev/null | python3 -m json.tool 2>/dev/null || echo " ✗ LocalStack is not responding"

# Open application in browser
open:
    open http://localhost:8000

# Shell into running app container
shell:
    docker compose exec localstack-ui bash

# Install Python dependencies locally (for development)
install:
    uv sync
