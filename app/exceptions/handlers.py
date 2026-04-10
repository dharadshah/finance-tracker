import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.exceptions.app_exceptions import AppError

logger = logging.getLogger(__name__)


def register_exception_handlers(app: FastAPI):

    # --- Handler 1: AppError and all subclasses ---
    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError):
        logger.warning(
            f"AppError {exc.status_code} on {request.method} {request.url} "
            f"-> [{exc.code}] {exc.message}"
        )
        return JSONResponse(
            status_code = exc.status_code,
            content     = exc.to_response_content(str(request.url))
        )

    # --- Handler 2: Pydantic Validation Errors ---
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        errors = [
            {
                "field"  : " -> ".join(str(loc) for loc in error["loc"]),
                "message": error["msg"]
            }
            for error in exc.errors()
        ]
        logger.warning(f"Validation error on {request.method} {request.url} -> {errors}")
        return JSONResponse(
            status_code = 422,
            content     = {
                "error": {
                    "code"   : "validation_error",
                    "message": "Request validation failed",
                    "errors" : errors
                },
                "path": str(request.url)
            }
        )

    # --- Handler 3: Unexpected Exceptions ---
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.critical(
            f"Unexpected error on {request.method} {request.url} -> {str(exc)}",
            exc_info=True
        )
        return JSONResponse(
            status_code = 500,
            content     = {
                "error": {
                    "code"   : "internal_error",
                    "message": "An unexpected error occurred"
                },
                "path": str(request.url)
            }
        )