# Use a slim Python base image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y gcc libpq-dev curl && apt-get clean

# Create working directory
WORKDIR /app

# Copy only the requirements first for caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install --no-cache-dir --root-user-action=ignore -r requirements.txt

# Copy the rest of your code
COPY . .

# Command to run your Django API (adjust if using Gunicorn, etc.)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
