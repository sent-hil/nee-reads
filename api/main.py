"""Main FastAPI application."""

from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from api.database import init_database
from api.routes.books import router as books_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan handler - runs on startup and shutdown."""
    # Startup: Initialize database
    await init_database()
    yield
    # Shutdown: Nothing to clean up


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="Nee Reads API",
        description="A personal Goodreads clone for discovering books",
        version="0.1.0",
        lifespan=lifespan,
    )

    # Configure CORS for development
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:7001"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include API routes
    app.include_router(books_router)

    # Serve static files in production
    static_path = Path(__file__).parent.parent / "web" / "dist"
    if static_path.exists():
        app.mount("/assets", StaticFiles(directory=static_path / "assets"), name="assets")

        @app.get("/")
        async def serve_index() -> FileResponse:
            """Serve the main index.html for the SPA."""
            return FileResponse(static_path / "index.html")

        @app.get("/{path:path}")
        async def serve_spa(path: str) -> FileResponse:
            """Serve index.html for all unmatched routes (SPA routing)."""
            file_path = static_path / path
            if file_path.exists() and file_path.is_file():
                return FileResponse(file_path)
            return FileResponse(static_path / "index.html")

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("api.main:app", host="0.0.0.0", port=7000, reload=True)
