FROM python:3.11-slim

# Prevent Python from writing pyc files & enable unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /code

# Install system deps for building Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libffi-dev \
    libssl-dev \
    cargo \
 && rm -rf /var/lib/apt/lists/*

# Copy requirements first (better caching)
COPY requirements.txt /code/

# Upgrade pip & install deps
RUN pip install --upgrade pip setuptools wheel setuptools-scm \
 && pip install --no-cache-dir --prefer-binary -r requirements.txt

# Copy project code
COPY . /code/

EXPOSE 8000