import sys
import os

# Add the project root directory to sys.path
# This must be done BEFORE importing any 'app' modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Delayed imports for app modules to ensure sys.path is ready
from app.core.lifespan import lifespan
from app.core.logging import setup_logging
from app.routers import lesson_plan, health, upload


def create_app() -> FastAPI:
    setup_logging()

    app = FastAPI(
        title="Lesson Plan Agent",
        lifespan=lifespan,
    )

    app.include_router(lesson_plan.router)
    app.include_router(health.router)
    app.include_router(upload.router)

    # Mount static files
    app.mount("/static", StaticFiles(directory="app/static"), name="static")

    # Serve index.html at root
    @app.get("/")
    async def read_index():
        return FileResponse("app/static/index.html")

    return app


app = create_app()

if __name__ == '__main__':
    uvicorn.run("app.main:app",
                host="0.0.0.0",
                port=8000,
                reload=True)
