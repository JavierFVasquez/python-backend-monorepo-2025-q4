FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc g++ curl && \
    rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY 3rdparty/python/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt && rm /tmp/requirements.txt

# Copy proto files
COPY proto ./proto

# Copy application code
COPY libs ./libs
COPY services/inventory ./services/inventory

# Generate protobuf code
RUN python -m grpc_tools.protoc \
    -I./proto \
    --python_out=./services/inventory/infrastructure/grpc \
    --grpc_python_out=./services/inventory/infrastructure/grpc \
    proto/products/products.proto && \
    # Fix imports (absolute → relative) \
    sed -i 's/from products import products_pb2/from . import products_pb2/g' \
    services/inventory/infrastructure/grpc/products/products_pb2_grpc.py && \
    # Create __init__.py to expose generated modules \
    echo '# Generated protobuf code' > services/inventory/infrastructure/grpc/products/__init__.py && \
    echo '# Expose generated modules for easier importing' >> services/inventory/infrastructure/grpc/products/__init__.py && \
    echo 'from . import products_pb2' >> services/inventory/infrastructure/grpc/products/__init__.py && \
    echo 'from . import products_pb2_grpc' >> services/inventory/infrastructure/grpc/products/__init__.py && \
    echo '' >> services/inventory/infrastructure/grpc/products/__init__.py && \
    echo "__all__ = ['products_pb2', 'products_pb2_grpc']" >> services/inventory/infrastructure/grpc/products/__init__.py

ENV PYTHONPATH=/app

EXPOSE 8002

CMD ["python", "-m", "uvicorn", "services.inventory.main:app", "--host", "0.0.0.0", "--port", "8002"]
