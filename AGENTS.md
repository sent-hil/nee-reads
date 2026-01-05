# Sandbox Environment

You are running inside an isolated sandbox container. This environment has its own git repository that is separate from the host.

## Git Workflow

### Committing Changes
Commit your changes as usual:
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
uv run pytest
```

### Running Frontend Tests
```bash
cd web && npm test
```

### Installing Dependencies
```bash
uv sync
```
