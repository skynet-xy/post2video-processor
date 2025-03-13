from fastapi import FastAPI
from app.api.routes import video, test, comments

app = FastAPI(title="Post 2 Video API")

# Include routers
app.include_router(video.router, prefix="/api")
app.include_router(test.router, prefix="/api", tags=["test"])
# app.include_router(comments.router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "Welcome to Post 2 Video API"}