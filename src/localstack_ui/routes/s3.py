from starlette.responses import HTMLResponse, RedirectResponse
from starlette.routing import Route
from starlette.templating import Jinja2Templates

from ..services.s3 import S3ServiceError, s3_service

templates = Jinja2Templates(directory="templates")


async def list_buckets(request):
    """List all S3 buckets."""
    error_message = None
    success_message = None
    buckets = []

    try:
        buckets = s3_service.list_buckets()
    except S3ServiceError as e:
        error_message = str(e)

    return templates.TemplateResponse(
        "s3/buckets.html",
        {
            "request": request,
            "buckets": buckets,
            "error_message": error_message,
            "success_message": success_message,
        },
    )


async def create_bucket(request):
    """Create a new S3 bucket."""
    if request.method == "GET":
        return templates.TemplateResponse("s3/create_bucket.html", {"request": request})

    # Handle POST request
    form = await request.form()
    bucket_name = form.get("bucket_name", "").strip()

    success, error_message = s3_service.create_bucket(bucket_name)

    if success:
        # Redirect to bucket list with success message
        response = RedirectResponse(url="/s3/buckets", status_code=302)
        # You might want to use flash messages here in a real app
        return response
    else:
        return templates.TemplateResponse(
            "s3/create_bucket.html",
            {"request": request, "error_message": error_message, "bucket_name": bucket_name},
        )


async def delete_bucket(request):
    """Delete an S3 bucket."""
    bucket_name = request.path_params["bucket_name"]

    if request.method == "GET":
        # Show confirmation page
        return templates.TemplateResponse(
            "s3/delete_bucket.html", {"request": request, "bucket_name": bucket_name}
        )

    # Handle POST request (confirmation)
    success, error_message = s3_service.delete_bucket(bucket_name)

    if success:
        # Redirect to bucket list
        return RedirectResponse(url="/s3/buckets", status_code=302)
    else:
        return templates.TemplateResponse(
            "s3/delete_bucket.html",
            {
                "request": request,
                "bucket_name": bucket_name,
                "error_message": error_message,
            },
        )


# S3 routes
s3_routes = [
    Route("/s3/buckets", list_buckets, methods=["GET"], name="s3_buckets"),
    Route("/s3/buckets/create", create_bucket, methods=["GET", "POST"], name="s3_create_bucket"),
    Route(
        "/s3/buckets/{bucket_name}/delete",
        delete_bucket,
        methods=["GET", "POST"],
        name="s3_delete_bucket",
    ),
]