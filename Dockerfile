FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential tzdata && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/
RUN pip install -r requirements.txt

COPY . /app

EXPOSE 8081

# uvicorn con hot reload es solo para dev; para prod podrías quitar --reload
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8081"]
