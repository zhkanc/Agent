from contextlib import asynccontextmanager
from fastapi import FastAPI
import logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.info("Application startup")
    yield
    logging.info("Application shutdown")
