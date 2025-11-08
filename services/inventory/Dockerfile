FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc g++ curl && \
    rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY 3rdparty/python/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt && rm /tmp/requirements.txt

# Copy application code
COPY libs ./libs
COPY services/inventory ./services/inventory

ENV PYTHONPATH=/app

EXPOSE 8002

CMD ["python", "-m", "uvicorn", "services.inventory.main:app", "--host", "0.0.0.0", "--port", "8002"]
