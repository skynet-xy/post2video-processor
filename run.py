import multiprocessing
import os

import uvicorn

if __name__ == "__main__":
    # Check environment variable
    env = os.environ.get("ENV", "development").lower()
    is_production = env != "development"

    if is_production:
        print("Running in production mode")
        workers = multiprocessing.cpu_count() * 2 + 1
        uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=False, workers=8)
    else:
        print("Running in development mode")
        uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)