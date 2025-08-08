# Format code with ruff
format:
    taidy .

# Start development environment in foreground
run:
    docker compose build
    docker compose up

# Run end-to-end tests
test:
    docker compose -f tests/compose.yaml up --build --abort-on-container-exit localstack-ui-playwright

# Clean up Docker resources
clean:
    docker compose down -v --remove-orphans
    docker system prune -f
