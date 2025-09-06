"""
Logging middleware for FastAPI requests.

This module defines an HTTP middleware that logs details of each incoming
request and its corresponding response. It generates a unique request ID
to correlate log entries across the lifecycle of a request. Logged fields
include HTTP method, path, status code, execution time, client IP, and
user agent. Errors are captured with full stack trace for easier debugging.

"""

import time
import logging
from fastapi import Request
from app.core.logging import new_request_id, REQUEST_ID_FILTER

logger = logging.getLogger("app.http")


async def access_log_middleware(request: Request, call_next):
    """
    Middleware to log details of each HTTP request/response.

    Each request is assigned a unique request ID and logged with key
    information for observability:
      - HTTP method and path
      - Response status code
      - Duration in milliseconds
      - Client IP address
      - User-Agent header
    If an unhandled exception occurs, the error and full stack trace
    are logged at exception level.

    Args:
        request (Request): The incoming FastAPI request object.
        call_next (Callable): Next handler in the middleware chain.

    Returns:
        Response: The outgoing FastAPI response object.

    Raises:
        Exception: Any unhandled exception from downstream processing.
    """
    rid = new_request_id()
    REQUEST_ID_FILTER.request_id = rid
    start = time.time()

    try:
        response = await call_next(request)
        duration_ms = int((time.time() - start) * 1000)
        client_ip = request.client.host if request.client else "-"
        logger.info(
            "REQ %s %s status=%s dur=%dms ip=%s ua=%s",
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
            client_ip,
            request.headers.get("user-agent", "-"),
        )
        return response

    except Exception:
        duration_ms = int((time.time() - start) * 1000)
        client_ip = request.client.host if request.client else "-"
        logger.exception(
            "ERR %s %s dur=%dms ip=%s",
            request.method,
            request.url.path,
            duration_ms,
            client_ip,
        )
        raise

    finally:
        REQUEST_ID_FILTER.request_id = "-"