FROM python:3.11-slim

WORKDIR /app

# Install system deps for scipy/numpy/xgboost
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ && \
    rm -rf /var/lib/apt/lists/*

# Install Python deps first (layer cache)
COPY pyproject.toml .
RUN pip install --no-cache-dir -e .

# Copy app source
COPY app/ app/

# Railway injects $PORT; default to 8000 for local builds
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
