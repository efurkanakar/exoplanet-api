from app.core.logging import setup_logging, REQUEST_ID_FILTER, new_request_id
setup_logging()

from fastapi import FastAPI, Request

from app.api.routes.health import router as health_router
from app.api.routes.planets import router as planets_router
from app.api.routes.visualization import router as vis_router


import time
import logging


# FastAPI uygulaması
app = FastAPI(
    title="Exoplanet Database",
    description="A simple API for storing and analyzing exoplanet data.",
    swagger_ui_parameters={"tryItOutEnabled": True},
)

logger = logging.getLogger("app.http")


@app.middleware("http")
async def access_log_middleware(request: Request, call_next):
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
    except Exception as exc:
        duration_ms = int((time.time() - start) * 1000)
        client_ip = request.client.host if request.client else "-"
        logger.exception(
            "ERR %s %s dur=%dms ip=%s",
            request.method, request.url.path, duration_ms, client_ip
        )
        raise
    finally:
        # isteğin sonunda rid sıfırlansın
        REQUEST_ID_FILTER.request_id = "-"


app.include_router(health_router)
app.include_router(planets_router)
app.include_router(vis_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
