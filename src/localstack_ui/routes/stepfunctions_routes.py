from starlette.routing import Route
from starlette.templating import Jinja2Templates

from ..services.stepfunctions_service import StepFunctionsServiceError, stepfunctions_service

templates = Jinja2Templates(directory="templates")


async def list_state_machines(request):
    """List all Step Functions state machines."""
    error_message = None
    state_machines = []
    search_query = request.query_params.get("search", "").strip()

    try:
        state_machines = stepfunctions_service.list_state_machines()
        
        # Apply search filter if provided
        if search_query:
            state_machines = [
                sm for sm in state_machines
                if search_query.lower() in sm["name"].lower()
                or search_query.lower() in sm.get("type", "").lower()
                or search_query.lower() in sm.get("status", "").lower()
            ]
    except StepFunctionsServiceError as e:
        error_message = str(e)

    return templates.TemplateResponse(
        "stepfunctions/state_machines.html",
        {
            "request": request,
            "state_machines": state_machines,
            "error_message": error_message,
            "search_query": search_query,
            "format_date": stepfunctions_service.format_date,
        },
    )


async def state_machine_detail(request):
    """Show details of a specific Step Functions state machine."""
    state_machine_arn = request.path_params["state_machine_arn"]
    error_message = None
    state_machine_info = None
    executions = []

    try:
        state_machine_info = stepfunctions_service.describe_state_machine(state_machine_arn)
        if not state_machine_info:
            error_message = f"State machine not found"
        else:
            # Try to get recent executions
            try:
                executions = stepfunctions_service.list_executions(state_machine_arn, 5)
            except StepFunctionsServiceError:
                # Ignore execution listing errors - just show empty list
                executions = []
    except StepFunctionsServiceError as e:
        error_message = str(e)

    return templates.TemplateResponse(
        "stepfunctions/state_machine_detail.html",
        {
            "request": request,
            "state_machine_info": state_machine_info,
            "executions": executions,
            "error_message": error_message,
            "format_date": stepfunctions_service.format_date,
            "get_state_count": stepfunctions_service.get_state_count,
            "get_state_types": stepfunctions_service.get_state_types,
        },
    )


# Step Functions routes
stepfunctions_routes = [
    Route(
        "/stepfunctions/state-machines",
        list_state_machines,
        methods=["GET"],
        name="stepfunctions_state_machines",
    ),
    Route(
        "/stepfunctions/state-machines/{state_machine_arn:path}",
        state_machine_detail,
        methods=["GET"],
        name="stepfunctions_state_machine_detail",
    ),
]