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

# Generar para Inventory service
poetry run python -m grpc_tools.protoc \
  -I./proto \
  --python_out=./services/inventory/infrastructure/grpc \
  --grpc_python_out=./services/inventory/infrastructure/grpc \
  proto/products/products.proto

# Arreglar imports (absolutos → relativos)
sed -i '' 's/from products import products_pb2/from . import products_pb2/g' \
  services/products/infrastructure/grpc/products/products_pb2_grpc.py
sed -i '' 's/from products import products_pb2/from . import products_pb2/g' \
  services/inventory/infrastructure/grpc/products/products_pb2_grpc.py

# Crear __init__.py para exponer los módulos generados
echo "Creating __init__.py files..."
cat > services/products/infrastructure/grpc/products/__init__.py << 'EOF'
# Generated protobuf code
# Expose generated modules for easier importing
from . import products_pb2
from . import products_pb2_grpc

__all__ = ['products_pb2', 'products_pb2_grpc']
EOF

cat > services/inventory/infrastructure/grpc/products/__init__.py << 'EOF'
# Generated protobuf code
# Expose generated modules for easier importing
from . import products_pb2
from . import products_pb2_grpc

__all__ = ['products_pb2', 'products_pb2_grpc']
EOF

echo "✅ Protobuf code generated successfully!"
echo ""
echo "Generated files:"
echo "  - services/products/infrastructure/grpc/products/products_pb2.py"
echo "  - services/products/infrastructure/grpc/products/products_pb2_grpc.py"
echo "  - services/inventory/infrastructure/grpc/products/products_pb2.py"
echo "  - services/inventory/infrastructure/grpc/products/products_pb2_grpc.py"

