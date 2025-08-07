from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.errors import ServerErrorMiddleware
from starlette.responses import HTMLResponse, JSONResponse
from starlette.routing import Route
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

from .aws_client import aws_client_factory
from .settings import settings


templates = Jinja2Templates(directory="templates")


async def homepage(request):
    """Home page showing navigation to different services."""
    return templates.TemplateResponse("index.html", {"request": request})


async def health_check(request):
    """Basic health check endpoint for Docker health checks."""
    return HTMLResponse("OK")


async def localstack_health(request):
    """Detailed health check for LocalStack services."""
    health_status = aws_client_factory.health_check()

    # Determine overall status
    overall_healthy = all(
        service["status"] == "healthy" for service in health_status.values()
    )

    status_code = 200 if overall_healthy else 503

    response_data = {
        "status": "healthy" if overall_healthy else "unhealthy",
        "services": health_status,
        "endpoint": settings.LOCALSTACK_ENDPOINT,
    }

    return JSONResponse(response_data, status_code=status_code)


routes = [
    Route("/", homepage, name="home"),
    Route("/health", health_check, name="health"),
    Route("/health/localstack", localstack_health, name="localstack_health"),
]

middleware = [
    Middleware(ServerErrorMiddleware, debug=settings.DEBUG),
]

app = Starlette(
    debug=settings.DEBUG,
    routes=routes,
    middleware=middleware,
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")