FROM python:3.11-slim

WORKDIR /app

# Install required system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    sqlite3 \
    nano \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for better caching)
COPY pyproject.toml .
COPY uv.lock .

# Install Python dependencies
RUN pip install --no-cache-dir gunicorn flask flask-sqlalchemy jinja2 werkzeug psycopg2-binary email-validator

# Copy the application code
COPY . .

# Initialize the database with sample data
RUN python db_setup.py

# Set environment variables
ENV FLASK_APP=main.py
ENV FLASK_ENV=production
ENV SESSION_SECRET=insecure_secret_key_for_educational_purposes_only

# Expose the port the app runs on
EXPOSE 5000

# Command to run the application
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--reuse-port", "--reload", "main:app"]
