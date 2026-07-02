## Requirements

- [Docker](https://docs.docker.com/get-docker/) — runs the full stack
- [uv](https://docs.astral.sh/uv/getting-started/installation/) — Python package manager
- [Node.js](https://nodejs.org/) 20+

## First-time setup

These steps are only needed once to generate the lockfiles that Docker uses during the build.

```bash
# 1. Install Python dependencies and generate uv.lock
uv sync

# 2. Install frontend dependencies and generate package-lock.json
cd frontend && npm install && cd ..

# 3. Copy the environment file and fill in any required values
cp .env.example .env
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

## Development

To rebuild the Docker images after making structural changes to the backend, run:

```bash
docker compose up -d --build
```

Structural changes include adding new dependencies, changing the database schema, or modifying the Dockerfile.
