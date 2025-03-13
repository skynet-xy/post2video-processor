from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.routes import video, test, reddit

app = FastAPI(title="Post 2 Video API")

# Include routers
app.include_router(video.router, prefix="/api")
app.include_router(test.router, prefix="/api", tags=["test"])
app.include_router(reddit.router, prefix="/api")

# Mount the static directory
app.mount("/videos", StaticFiles(directory="generated/output"), name="videos")


@app.get("/")
async def root():
    return {"message": "Welcome to Post 2 Video API"}
