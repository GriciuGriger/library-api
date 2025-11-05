from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Library API",
    description="API dla systemu informatycznego biblioteki",
    version="1.0.0",
)

# CORS middleware - pozwoli frontendowi komunikować się z API
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

