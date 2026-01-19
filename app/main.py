from fastapi import FastAPI
from app.core.lifespan import lifespan
from app.core.logging import setup_logging
from app.routers import lesson_plan, health


def create_app() -> FastAPI:
    setup_logging()

    app = FastAPI(
        title="Lesson Plan Agent",
        lifespan=lifespan,
    )

    app.include_router(lesson_plan.router)
    app.include_router(health.router)

    return app


app = create_app()
