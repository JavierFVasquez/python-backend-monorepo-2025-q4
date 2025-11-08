# Architecture Documentation

## Hexagonal Architecture (Ports & Adapters)

This project follows the hexagonal architecture pattern to ensure clean separation of concerns and maintainability.

### Layer Structure - Hexagonal Architecture

```
                    DRIVING ADAPTERS (Puertos de Entrada)
              ┌──────────────────┬──────────────────┐
              │   FastAPI REST   │   gRPC Server    │
              │   (Clientes)     │  (Inter-service) │
              └────────┬─────────┴────────┬─────────┘
                       │                  │
                       ▼                  ▼
       ┌───────────────────────────────────────────────────┐
       │              API LAYER (Adapters)                 │
       │  - HTTP Routes (FastAPI)                          │
       │  - gRPC Servicers                                 │
       │  - Request/Response Schemas (Pydantic)            │
       │  - JSON:API Serializers                           │
       │  - Protocol Buffers (protobuf)                    │
       └───────────────────────┬───────────────────────────┘
                               │
       ┌───────────────────────▼───────────────────────────┐
       │         APPLICATION LAYER (Use Cases)             │
       │  - CreateProduct, GetProduct, UpdateProduct       │
       │  - GetInventory, UpdateInventory                  │
       │  - Business Logic Orchestration                   │
       │  - Uses Domain Entities & Ports                   │
       └───────────────────────┬───────────────────────────┘
                               │
       ┌───────────────────────▼───────────────────────────┐
       │         DOMAIN LAYER (Core Business)              │
       │  ┌──────────────────┬──────────────────┐          │
       │  │    ENTITIES      │      PORTS       │          │
       │  │  (Value Objects) │   (Interfaces)   │          │
       │  ├──────────────────┼──────────────────┤          │
       │  │  - Product       │  - ProductRepo   │          │
       │  │  - Inventory     │  - InventoryRepo │          │
       │  │                  │  - ProductSvcPort│          │
       │  │                  │  - CachePort     │          │
       │  └──────────────────┴──────────────────┘          │
       └───────────────────────┬───────────────────────────┘
                               │
       ┌───────────────────────▼───────────────────────────┐
       │      INFRASTRUCTURE LAYER (Adapters)              │
       │  ┌────────────────────────────────────────────┐   │
       │  │         DRIVEN ADAPTERS (Salida)           │   │
       │  ├────────────────────────────────────────────┤   │
       │  │  - SupabaseRepository (PostgreSQL)         │   │
       │  │  - MongoDBRepository                       │   │
       │  │  - RedisCache                              │   │
       │  │  - ProductsGrpcClient (gRPC Client)        │   │
       │  └────────────────────────────────────────────┘   │
       └───────────────────────────────────────────────────┘
                               │
                               ▼
                    DRIVEN SYSTEMS (External)
              ┌──────────────────┬──────────────────┐
              │   PostgreSQL     │     MongoDB      │
              │   (Supabase)     │   (Atlas)        │
              │                  │                  │
              │     Redis        │  Products gRPC   │
              │   (Cache)        │   Service        │
              └──────────────────┴──────────────────┘
```

**Explicación de las capas:**

1. **API Layer (Driving Adapters)**: 
   - Adaptadores de entrada que reciben requests externos
   - REST API para clientes (FastAPI + JSON:API)
   - gRPC Server para comunicación inter-servicios

2. **Application Layer**: 
   - Casos de uso que implementan la lógica de negocio
   - Orquestan el flujo entre Domain e Infrastructure
   - Son independientes del framework

3. **Domain Layer**: 
   - Núcleo de la aplicación con entidades y reglas de negocio
   - Ports (interfaces) que definen contratos
   - NO tiene dependencias externas

4. **Infrastructure Layer (Driven Adapters)**: 
   - Implementaciones concretas de los Ports
   - Adaptadores de salida (repositories, clients, cache)
   - Detalles técnicos de persistencia y comunicación

### Benefits

1. **Testability**: Domain and application layers can be tested without infrastructure
2. **Flexibility**: Easy to swap implementations (e.g., switch from PostgreSQL to another DB)
3. **Maintainability**: Clear boundaries between layers
4. **Independence**: Business logic is independent of frameworks and external systems

## Service Communication

### Products ←→ Inventory (gRPC)

Los servicios se comunican mediante gRPC para comunicación inter-service de alta performance:

```
┌──────────────────┐                        ┌──────────────────┐
│                  │                        │                  │
│   Inventory      │                        │    Products      │
│   Service        │                        │    Service       │
│                  │                        │                  │
│  ┌────────────┐  │                        │  ┌────────────┐  │
│  │ gRPC Client│  │   gRPC Request         │  │ gRPC Server│  │
│  │ (Driven    │──┼────────────────────────►  │ (Driving   │  │
│  │  Adapter)  │  │   products:50051       │  │  Adapter)  │  │
│  │            │  │                        │  │            │  │
│  │            │  │   Metadata:            │  │            │  │
│  │            │  │   - x-request-id       │  │            │  │
│  │            │◄─┼────────────────────────┼──│            │  │
│  └────────────┘  │   Product Protobuf     │  └────────────┘  │
│                  │                        │                  │
└──────────────────┘                        └──────────────────┘
```

**Key Features:**
- **Protocol Buffers**: Serialización binaria eficiente y tipado fuerte
- **Request ID Metadata**: Propagación de request_id vía metadata para tracing
- **Async/Await**: Cliente y servidor asíncronos usando grpc.aio
- **Channel Reuse**: Conexiones gRPC persistentes y reutilizables
- **Error Handling**: Códigos de estado gRPC estándar (NOT_FOUND, INTERNAL, etc.)

**gRPC Service Definition** (`proto/products/products.proto`):
```protobuf
service ProductsService {
  rpc GetProduct(GetProductRequest) returns (GetProductResponse);
  rpc ProductExists(ProductExistsRequest) returns (ProductExistsResponse);
  rpc ListProducts(ListProductsRequest) returns (ListProductsResponse);
}
```

**Ventajas de gRPC sobre HTTP/REST:**
- ⚡ **Performance**: ~10x más rápido que REST debido a serialización binaria
- 🔒 **Type Safety**: Schemas estrictos con Protocol Buffers
- 🔄 **Streaming**: Soporte nativo para streaming bidireccional
- 📦 **Payload Pequeño**: Mensajes más compactos que JSON
- 🌐 **Multi-language**: Generación de código para múltiples lenguajes

### Protocol Buffers (protobuf) - Code Generation

Los archivos `.proto` definen el contrato de comunicación entre servicios:

**Location**: `proto/products/products.proto`

**Generated Python code**:
- `products_pb2.py`: Mensajes (Product, GetProductRequest, etc.)
- `products_pb2_grpc.py`: Servicios (ProductsServiceStub, ProductsServiceServicer)

**Regeneration**:
```bash
# Generate Python code from proto files
./scripts/generate_proto.sh

# Or manually:
python -m grpc_tools.protoc \
  -I proto \
  --python_out=. \
  --grpc_python_out=. \
  --pyi_out=. \
  proto/products/products.proto
```

**Architecture Impact**:
- Proto files son la **source of truth** para contratos inter-service
- Los cambios en `.proto` requieren regenerar código en ambos servicios
- Versionado de APIs se maneja a nivel de protobuf (ej: `products.v1`, `products.v2`)

## Data Flow Example

### Creating and Managing Inventory

1. **Client creates product** → POST /products (Products Service REST API)
2. **Products service** → Stores in PostgreSQL (Supabase)
3. **Client creates inventory** → POST /inventory (Inventory Service REST API)
4. **Inventory service** → Validates product exists via **gRPC call** to Products Service
   ```
   Inventory Service → ProductsGrpcClient.product_exists(product_id)
                    → gRPC: ProductExists(product_id) 
                    → Products Service gRPC Server
                    → Returns: {exists: true, product: {...}}
   ```
5. **Inventory service** → Stores in MongoDB

### Purchase Flow (Inventory Update)

1. Client requests inventory update (quantity_delta: -5)
2. Inventory service checks current quantity
3. Validates sufficient quantity available
4. Updates MongoDB document
5. Logs structured event with details

## Caching Strategy

Products service implements read-through caching:

```
GET /products/{id}
    ↓
Check Redis Cache
    ↓
  Hit? ──Yes──► Return cached data
    ↓
   No
    ↓
Query PostgreSQL
    ↓
Store in Redis (TTL: 300s)
    ↓
Return data
```

Cache invalidation occurs on:
- PATCH /products/{id}
- DELETE /products/{id}

## Error Handling

All errors follow JSON:API error format:

```json
{
  "errors": [
    {
      "status": "404",
      "title": "Not Found",
      "detail": "Product with id 123 not found",
      "source": {
        "pointer": "/products/123"
      }
    }
  ]
}
```

## Logging Strategy

Structured JSON logging with correlation:

```json
{
  "timestamp": "2024-01-01T12:00:00Z",
  "level": "INFO",
  "service": "products",
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "Product created successfully",
  "product_id": "123"
}
```


## Database Schema

### Products (PostgreSQL)

```sql
CREATE TABLE products (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);
```

### Inventory (MongoDB)

```javascript
{
  _id: ObjectId("..."),
  product_id: "uuid-string",
  quantity: 100,
  last_updated: ISODate("2024-01-01T12:00:00Z")
}

// Index on product_id (unique)
```

## Security

### Client-to-Service Authentication (REST API)

- **API Key Authentication**: Header `X-API-Key`
- Validated on every HTTP/REST request
- Returns 401 Unauthorized if invalid
- Used for external clients accessing REST endpoints

### Service-to-Service Communication (gRPC)

- **Network-level security**: Services within Docker network
- **Future enhancement**: mTLS (mutual TLS) for production
- **Request tracing**: Metadata propagation (x-request-id)

### Environment Variables

All sensitive configuration stored in environment variables:
- Database credentials
- API keys
- Service URLs (REST and gRPC)

## Hexagonal Architecture in Practice

### Products Service - Layer Mapping

```
├── api/                          # API Layer (Driving Adapters)
│   ├── routes.py                 # FastAPI REST endpoints
│   ├── schemas.py                # Pydantic request/response models
│   └── serializers.py            # JSON:API serialization
│
├── application/                  # Application Layer (Use Cases)
│   ├── create_product.py         # CreateProduct use case
│   ├── get_product.py            # GetProduct use case
│   ├── update_product.py         # UpdateProduct use case
│   ├── delete_product.py         # DeleteProduct use case
│   └── list_products.py          # ListProducts use case
│
├── domain/                       # Domain Layer (Core)
│   ├── entities.py               # Product entity (value object)
│   └── ports.py                  # Interfaces (ProductRepository, CachePort)
│
└── infrastructure/               # Infrastructure Layer (Driven Adapters)
    ├── database/
    │   └── models.py             # SQLAlchemy models
    ├── grpc/
    │   └── grpc_server.py        # gRPC server adapter
    ├── supabase_repository.py    # ProductRepository implementation
    └── redis_cache.py            # CachePort implementation
```

### Inventory Service - Layer Mapping

```
├── api/                          # API Layer (Driving Adapters)
│   ├── routes.py                 # FastAPI REST endpoints
│   ├── schemas.py                # Pydantic request/response models
│   └── serializers.py            # JSON:API serialization
│
├── application/                  # Application Layer (Use Cases)
│   ├── get_inventory.py          # GetInventory use case
│   └── update_inventory.py       # UpdateInventory use case
│
├── domain/                       # Domain Layer (Core)
│   ├── entities.py               # Inventory entity (value object)
│   └── ports.py                  # Interfaces (InventoryRepository, ProductServicePort)
│
└── infrastructure/               # Infrastructure Layer (Driven Adapters)
    ├── database/
    │   └── models.py             # MongoDB document models
    ├── grpc/
    │   └── products_grpc_client.py  # gRPC client adapter
    └── mongodb_repository.py     # InventoryRepository implementation
```

**Flujo de Dependencias (Dependency Rule):**

```
API Layer ──────► Application Layer ──────► Domain Layer
    │                    │                        ▲
    │                    │                        │
    │                    ▼                        │
    └──────────► Infrastructure Layer ───────────┘
                 (implements ports)
```

- Las dependencias apuntan HACIA ADENTRO
- Domain NO depende de nadie
- Infrastructure implementa las interfaces (ports) definidas en Domain
- Application usa ports del Domain, no conoce implementaciones concretas

## Observability

### Health Checks

Each service exposes `/health` endpoint:
- Returns 200 OK if service is healthy
- Used by Docker health checks
- Can be extended for dependency checks

### Metrics (Future Enhancement)

Consider adding:
- Prometheus metrics
- Request duration histograms
- Error rate counters
- Cache hit/miss ratios

## Testing Strategy

### Unit Tests (Isolation)
- **Domain entities**: Validation, business rules, value objects
- **Use cases**: With mocked repositories (ports)
- **JSON:API serializers**: Request/response transformations
- **Error handling**: Custom exceptions and error responses
- **gRPC adapters**: With mocked stubs and channels

**Example:**
```python
# Test use case with mocked repository
async def test_get_product():
    mock_repo = Mock(ProductRepository)
    mock_repo.get_by_id.return_value = Product(...)
    
    use_case = GetProduct(mock_repo)
    result = await use_case.execute("123")
    
    assert result.id == "123"
    mock_repo.get_by_id.assert_called_once_with("123")
```

### Integration Tests (Components)
- **REST API endpoints**: With FastAPI TestClient
- **Database operations**: With test database
- **gRPC communication**: With test gRPC server/client
- **Cache operations**: With Redis test instance

**Example:**
```python
# Test REST API endpoint
async def test_create_product_endpoint(client):
    response = await client.post("/products", json={...})
    assert response.status_code == 201
```

### End-to-End Tests (System)
- **Complete flows**: Product creation → Inventory creation
- **gRPC inter-service**: Inventory calling Products via gRPC
- **Error scenarios**: 404s, validation errors, service unavailable

### Test Coverage Targets
- **Minimum 80%** code coverage overall
- **90%+** for domain and application layers
- Focus on:
  - Business logic paths
  - Error scenarios
  - Edge cases
  - gRPC error handling (NOT_FOUND, UNAVAILABLE, etc.)

## Complete Flow Diagrams

### Sequence Diagram: Create Inventory (End-to-End with gRPC)

```
┌────────┐         ┌─────────────┐         ┌─────────────┐         ┌──────────┐
│ Client │         │  Inventory  │         │  Products   │         │ Database │
│        │         │   Service   │         │   Service   │         │          │
└───┬────┘         └──────┬──────┘         └──────┬──────┘         └────┬─────┘
    │                     │                       │                     │
    │ POST /inventory     │                       │                     │
    │ X-Request-ID: R1    │                       │                     │
    │────────────────────►│                       │                     │
    │                     │                       │                     │
    │                     │ Validate request      │                     │
    │                     │ (Pydantic schema)     │                     │
    │                     │                       │                     │
    │                     │ gRPC: ProductExists   │                     │
    │                     │ metadata: x-request-id=R1                   │
    │                     │──────────────────────►│                     │
    │                     │                       │                     │
    │                     │                       │ Query product       │
    │                     │                       │────────────────────►│
    │                     │                       │                     │
    │                     │                       │ Product data        │
    │                     │                       │◄────────────────────│
    │                     │                       │                     │
    │                     │ ProductExistsResponse │                     │
    │                     │ {exists: true, ...}   │                     │
    │                     │◄──────────────────────│                     │
    │                     │                       │                     │
    │                     │ Create Inventory      │                     │
    │                     │ entity (domain)       │                     │
    │                     │                       │                     │
    │                     │ Save to MongoDB       │                     │
    │                     │────────────────────────────────────────────►│
    │                     │                                             │
    │                     │ Inventory saved                             │
    │                     │◄────────────────────────────────────────────│
    │                     │                       │                     │
    │ 201 Created         │                       │                     │
    │ JSON:API response   │                       │                     │
    │◄────────────────────│                       │                     │
    │                     │                       │                     │
```

### Architecture Flow: REST + gRPC Integration

```
External Client
      │
      │ REST API (JSON:API)
      │ Port 8002
      ▼
┌─────────────────────────────────────────┐
│      INVENTORY SERVICE                  │
│                                         │
│  ┌──────────────────────────────────┐   │
│  │  FastAPI Routes (Driving)        │   │
│  └────────────┬─────────────────────┘   │
│               │                         │
│  ┌────────────▼─────────────────────┐   │
│  │  UpdateInventory Use Case        │   │
│  └────────────┬─────────────────────┘   │
│               │                         │
│         ┌─────┴──────┐                  │
│         │            │                  │
│    ┌────▼──────┐ ┌───▼──────────────┐   │
│    │ Inventory │ │ ProductsGrpcClient│  │
│    │ Repository│ │ (ProductServicePort│  │
│    │  (Port)   │ │  implementation)  │   │
│    └────┬──────┘ └───┬──────────────┘   │
│         │            │                  │
└─────────┼────────────┼──────────────────┘
          │            │
          │            │ gRPC Call
          │            │ Port 50051
          │            ▼
          │  ┌─────────────────────────────┐
          │  │   PRODUCTS SERVICE          │
          │  │                             │
          │  │ ┌─────────────────────────┐ │
          │  │ │ gRPC Server (Driving)   │ │
          │  │ └──────────┬──────────────┘ │
          │  │            │                │
          │  │ ┌──────────▼──────────────┐ │
          │  │ │ GetProduct Use Case     │ │
          │  │ └──────────┬──────────────┘ │
          │  │            │                │
          │  │ ┌──────────▼──────────────┐ │
          │  │ │ ProductRepository(Port) │ │
          │  │ └──────────┬──────────────┘ │
          │  │            │                │
          │  └────────────┼────────────────┘
          │               │
          ▼               ▼
    MongoDB          PostgreSQL
    (Atlas)          (Supabase)
```

### Key Architectural Decisions

| Decision | Technology | Rationale |
|----------|-----------|-----------|
| **Inter-service Communication** | gRPC | Performance, type safety, streaming support |
| **Client API** | REST + JSON:API | Standard, widely adopted, easy integration |
| **Architecture** | Hexagonal (Ports & Adapters) | Testability, flexibility, maintainability |
| **Products DB** | PostgreSQL (Supabase) | ACID, relational data, managed service |
| **Inventory DB** | MongoDB (Atlas) | Document-oriented, flexible schema |
| **Cache** | Redis | Fast in-memory, TTL support |
| **Request Tracing** | Request ID propagation | Distributed tracing across services |
| **Serialization** | Protocol Buffers (gRPC) | Compact, fast, type-safe |
| **Serialization** | JSON (REST) | Human-readable, standard |

