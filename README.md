# Stock Behavior

See the [Project.md](Project.md) for a detailed description of the project, its goals, and the technologies used.

## Requirements

- [Docker](https://docs.docker.com/get-docker/) — runs the full stack
- [uv](https://docs.astral.sh/uv/getting-started/installation/) — Python package manager
- [Node.js](https://nodejs.org/) 20+
- [Make](https://www.gnu.org/software/make/) — recommended for running commands

## First-time setup

These steps are only needed once to generate the lockfiles that Docker uses during the build.

```bash
# Mac/Linux
# 1. Install Python dependencies and generate uv.lock
uv sync

# 2. Install frontend dependencies and generate package-lock.json
cd frontend && npm install && cd ..

# 3. Copy the environment file and fill in any required values
cp .env.example .env
```

```powershell
# Windows
# 1. Install Python dependencies and generate uv.lock
uv sync

# 2. Install frontend dependencies and generate package-lock.json
cd frontend; npm install; cd ..

# 3. Copy the environment file and fill in any required values
copy .env.example .env
```

## Running the project

```bash
make dev
```

This starts all services via Docker Compose. On first run Docker will build the images, which takes a few minutes.

| Service  | URL                        |
| -------- | -------------------------- |
| Frontend | http://localhost:5173      |
| Backend  | http://localhost:8000      |
| Swagger  | http://localhost:8000/docs |
| Database | localhost:5433             |
| Adminer  | http://localhost:8080      |

## Price data

On startup the backend automatically fetches the last 60 days of 5-minute bars for all S&P 500 companies from Yahoo Finance. This runs in the background and can take a few minutes.

To re-trigger the backfill manually (e.g. after stopping it or resetting the database):

```bash
docker compose exec backend uv run python -c "
from sqlmodel import Session
from backend.database.session import engine
from backend.services.stock_ingestion import ingest_latest_prices
with Session(engine) as s:
    n = ingest_latest_prices(s, force=True, period='60d')
    print(f'Ingested {n} rows')
"
```

While the market is open, the backend also polls for new bars every 5 minutes automatically.

## Development

To rebuild the Docker images after making structural changes to the backend, run:

```bash
docker compose up -d --build
```

Structural changes include adding new dependencies, changing the database schema, or modifying the Dockerfile.
