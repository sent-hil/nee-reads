# Sandbox Environment

You are running inside an isolated sandbox container. This environment has its own git repository that is separate from the host.

## Git Workflow

### Committing Changes

**IMPORTANT:** Before committing, always run:
1. Python tests: `uv run pytest`
2. Frontend build: `cd web && npm run build`

Only commit if both pass successfully.

```bash
git add .
git commit -m "your commit message"
```

### Pushing Changes
After committing, push your changes so they can be merged on the host:
```bash
git push origin HEAD
```

This pushes to the sandbox's git server at `/repo-origin`. The host can then merge your changes.

### Important Notes
- Your branch name follows the pattern `sandbox/<sandbox-name>`
- Always push before asking the user to merge your changes
- The remote `origin` points to `/repo-origin` (the shared git server)

## Merging on Host
After you push, tell the user to run on the host:
```bash
agent-sandbox merge <sandbox-name>
```

This fetches your commits and merges them into the host's current branch.

## Development Commands

This project uses `uv` for Python dependency management.

### Running the API
```bash
uv run uvicorn api.main:app --reload --port 7002
```

### Running Python Tests
```bash
uv sync --extra dev && uv run pytest
```

### Running Frontend Tests
**Note:** Frontend tests are currently broken due to ESM/Jest configuration issues with Preact. The test infrastructure exists but needs fixing before it can be used.

```bash
cd web && npm install && npm test
```

### Installing Dependencies
```bash
uv sync
```

### Installing Frontend Dependencies
```bash
cd web && npm install
```

## Building

### Building the Frontend
```bash
cd web && npm run build
```

This creates a production build in `web/dist/`.

### Building with Docker
```bash
# Production build
docker-compose build

# Development build
docker-compose --profile dev build
```

## Running the Full Application

### Using Docker Compose (Development)
For local development with hot reload, use the `dev` profile which uses `Dockerfile.dev`:
```bash
docker-compose --profile dev up
```

This starts:
- API server on port 7002 (with hot reload)
- Vite dev server on port 7003 (with hot reload)

### Using Docker Compose (Production)
```bash
docker-compose up
```

This runs the production build on port 7002.

### Manual Development Setup (without Docker)
1. Start the API:
   ```bash
   uv run uvicorn api.main:app --reload --port 7002
   ```

2. Start the frontend dev server (in a separate terminal):
   ```bash
   cd web && npm run dev
   ```
