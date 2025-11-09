# Python Backend Monorepo

[![Test Coverage](https://github.com/JavierFVasquez/python-backend-monorepo-2025-q4/actions/workflows/coverage.yml/badge.svg)](https://github.com/JavierFVasquez/python-backend-monorepo-2025-q4/actions/workflows/coverage.yml)
[![codecov](https://codecov.io/gh/JavierFVasquez/python-backend-monorepo-2025-q4/branch/main/graph/badge.svg)](https://codecov.io/gh/JavierFVasquez/python-backend-monorepo-2025-q4)

A scalable Python monorepo containing two microservices (`products` and `inventory`) built with FastAPI, following hexagonal architecture and JSON:API standard.


## Architecture Overview

> 📖 **Para documentación detallada de arquitectura, ver [ARCHITECTURE.md](./ARCHITECTURE.md)**
>
> Incluye:
> - Arquitectura Hexagonal (Ports & Adapters) explicada en detalle
> - Comunicación gRPC entre servicios con diagramas
> - Mapeo de capas y flujo de dependencias
> - Estrategia de testing, logging y caching
> - Diagramas de secuencia end-to-end

```
┌──────────────────────────────────────────────────────────────┐
│                    API Gateway / Client                       │
└───────────┬──────────────────────────┬───────────────────────┘
            │ HTTP/REST                │ HTTP/REST
            ▼                          ▼
  ┌───────────────────┐      ┌───────────────────┐
  │ Products Service  │      │ Inventory Service │
  │                   │      │                   │
  │ HTTP API: 8001    │      │ HTTP API: 8002    │
  │ gRPC API: 50051 ──┼──────┼──► gRPC Client    │
  │                   │ gRPC │                   │
  │ - FastAPI         │      │ - FastAPI         │
  │ - gRPC Server     │      │ - gRPC Client     │
  │ - PostgreSQL      │      │ - MongoDB         │
  │ - Redis Cache     │      │                   │
  └─────────┬─────────┘      └─────────┬─────────┘
            │                          │
            ▼                          ▼
  ┌───────────────────┐      ┌───────────────────┐
  │    Supabase       │      │     MongoDB       │
  │  (PostgreSQL)     │      │                   │
  └───────────────────┘      └───────────────────┘
            │
            ▼
  ┌───────────────────┐
  │       Redis       │
  │      (Cache)      │
  └───────────────────┘
```

## Technology Stack

- **Python Management**: pyenv 2.6.12
- **Dependency Manager**: Poetry 2.2.1 ⭐ (Modern Python packaging)
- **Monorepo Build**: Pants 2.24.0 (Optional for CI/CD)
- **Framework**: FastAPI 0.109.0
- **Inter-Service Communication**: gRPC + Protocol Buffers 🚀
- **Data Validation**: Pydantic v2
- **Databases**: 
  - PostgreSQL (via Supabase) with SQLAlchemy 2.x + asyncpg
  - MongoDB with Beanie ODM + Motor
- **Caching**: Redis
- **Testing**: pytest with pytest-asyncio
- **Linting**: black, ruff, mypy
- **Containerization**: Docker + Docker Compose

## Project Structure

```
.
├── proto/                     # Protocol Buffers definitions
│   └── products/
│       └── products.proto     # Products service contract
├── services/
│   ├── products/              # Products microservice
│   │   ├── domain/            # Business entities & ports
│   │   ├── application/       # Use cases
│   │   ├── infrastructure/    
│   │   │   ├── database/      # PostgreSQL adapter
│   │   │   ├── grpc/          # gRPC server (driving adapter)
│   │   │   │   ├── grpc_server.py
│   │   │   │   └── products/  # Generated proto code
│   │   │   └── redis_cache.py # Cache adapter
│   │   ├── api/               # FastAPI HTTP routes
│   │   ├── migrations/        # Alembic database migrations
│   │   ├── seeds/             # Database seeds & fixtures
│   │   ├── tests/             # Unit & integration tests
│   │   ├── alembic.ini        # Alembic configuration
│   │   └── main.py            # HTTP + gRPC servers
│   └── inventory/             # Inventory microservice
│       ├── domain/            # Business entities & ports
│       ├── application/       # Use cases
│       ├── infrastructure/
│       │   ├── database/      # MongoDB adapter
│       │   └── grpc/          # gRPC client (driven adapter)
│       │       ├── products_grpc_client.py
│       │       └── products/  # Generated proto code
│       ├── api/               # FastAPI HTTP routes
│       ├── tests/
│       └── main.py
├── libs/
│   ├── common/                # Shared utilities
│   │   ├── logging.py         # JSON structured logging
│   │   ├── jsonapi.py         # JSON:API serializers
│   │   ├── errors.py          # Custom exceptions
│   │   └── middleware.py      # Request ID & error handling
│   └── auth/
│       └── api_key.py         # API key validation
├── scripts/
│   └── generate_proto.sh      # Generate Python from .proto
├── pyproject.toml             # Poetry dependencies + tools
├── pants.toml                 # Pantsbuild configuration
├── docker-compose.yml         # Service orchestration
└── Makefile                   # Convenience commands
```

## Quick Start

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- Homebrew (macOS)

### Setup (Una vez)

```bash
# 1. Instalar dependencias
make install

# 2. Configurar variables de entorno
cp env.example .env
# Por defecto usa PostgreSQL local (no necesitas editar nada)

# 3. Levantar PostgreSQL local
make db-up

# 4. Ejecutar migraciones
make migrate

# 5. (Opcional) Insertar datos de prueba
make seed
```

### Desarrollo Local (Recomendado)

```bash
# 1. Levantar PostgreSQL (solo una vez o cuando reinicies)
make db-up

# 2. Run servicios en terminales separadas
# Terminal 1
make run-products   # HTTP:8001 + gRPC:50051

# Terminal 2  
make run-inventory  # HTTP:8002

# 3. Detener PostgreSQL cuando termines
make db-down
```

### Con Docker (Todo junto)

```bash
make docker-up     # Levanta servicios + DBs
make docker-down   # Detener
```

### 🐳 Docker Build & Deployment

#### Build Individual Services

```bash
# Build productos service
make docker-build-products

# Build inventory service
make docker-build-inventory

# Build all services
make docker-build-all
```
### Ejecutar Tests

```bash
make test          # Ejecutar tests con pytest
make test-pants    # Ejecutar tests con Pants + coverage report

# Ver reporte de coverage HTML
open dist/coverage/python/htmlcov/index.html
```

**Reportes generados:**
- 📊 HTML: `dist/coverage/python/htmlcov/index.html` - Reporte visual interactivo
- 📄 JSON: `dist/coverage/python/coverage.json` - Datos estructurados
- 🌐 GitHub Pages: Se publica automáticamente en cada push a main/master
- 📈 Codecov: Dashboard con gráficos históricos y comentarios en PRs

## 📊 Coverage Report

View the latest test coverage report: [Coverage Report](https://app.codecov.io/gh/JavierFVasquez/python-backend-monorepo-2025-q4)

## 📚 Documentation

### Architecture Documentation

📖 **[ARCHITECTURE.md](./ARCHITECTURE.md)** - Documentación completa de arquitectura:
- Hexagonal Architecture (Ports & Adapters) con diagramas explícitos
- Comunicación gRPC inter-servicios
- Flujo de datos y diagramas de secuencia
- Estrategias de testing, caching y logging
- Distributed tracing con Request IDs

📋 **[TECHNICAL_DECISIONS.md](./TECHNICAL_DECISIONS.md)** - Decisiones técnicas y patrones:
- Patrones de diseño implementados (Repository, DI, Strategy)
- Justificación de decisiones arquitectónicas
- Estrategia de versionado de API
- Logs estructurados en JSON
- Propuestas de mejoras para escalabilidad

### API Documentation

FastAPI genera **automáticamente** documentación OpenAPI/Swagger interactiva para ambos servicios:

**Products Service:**
- 📖 Swagger UI: http://localhost:8001/docs
- 📘 ReDoc: http://localhost:8001/redoc

**Inventory Service:**
- 📖 Swagger UI: http://localhost:8002/docs
- 📘 ReDoc: http://localhost:8002/redoc

**Para usar la documentación:**
1. Abre el link de Swagger UI
2. Haz clic en **"Authorize"** e ingresa tu API Key
3. Prueba los endpoints directamente desde la interfaz

**gRPC APIs (Inter-service):**
- Products gRPC: `localhost:50051`
- Inventory → Products: comunicación vía gRPC

### API Versioning

Las APIs están versionadas usando URL path prefix (`/api/v1`, `/api/v2`, etc.):

**Current Version (v1):**
- `POST /api/v1/products` - Create product
- `GET /api/v1/products` - List products
- `GET /api/v1/products/{id}` - Get product
- `PATCH /api/v1/products/{id}` - Update product
- `DELETE /api/v1/products/{id}` - Delete product
- `POST /api/v1/inventory` - Create inventory
- `GET /api/v1/inventory/{id}` - Get inventory
- `PATCH /api/v1/inventory/{id}` - Update inventory

La arquitectura permite agregar nuevas versiones (v2, v3) sin afectar clientes existentes. Ver **[TECHNICAL_DECISIONS.md](./TECHNICAL_DECISIONS.md)** para detalles.

### Structured Logging

Los logs se generan en formato JSON estructurado con contexto completo:

```json
{
  "timestamp": "2025-11-09T10:30:45Z",
  "level": "INFO",
  "service": "products",
  "request_id": "550e8400-e29b-41d4",
  "message": "Product created successfully",
  "product_id": "123",
  "duration_ms": 45.2
}
```

**Características:**
- Request ID propagation para distributed tracing
- Contexto automático (service, module, function, line)
- Timing automático con `LogTimer`
- Integrable con ELK, Datadog, CloudWatch

**Uso básico:**
```python
from libs.common.logging import get_logger, LogTimer

logger = get_logger(__name__)

with LogTimer(logger, "create_product"):
    logger.info("Product created", extra={"product_id": product.id})
```

## API Examples

### Products Service

**Create Product**
```bash
curl -X POST http://localhost:8001/api/v1/products/ \
  -H "X-API-Key: your-secret-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Laptop",
    "description": "High-performance laptop",
    "price": 1299.99
  }'
```

**Get Product**
```bash
curl -X GET http://localhost:8001/api/v1/products/{product_id} \
  -H "X-API-Key: your-secret-api-key"
```

**Update Product**
```bash
curl -X PATCH http://localhost:8001/api/v1/products/{product_id} \
  -H "X-API-Key: your-secret-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "price": 1199.99
  }'
```

**List Products**
```bash
curl -X GET "http://localhost:8001/api/v1/products/?page=1&size=10" \
  -H "X-API-Key: your-secret-api-key"
```

**Delete Product**
```bash
curl -X DELETE http://localhost:8001/api/v1/products/{product_id} \
  -H "X-API-Key: your-secret-api-key"
```

### Inventory Service

**Create Inventory**
```bash
curl -X POST http://localhost:8002/api/v1/inventory/ \
  -H "X-API-Key: your-secret-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": "{product_id}",
    "quantity": 100
  }'
```

**Get Inventory**
```bash
curl -X GET http://localhost:8002/api/v1/inventory/{product_id} \
  -H "X-API-Key: your-secret-api-key"
```

**Update Inventory (Purchase)**
```bash
curl -X PATCH http://localhost:8002/api/v1/inventory/{product_id} \
  -H "X-API-Key: your-secret-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "quantity_delta": -5
  }'
```

## JSON:API Format

All responses follow the JSON:API specification:

**Success Response (Single Resource)**
```json
{
  "data": {
    "type": "products",
    "id": "123",
    "attributes": {
      "name": "Laptop",
      "description": "High-performance laptop",
      "price": "1299.99",
      "created_at": "2024-01-01T12:00:00",
      "updated_at": "2024-01-01T12:00:00"
    }
  }
}
```

**Success Response (Collection)**
```json
{
  "data": [
    {
      "type": "products",
      "id": "123",
      "attributes": {...}
    }
  ],
  "meta": {
    "page": {
      "number": 1,
      "size": 10,
      "total": 50
    }
  }
}
```

**Error Response**
```json
{
  "errors": [
    {
      "status": "404",
      "title": "Not Found",
      "detail": "Product with id 123 not found"
    }
  ]
}
```

## gRPC Communication

### Arquitectura

Este monorepo usa **gRPC** para comunicación inter-service:

```
Cliente Web/Mobile
       │
       ▼
   [FastAPI HTTP:8001] ← Para clientes externos
       │
Products Service
       │
   [gRPC Server:50051] ← Para inter-service
       ▲
       │ gRPC
       │
Inventory Service
   [gRPC Client]
```

### Ventajas de gRPC

- ⚡ **Performance**: Binario (Protocol Buffers) vs JSON
- 🔒 **Type-Safe**: Contratos definidos en `.proto`
- 📦 **Eficiente**: Menor payload, menor latencia
- 🔄 **Streaming**: Soporte para comunicación bidireccional

### Arquitectura Hexagonal

gRPC está implementado siguiendo arquitectura hexagonal:

**Products Service:**
- `proto/products/products.proto` - Definición del contrato
- `services/products/infrastructure/grpc/grpc_server.py` - Adaptador de entrada (driving)
- Expone casos de uso del dominio vía gRPC

**Inventory Service:**
- `services/inventory/infrastructure/grpc/products_grpc_client.py` - Adaptador de salida (driven)
- Implementa el puerto `ProductServicePort`
- Traduce llamadas del dominio a gRPC

### Generar Código desde .proto

Si modificas archivos `.proto`:

```bash
make proto  # Regenera código Python
```

### Hot Reload

Ambos servicios tienen hot-reload activado:
- ✅ Cambios en código Python → reload automático
- ✅ Sin reiniciar manualmente

## Development

### Database Migrations

```bash
make migrate           # Ejecutar migraciones
make migrate-create    # Crear nueva migración
make migrate-rollback  # Rollback última migración
make migrate-history   # Ver historial de migraciones
```

### Seeds & Fixtures

```bash
make seed         # Insertar 10 productos de prueba
make seed-clear   # Limpiar todos los productos
```

### Code Quality

```bash
# Antes de commit
make format    # Formatear código
make lint      # Linters
make test      # Tests
```

## Key Features

- **Hexagonal Architecture**: Clear separation between domain, application, infrastructure, and API layers
- **gRPC Communication**: High-performance inter-service communication with Protocol Buffers
- **Dual Protocol**: HTTP/REST for external clients + gRPC for inter-service
- **Database Migrations**: Alembic for version-controlled schema changes
- **Seeds & Fixtures**: Test data generators for development
- **JSON:API Standard**: Consistent API responses across all HTTP endpoints
- **Request Tracing**: X-Request-ID propagation for distributed tracing
- **Type Safety**: Full type hints with mypy + Protocol Buffers contracts
- **Caching**: Redis-based caching for product queries
- **Structured Logging**: JSON-formatted logs with correlation IDs
- **High Test Coverage**: 80%+ test coverage with pytest
- **Monorepo Benefits**: Shared libraries, consistent tooling, atomic changes

## Health Checks

Each service exposes a health endpoint:

```bash
curl http://localhost:8001/health  # Products
curl http://localhost:8002/health  # Inventory
```

## Stopping Services

```bash
make docker-down
```

## Comandos Útiles

```bash
# Setup
make install       # Instalar dependencias + generar código gRPC
make db-up         # Levantar PostgreSQL local
make migrate       # Ejecutar migraciones
make seed          # Insertar datos de prueba (10 productos)

# Desarrollo
make run-products  # Run products (HTTP:8001 + gRPC:50051)
make run-inventory # Run inventory (HTTP:8002)

# Database
make migrate-create    # Crear nueva migración
make migrate-rollback  # Rollback migración
make seed-clear        # Limpiar datos

# Testing
make test          # Tests
make lint          # Linters
make format        # Format código

# Docker
make docker-up              # Todo junto con Docker
make docker-down            # Detener todos los servicios
make docker-build-products  # Build imagen de products
make docker-build-inventory # Build imagen de inventory
make docker-build-all       # Build todas las imágenes
make db-up                  # Solo PostgreSQL local
make db-down                # Detener PostgreSQL local

# Protobuf
make generate-proto  # Generar código Python desde .proto
```

## License

MIT

--- 

_Creado por Javier Vasquez 👽_