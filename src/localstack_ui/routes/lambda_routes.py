from starlette.routing import Route
from starlette.templating import Jinja2Templates

from ..services.lambda_service import LambdaServiceError, lambda_service

templates = Jinja2Templates(directory="templates")


async def list_functions(request):
    """List all Lambda functions."""
    error_message = None
    functions = []
    search_query = request.query_params.get("search", "").strip()

    try:
        functions = lambda_service.list_functions()

        # Apply search filter if provided
        if search_query:
            functions = [
                func
                for func in functions
                if search_query.lower() in func["function_name"].lower()
                or search_query.lower() in func.get("description", "").lower()
                or search_query.lower() in func.get("runtime", "").lower()
            ]
    except LambdaServiceError as e:
        error_message = str(e)

    return templates.TemplateResponse(
        "lambda/functions.html",
        {
            "request": request,
            "functions": functions,
            "error_message": error_message,
            "search_query": search_query,
            "format_memory_size": lambda_service.format_memory_size,
            "format_timeout": lambda_service.format_timeout,
            "format_code_size": lambda_service.format_code_size,
        },
    )


async def function_detail(request):
    """Show details of a specific Lambda function."""
    function_name = request.path_params["function_name"]
    error_message = None
    function_info = None

    try:
        function_info = lambda_service.get_function(function_name)
        if not function_info:
            error_message = f"Lambda function '{function_name}' not found"
    except LambdaServiceError as e:
        error_message = str(e)

    return templates.TemplateResponse(
        "lambda/function_detail.html",
        {
            "request": request,
            "function_info": function_info,
            "error_message": error_message,
            "format_memory_size": lambda_service.format_memory_size,
            "format_timeout": lambda_service.format_timeout,
            "format_code_size": lambda_service.format_code_size,
        },
    )


# Lambda routes
lambda_routes = [
    Route("/lambda/functions", list_functions, methods=["GET"], name="lambda_functions"),
    Route(
        "/lambda/functions/{function_name}",
        function_detail,
        methods=["GET"],
        name="lambda_function_detail",
    ),
]
