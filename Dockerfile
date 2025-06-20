# Use Python 3.11 slim image for smaller size and consistent environment
FROM python:3.11-slim

# Set working directory inside the container
WORKDIR /app

# Install git (required for some Python packages that may need it)
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Create logs directory
RUN mkdir -p /app/logs

# Create a non-root user to run the application (security best practice)
RUN useradd -m -u 1000 mcpuser && \
    chown -R mcpuser:mcpuser /app

# Switch to non-root user
USER mcpuser

# The default command is to run the server
CMD ["python", "server.py"]