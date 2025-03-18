from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.routes import video, reddit
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
app.include_router(reddit.router, prefix="/api")

# Mount the static directory
app.mount("/videos", StaticFiles(directory="generated/output"), name="videos")


@app.get("/")
async def root():
    return {"message": "Welcome to Post 2 Video API"}
