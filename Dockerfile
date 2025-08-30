FROM python:3

# Set environment variables for Python optimizations
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Set the working directory in the container
WORKDIR /code

# Copy the project code into the container
COPY . /code/

# Upgrade pip, setuptools, wheel
RUN pip install --upgrade pip setuptools wheel setuptools-scm

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libffi-dev \
    libssl-dev \
    cargo \
    mercurial \
 && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir --prefer-binary -r requirements.txt

# Expose the port on which Gunicorn/Django will run
EXPOSE 8000
