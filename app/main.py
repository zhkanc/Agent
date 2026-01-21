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

if __name__ == '__main__':
    import uvicorn
    uvicorn.run("app.main:app",
                host="0.0.0.0",
                port=8000,
                reload=True)