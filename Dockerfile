FROM python:3.12-slim

WORKDIR /app

# Install dependencies for moviepy and other packages
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsm6 \
    libxext6 \
    libgl1-mesa-glx \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY run.py .

# Expose the port FastAPI runs on
EXPOSE 8000

# Command to run the application
CMD ["python", "run.py"]