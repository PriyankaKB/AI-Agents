# Use lightweight Python base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies (for venv, BigQuery, etc.)
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY adk_agent/mcp_news_app ./mcp_news_app
COPY data ./data
COPY setup ./setup
COPY cleanup ./cleanup

# Environment variables (Cloud Run will override as needed)
ENV PORT=8000
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 8000

# Run the ADK agent web interface
# Replace with FastAPI entrypoint if you wrap agent.py in FastAPI
CMD ["adk", "web", "--allow_origins", "regex:https://.*\\.cloudshell\\.dev", "--port", "8000"]
