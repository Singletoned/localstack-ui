# Format code with ruff
format:
    ruff format src/
    ruff check --fix src/

# Start development environment in foreground
run:
    docker compose build
    docker compose up

# Run end-to-end tests
test:
    docker compose -f tests/compose.yaml up --build --abort-on-container-exit playwright

# Clean up Docker resources
clean:
    docker compose down -v --remove-orphans
    docker system prune -f
