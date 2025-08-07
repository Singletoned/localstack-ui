from starlette.responses import RedirectResponse, Response
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


async def bucket_contents(request):
    """Show contents of an S3 bucket."""
    bucket_name = request.path_params["bucket_name"]
    error_message = None
    objects = []

    try:
        objects = s3_service.list_objects(bucket_name)
    except S3ServiceError as e:
        error_message = str(e)

    return templates.TemplateResponse(
        "s3/bucket_contents.html",
        {
            "request": request,
            "bucket_name": bucket_name,
            "objects": objects,
            "error_message": error_message,
            "format_file_size": s3_service.format_file_size,
        },
    )


async def upload_file(request):
    """Upload a file to an S3 bucket."""
    bucket_name = request.path_params["bucket_name"]

    if request.method == "GET":
        return templates.TemplateResponse(
            "s3/upload_file.html", {"request": request, "bucket_name": bucket_name}
        )

    # Handle POST request
    try:
        form = await request.form()
        uploaded_file = form.get("file")

        if not uploaded_file or not uploaded_file.filename:
            return templates.TemplateResponse(
                "s3/upload_file.html",
                {
                    "request": request,
                    "bucket_name": bucket_name,
                    "error_message": "No file selected",
                },
            )

        # Read file data
        file_data = await uploaded_file.read()
        file_key = uploaded_file.filename

        success, error_message = s3_service.upload_file(bucket_name, file_key, file_data)

        if success:
            return RedirectResponse(url=f"/s3/buckets/{bucket_name}/contents", status_code=302)
        else:
            return templates.TemplateResponse(
                "s3/upload_file.html",
                {
                    "request": request,
                    "bucket_name": bucket_name,
                    "error_message": error_message,
                },
            )

    except Exception as e:
        return templates.TemplateResponse(
            "s3/upload_file.html",
            {
                "request": request,
                "bucket_name": bucket_name,
                "error_message": f"Upload failed: {e}",
            },
        )


async def download_file(request):
    """Download a file from an S3 bucket."""
    bucket_name = request.path_params["bucket_name"]
    file_key = request.path_params["file_key"]

    success, file_data, error_message = s3_service.download_file(bucket_name, file_key)

    if not success:
        return templates.TemplateResponse(
            "s3/bucket_contents.html",
            {
                "request": request,
                "bucket_name": bucket_name,
                "objects": [],
                "error_message": error_message,
                "format_file_size": s3_service.format_file_size,
            },
        )

    # Determine content type
    content_type = "application/octet-stream"
    if "." in file_key:
        extension = file_key.split(".")[-1].lower()
        content_types = {
            "txt": "text/plain",
            "json": "application/json",
            "csv": "text/csv",
            "html": "text/html",
            "css": "text/css",
            "js": "application/javascript",
            "png": "image/png",
            "jpg": "image/jpeg",
            "jpeg": "image/jpeg",
            "gif": "image/gif",
            "pdf": "application/pdf",
        }
        content_type = content_types.get(extension, "application/octet-stream")

    return Response(
        content=file_data,
        media_type=content_type,
        headers={"Content-Disposition": f'attachment; filename="{file_key}"'},
    )


async def delete_file(request):
    """Delete a file from an S3 bucket."""
    bucket_name = request.path_params["bucket_name"]
    file_key = request.path_params["file_key"]

    if request.method == "GET":
        # Show confirmation page
        return templates.TemplateResponse(
            "s3/delete_file.html",
            {"request": request, "bucket_name": bucket_name, "file_key": file_key},
        )

    # Handle POST request (confirmation)
    success, error_message = s3_service.delete_file(bucket_name, file_key)

    if success:
        return RedirectResponse(url=f"/s3/buckets/{bucket_name}/contents", status_code=302)
    else:
        return templates.TemplateResponse(
            "s3/delete_file.html",
            {
                "request": request,
                "bucket_name": bucket_name,
                "file_key": file_key,
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
    Route(
        "/s3/buckets/{bucket_name}/contents",
        bucket_contents,
        methods=["GET"],
        name="s3_bucket_contents",
    ),
    Route(
        "/s3/buckets/{bucket_name}/upload",
        upload_file,
        methods=["GET", "POST"],
        name="s3_upload_file",
    ),
    Route(
        "/s3/buckets/{bucket_name}/files/{file_key:path}/download",
        download_file,
        methods=["GET"],
        name="s3_download_file",
    ),
    Route(
        "/s3/buckets/{bucket_name}/files/{file_key:path}/delete",
        delete_file,
        methods=["GET", "POST"],
        name="s3_delete_file",
    ),
]
