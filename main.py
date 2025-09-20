from app.core.logging import setup_logging
setup_logging()

from fastapi import FastAPI
from app.api.routes.health import router as health_router
from app.api.routes.planets import router as planets_router
from app.api.routes.visualization import router as vis_router

from app.middleware.cors import setup_cors
from app.middleware.logging_middleware import access_log_middleware

app = FastAPI(
    title="Exoplanet Database",
    description="A simple API for storing and analyzing exoplanet data.",
    swagger_ui_parameters={"tryItOutEnabled": True},
)

setup_cors(app)
app.middleware("http")(access_log_middleware)

app.include_router(health_router)
app.include_router(planets_router)
app.include_router(vis_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
