from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.db import Base, engine
from app.models import Book  # Import models so SQLAlchemy can see them
from app.routers import books


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Run startup and shutdown tasks for the application."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(
    title="Library API",
    description="API for library management system",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware - allows frontend to communicate with API
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """API information endpoint"""
    return {
        "name": "Library API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health")
async def health():
    """Health check endpoint for monitoring"""
    return {"status": "ok"}


# Include routers
app.include_router(books.router)

