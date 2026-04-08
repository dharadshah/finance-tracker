import logging
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.exceptions.finance_exceptions import FinanceBaseException

logger = logging.getLogger(__name__)


def register_exception_handlers(app: FastAPI):

    # --- Handler 1: HTTPException (404, 400, 422 etc.) ---
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        logger.warning(
            f"HTTP {exc.status_code} on {request.method} {request.url} "
            f"-> {exc.detail}"
        )
        return JSONResponse(
            status_code = exc.status_code,
            content     = {
                "error"   : True,
                "status"  : exc.status_code,
                "message" : exc.detail,
                "path"    : str(request.url)
            }
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
                "error"   : True,
                "status"  : 422,
                "message" : "Validation failed",
                "errors"  : errors,
                "path"    : str(request.url)
            }
        )

    # --- Handler 3: Finance Domain Exceptions ---
    @app.exception_handler(FinanceBaseException)
    async def finance_exception_handler(request: Request, exc: FinanceBaseException):
        logger.error(
            f"Domain error on {request.method} {request.url} -> {exc.message}"
        )
        return JSONResponse(
            status_code = 500,
            content     = {
                "error"   : True,
                "status"  : 500,
                "message" : exc.message,
                "path"    : str(request.url)
            }
        )

    # --- Handler 4: Unexpected Exceptions ---
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.critical(
            f"Unexpected error on {request.method} {request.url} -> {str(exc)}",
            exc_info = True
        )
        return JSONResponse(
            status_code = 500,
            content     = {
                "error"   : True,
                "status"  : 500,
                "message" : "An unexpected error occurred",
                "path"    : str(request.url)
            }
        )