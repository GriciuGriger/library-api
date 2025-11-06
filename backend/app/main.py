from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db import Base, engine
from app.models import Book  # Import models so SQLAlchemy can see them
from app.routers import books


app = FastAPI(
    title="Library API",
    description="API for library management system",
    version="1.0.0",
)

# CORS middleware - allows frontend to communicate with API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Library API is running"}


@app.get("/health")
async def health():
    return {"status": "ok"}


# Include routers
app.include_router(books.router)


@app.on_event("startup")
async def startup_event():
    """Create database tables on startup"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

