# Exoplanet API

A FastAPI-based service for storing, querying, and analyzing exoplanet data. The project relies on:

- **FastAPI** for building REST endpoints.
- **SQLAlchemy** paired with **PostgreSQL** for ORM-backed persistence.
- **Alembic** for database schema migrations.
- **Pydantic** for request/response validation.
- **Uvicorn** as the ASGI server.
- **Custom middleware** (CORS and structured request logging) for cross-origin support and observability.

Project layout:

```
exoplanet-api/
├── alembic/                # Migration scripts (+ env)
│   └── versions/           # Individual revision files
├── alembic.ini             # Alembic configuration
├── app/
│   ├── api/
│   │   └── routes/         # FastAPI routers (system, planets, visualization)
│   ├── core/               # Config, logging helpers, security utilities
│   ├── db/                 # SQLAlchemy Base, models, session factory
│   ├── middleware/         # CORS + logging middleware
│   └── schemas/            # Pydantic schemas for request/response models
├── logs/                   # Runtime log directory (.gitkeep placeholder)
├── main.py                 # FastAPI app bootstrap + uvicorn entrypoint
├── planets_data.sql        # Sample dataset
└── requirements.txt        # Python dependencies
```

