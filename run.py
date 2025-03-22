import multiprocessing

import uvicorn

if __name__ == "__main__":
    workers = multiprocessing.cpu_count() * 2 + 1
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=False, workers=8)