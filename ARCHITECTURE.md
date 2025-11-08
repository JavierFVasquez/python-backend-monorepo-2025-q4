# Architecture Documentation

## Hexagonal Architecture (Ports & Adapters)

This project follows the hexagonal architecture pattern to ensure clean separation of concerns and maintainability.

### Layer Structure

```
┌─────────────────────────────────────────────────────────────┐
│                        API Layer                             │
│  - FastAPI Routes                                            │
│  - Request/Response Schemas (Pydantic)                       │
│  - JSON:API Serializers                                      │
└──────────────────────┬───────────────────────────────────────┘
                       │
┌──────────────────────▼───────────────────────────────────────┐
│                   Application Layer                          │
│  - Use Cases (Business Logic)                                │
│  - Orchestration                                             │
└──────────────────────┬───────────────────────────────────────┘
                       │
┌──────────────────────▼───────────────────────────────────────┐
│                    Domain Layer                              │
│  - Entities (Business Objects)                               │
│  - Ports (Interfaces/Abstractions)                           │
└──────────────────────┬───────────────────────────────────────┘
                       │
┌──────────────────────▼───────────────────────────────────────┐
│                 Infrastructure Layer                         │
│  - Adapters (Implementations of Ports)                       │
│  - Database Repositories                                     │
│  - External Service Clients                                  │
│  - Cache Implementations                                     │
└─────────────────────────────────────────────────────────────┘
```

### Benefits

1. **Testability**: Domain and application layers can be tested without infrastructure
2. **Flexibility**: Easy to swap implementations (e.g., switch from PostgreSQL to another DB)
3. **Maintainability**: Clear boundaries between layers
4. **Independence**: Business logic is independent of frameworks and external systems

## Service Communication

### Products ←→ Inventory

The inventory service communicates with the products service via HTTP:

```
┌──────────────┐     HTTP Request      ┌──────────────┐
│              │  ──────────────────►  │              │
│  Inventory   │  X-API-Key Header     │   Products   │
│   Service    │  X-Request-ID         │   Service    │
│              │  ◄──────────────────  │              │
└──────────────┘    JSON:API Response  └──────────────┘
```

**Key Features:**
- API Key authentication for security
- Request ID propagation for tracing
- Automatic retries with exponential backoff
- JSON:API standard responses

## Data Flow Example

### Creating and Managing Inventory

1. Client creates product in Products service
2. Products service stores in PostgreSQL (Supabase)
3. Client creates inventory record in Inventory service
4. Inventory service validates product exists by calling Products service
5. Inventory service stores in MongoDB

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

Request IDs propagate across services for distributed tracing.

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

### API Key Authentication

- Custom header: `X-API-Key`
- Validated on every request
- Shared secret between services
- Returns 401 Unauthorized if invalid

### Environment Variables

All sensitive configuration stored in environment variables:
- Database credentials
- API keys
- Service URLs

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

### Unit Tests
- Domain entities
- Use cases with mocked repositories
- JSON:API serializers
- Error handling

### Integration Tests
- API endpoints with test client
- Database operations (with test DB)
- Service communication (with mocked HTTP)

### Coverage Target
- Minimum 80% code coverage
- Focus on business logic paths
- Test error scenarios

