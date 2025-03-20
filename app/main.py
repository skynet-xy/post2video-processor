from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.routes import video, crawl
from app.core.config import settings

app = FastAPI(title="Post 2 Video API")

# Set up CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=settings.ALLOW_CREDENTIALS,
    allow_methods=settings.ALLOW_METHODS,
    allow_headers=settings.ALLOW_HEADERS,
)

# Include routers
app.include_router(video.router, prefix="/api")
app.include_router(crawl.router, prefix="/api")

# Mount the static directory
app.mount("/static/output", StaticFiles(directory="generated/output"), name="output")
app.mount("/static/assets", StaticFiles(directory="assets"), name="assets")


@app.get("/")
async def root():
    return {"message": "Welcome to Post 2 Video API"}
