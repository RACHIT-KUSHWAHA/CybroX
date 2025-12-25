FROM python:3.12-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Install system dependencies
# git: for cloning plugins/modules
# gcc, musl-dev, libffi-dev: for compiling native extensions (uvloop, pytgcrypto)
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    gcc \
    musl-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY . .

# Copy start script and make it executable
COPY start.sh .
RUN chmod +x start.sh

# Expose port (for the dummy web server)
EXPOSE 8080

# Start command
CMD ["./start.sh"]
