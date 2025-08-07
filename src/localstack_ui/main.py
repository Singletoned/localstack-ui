from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.errors import ServerErrorMiddleware
from starlette.responses import HTMLResponse
from starlette.routing import Route
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

from .settings import settings


templates = Jinja2Templates(directory="templates")


async def homepage(request):
    """Home page showing navigation to different services."""
    return templates.TemplateResponse("index.html", {"request": request})


async def health_check(request):
    """Health check endpoint for Docker health checks."""
    return HTMLResponse("OK")


routes = [
    Route("/", homepage, name="home"),
    Route("/health", health_check, name="health"),
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