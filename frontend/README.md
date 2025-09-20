# Exoplanet Explorer Frontend

This Vite + React client consumes the Exoplanet FastAPI backend and exposes three primary views:

- **Dashboard** – highlights catalog metrics and renders the annual discoveries timeline.
- **Catalog** – interactive table with search, discovery method and year filters, plus client-side pagination.
- **Visualizations** – charts for stellar temperature histogram, yearly discoveries and method distribution.

## Getting started

Install dependencies with your preferred package manager (examples below use **pnpm**, but `npm` or `yarn` also work).

```bash
pnpm install
pnpm dev
```

The app expects the API to be available at `http://localhost:8000` during development. Override the base URL by creating a `.env` file in the `frontend` directory:

```bash
VITE_API_BASE_URL=https://your-api.example.com
```

## Project structure

```
frontend/
  src/
    api/           # HTTP client helpers
    components/    # Reusable UI building blocks
    hooks/         # Data fetching hooks powered by React Query
    pages/         # Route-level views
```

## Production build

```bash
pnpm build
pnpm preview
```

Deploy the contents of the generated `dist/` directory to any static hosting provider.
