# Dockerfile

# Base image with Python
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Django project
COPY . .

# Expose port for the Django app
EXPOSE 8000
# Command to run the Django development server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
