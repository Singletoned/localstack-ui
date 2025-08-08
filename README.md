# LocalStack UI

A simple web interface for managing LocalStack AWS services. Built with Python/Starlette and designed for easy maintenance by junior engineers.

## Features

- **S3 Bucket Management**: Create, delete, and list S3 buckets
- **Lambda Viewer**: Browse Lambda functions and their configurations (read-only)
- **Step Functions Viewer**: View state machines and their definitions (read-only)
- **File Operations**: Upload, download, and delete files in S3 buckets (1MB limit)
- **Health Monitoring**: Built-in health checks for LocalStack services

## Architecture

- **Backend**: Python with Starlette web framework
- **Frontend**: Server-side rendered HTML with Bulma CSS framework
- **Infrastructure**: Docker Compose with LocalStack, Nginx, and Playwright
- **Testing**: End-to-end browser tests with Playwright

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Just (command runner) - `brew install just` on macOS

### Run the Application

```bash
# Start everything in the foreground (builds and runs)
just run

# Or run manually
docker compose build
docker compose up

# Check application health
curl http://localhost:8000/health
curl http://localhost:8000/health/localstack
```

The application will be available at:

- **Web UI**: http://localhost:8000
- **LocalStack**: http://localhost:4566

### Pre-loaded Demo Data

LocalStack automatically creates sample resources:

- **S3 Buckets**: `demo-bucket-1`, `demo-bucket-2`, `test-uploads`
- **Lambda Functions**: `hello-world`, `data-processor`
- **Step Functions**: `SimpleExample`, `DataProcessingWorkflow`

## Available Commands

```bash
# Start development environment (builds and runs in foreground)
just run

# Run end-to-end tests
just test

# Format code with ruff
just format

# Clean up Docker resources
just clean
```

## Development

### Project Structure

```
.
├── src/localstack_ui/          # Python application code
│   ├── main.py                 # Starlette application
│   ├── settings.py             # Configuration
│   ├── aws_client.py           # AWS/LocalStack client factory
│   ├── services/               # Business logic services
│   └── routes/                 # HTTP route handlers
├── templates/                  # Jinja2 HTML templates
├── static/                     # CSS and JavaScript files
├── docker/                     # Docker configuration
│   ├── app/                    # Application container
│   ├── localstack/             # LocalStack container with init scripts
│   ├── nginx/                  # Nginx reverse proxy
│   └── playwright/             # E2E testing container
├── tests/                      # Test files
└── compose.yaml                # Docker Compose configuration
```

### Configuration

Environment variables can be set in `envs/localstack-ui.env`:

```bash
# Application settings
DEBUG=true
HOST=0.0.0.0
PORT=8000
MAX_FILE_SIZE_MB=1

# LocalStack connection
LOCALSTACK_ENDPOINT=http://localstack:4566
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=test
AWS_SECRET_ACCESS_KEY=test
```

### Adding New Features

1. **Services**: Add business logic in `src/localstack_ui/services/`
2. **Routes**: Add HTTP handlers in `src/localstack_ui/routes/`
3. **Templates**: Add HTML templates in `templates/`
4. **Tests**: Add E2E tests in `tests/e2e/`

Follow the existing patterns for consistency.

## API Endpoints

### Health Checks

- `GET /health` - Basic health check
- `GET /health/localstack` - Detailed LocalStack service status

### S3 Management

- `GET /s3/buckets` - List all buckets
- `GET /s3/buckets/create` - Show bucket creation form
- `POST /s3/buckets/create` - Create new bucket
- `GET /s3/buckets/{name}/delete` - Show bucket deletion confirmation
- `POST /s3/buckets/{name}/delete` - Delete bucket

More endpoints will be added for file operations and service viewers.

## Testing

```bash
# Run end-to-end tests
just test

# Or manually with Docker Compose
docker compose -f tests/compose.yaml up --build --abort-on-container-exit playwright
```

Tests use Playwright to verify:

- Application loads correctly
- S3 bucket operations work
- Navigation functions properly
- Error handling works as expected

## Troubleshooting

### LocalStack Not Starting

- Check if ports 4566 and 4510-4559 are available
- Verify Docker has enough memory allocated (at least 2GB)
- Check LocalStack logs: `docker compose logs localstack`
- Stop and clean up: `just clean`

### Application Won't Connect to LocalStack

- Ensure LocalStack is healthy: `curl http://localhost:4566/_localstack/health`
- Check health endpoint: `curl http://localhost:8000/health/localstack`
- Verify network configuration in `compose.yaml`

### File Upload Issues

- Default file size limit is 1MB (configurable via `MAX_FILE_SIZE_MB`)
- Ensure bucket exists and is accessible
- Check browser developer tools for JavaScript errors

## Security Considerations

This application is designed for **local development only**. It includes:

- No authentication (open access)
- Test AWS credentials
- Debug mode enabled
- No HTTPS enforcement (except via Nginx proxy)

**Do not deploy to production** without adding proper security measures.

## Contributing

1. Follow the existing code style (enforced by Ruff)
2. Add tests for new functionality
3. Update documentation for API changes
4. Keep the UI simple and accessible

## License

This project is for educational and development purposes.
