## Requirements

- Node.js 18.x
- Docker

## Instructions

1. Run `uv sync` from the root of the repo.
2. Run `npm install` from the `frontend` directory.
3. Create a `.env` file in the root directory copying the contents of `.env.example`.
4. Run `make dev` to start the development environment.

Frontend will be available at `http://localhost:5173` and backend at `http://localhost:8000`. Swagger docs are available at `http://localhost:8000/docs`.
