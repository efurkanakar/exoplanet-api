from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

def setup_cors(app) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_origin_regex=settings.CORS_ORIGIN_REGEX,
        allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
        allow_methods=["*"],   # en azından GET/OPTIONS kesin olmalı
        allow_headers=["*"],
    )
