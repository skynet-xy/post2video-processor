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

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p fonts generated/output download assets

# Download default font if not present
RUN if [ ! -f fonts/arial.ttf ] || [ ! -f fonts/arial_bold.ttf ]; then \
    apt-get update && apt-get install -y wget fontconfig && \
    mkdir -p /usr/share/fonts/truetype/ && \
    wget -q -O /usr/share/fonts/truetype/arial.ttf https://github.com/matomo-org/travis-scripts/raw/master/fonts/Arial.ttf && \
    wget -q -O /usr/share/fonts/truetype/arial_bold.ttf https://github.com/matomo-org/travis-scripts/raw/master/fonts/Arial_Bold.ttf && \
    cp /usr/share/fonts/truetype/arial.ttf fonts/arial.ttf && \
    cp /usr/share/fonts/truetype/arial_bold.ttf fonts/arial_bold.ttf && \
    fc-cache -f -v; \
    fi

# Expose the port FastAPI runs on
EXPOSE 8000

# Command to run the application
CMD ["python", "run.py"]