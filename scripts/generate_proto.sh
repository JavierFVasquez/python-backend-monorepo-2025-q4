#!/bin/bash
set -e

# Script para generar código Python desde archivos .proto

echo "🔨 Generating Python code from protobuf files..."

# Directorio base
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$BASE_DIR"

# Activar entorno de Poetry
export PATH="$HOME/.local/bin:$PATH"
eval "$(pyenv init -)" 2>/dev/null || true

# Generar código para Products service
echo "Generating products.proto..."
poetry run python -m grpc_tools.protoc \
  -I./proto \
  --python_out=./services/products/infrastructure/grpc \
  --grpc_python_out=./services/products/infrastructure/grpc \
  proto/products/products.proto

echo "✅ Protobuf code generated successfully!"
echo ""
echo "Generated files:"
echo "  - services/products/infrastructure/grpc/products/products_pb2.py"
echo "  - services/products/infrastructure/grpc/products/products_pb2_grpc.py"

