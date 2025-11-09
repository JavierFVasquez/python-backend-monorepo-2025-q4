# Decisiones Técnicas y Patrones de Diseño

## 🏗️ Patrones de Diseño Implementados

### Hexagonal Architecture (Ports & Adapters)
**Justificación**: Separa la lógica de negocio de los detalles de infraestructura.

- **Domain Layer**: Entidades y puertos (interfaces)
- **Application Layer**: Casos de uso independientes del framework
- **Infrastructure Layer**: Adaptadores concretos (DB, gRPC, cache)
- **API Layer**: Adaptadores de entrada (REST, gRPC server)

**Beneficios**: 
- Testing sin dependencias externas
- Intercambio fácil de implementaciones
- Independencia del framework

### Repository Pattern
**Justificación**: Abstrae el acceso a datos y permite múltiples implementaciones.

- `ProductRepository` → Implementado por `SupabaseProductRepository`
- `InventoryRepository` → Implementado por `MongoDBRepository`
- `ProductServicePort` → Implementado por `ProductsGrpcClient`

**Beneficios**: Testing con mocks, cambio de DB sin afectar lógica de negocio.

### Dependency Injection
**Justificación**: Invierte el control y facilita testing.

```python
# FastAPI DI en rutas
repository: ProductRepository = Depends(get_product_repository)
cache: CachePort = Depends(get_cache)
```

**Beneficios**: Componentes desacoplados, fácil testing, configuración centralizada.

### Strategy Pattern
**Justificación**: Permite intercambiar algoritmos/servicios dinámicamente.

- Cache: `RedisCache` implementa `CachePort`
- Product Service: gRPC vs REST (futuro)

### Factory Pattern
**Justificación**: Centraliza la creación de objetos complejos.

```python
# Casos de uso instanciados en routes
use_case = GetInventory(repository, product_service)
```

## 🔧 Decisiones Técnicas Clave

### gRPC para Comunicación Inter-Servicios
**Justificación**: Performance, type-safety y contratos estrictos.

- Protocol Buffers: 10x más rápido que JSON
- Streaming nativo y menor latencia
- Contratos versionables (.proto files)

**Trade-off**: Mayor complejidad vs REST, pero mejor para alta carga.

### JSON:API para Clientes Externos
**Justificación**: Estándar ampliamente adoptado, responses consistentes.

```json
{
  "data": {"type": "products", "id": "123", "attributes": {...}},
  "meta": {"page": {...}}
}
```

**Beneficios**: Paginación estándar, relaciones, errores estructurados.

### PostgreSQL + MongoDB (Polyglot Persistence)
**Justificación**: Usar la DB correcta según el caso de uso.

- **PostgreSQL** (Products): Datos relacionales, ACID, consultas complejas
- **MongoDB** (Inventory): Documentos flexibles, alta escritura

### Redis Cache (Read-Through Pattern)
**Justificación**: Reduce latencia y carga en DB.

- Cache hit → Respuesta inmediata
- Cache miss → Query DB + guardar en cache (TTL 300s)
- Invalidación en UPDATE/DELETE

### Monorepo con Pants Build
**Justificación**: Compartir código, testing unificado, builds incrementales.

- Librería común (`libs/`) reutilizada
- Un solo `pyproject.toml` para dependencias
- Builds y tests paralelos

## 📐 Estrategia de Versionado de API

### Versionado Semántico (v1, v2, v3)
**Implementación**: URL path prefix

```
/api/v1/products      # Versión actual estable
/api/v2/products      # Futuras versiones con breaking changes
```

**Estado Actual**: v1 es la versión productiva

**Política de Nuevas Versiones**:
- Nuevas versiones (v2, v3) conviven con anteriores
- Período de soporte: mínimo 6 meses para versión anterior
- Header `Sunset` indica fecha de fin de soporte
- Documentación mantiene 2 versiones activas

**Breaking Changes Requieren Nueva Versión**:
- Cambio en estructura de response
- Eliminación de campos obligatorios
- Cambio de tipos de dato

**Non-Breaking Changes en Misma Versión**:
- Agregar campos opcionales
- Nuevos endpoints
- Optimizaciones internas
- Mejoras de performance

### Versionado gRPC
Protocol Buffers con packages versionados:

```protobuf
package products.v1;
package products.v2;  // Para breaking changes
```

## 📊 Logs Estructurados (JSON)

### Formato Estándar
```json
{
  "timestamp": "2025-11-09T10:30:00Z",
  "level": "INFO",
  "service": "products",
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "module": "create_product",
  "function": "execute",
  "message": "Product created successfully",
  "product_id": "123",
  "duration_ms": 45
}
```

### Niveles de Log
- **DEBUG**: Detalles de desarrollo (deshabilitado en prod)
- **INFO**: Eventos de negocio (creación, actualización)
- **WARNING**: Situaciones recuperables (cache miss, retry)
- **ERROR**: Errores que requieren atención
- **CRITICAL**: Fallos del sistema

### Request ID Propagation
- Generado en gateway o primer servicio
- Propagado vía headers (REST) y metadata (gRPC)
- Incluido en todos los logs para tracing distribuido

### Contexto de Logs
- **Business Events**: `product_created`, `inventory_updated`
- **Performance**: `duration_ms`, `cache_hit`
- **Errors**: `error_type`, `stack_trace`, `user_action`

## 🚀 Propuestas de Mejoras para Escalabilidad

### 1. Event-Driven Architecture (Kafka/RabbitMQ)
**Problema**: Acoplamiento síncrono entre servicios.

**Solución**: Eventos asíncronos para operaciones no críticas.

```
Products Service → Event: "product_created" → Kafka
Inventory Service → Subscribe → Actualizar catálogo
Notifications Service → Subscribe → Enviar email
```

**Beneficios**: Desacoplamiento, resilencia, procesamiento asíncrono.

### 2. Database Read Replicas
**Problema**: Lecturas sobrecargando la DB principal.

**Solución**: 
- Escrituras → Primary DB
- Lecturas → Read Replicas (load balancing)

**Beneficios**: 10x más capacidad de lectura, HA.

### 3. API Gateway (Kong, Envoy)
**Problema**: Lógica de auth/routing duplicada en servicios.

**Solución**: Gateway centralizado.

```
Client → API Gateway → [auth, rate-limit, routing] → Services
```

**Beneficios**: Rate limiting global, autenticación centralizada, observabilidad.

### 4. Circuit Breaker Pattern (Resilience4j)
**Problema**: Fallos en cascada si un servicio cae.

**Solución**: Circuit breaker en llamadas gRPC.

```python
# Si Products gRPC falla 5 veces → Open circuit
# Inventory retorna respuesta degradada sin product details
```

**Beneficios**: Previene cascading failures, fail-fast.

### 5. Horizontal Pod Autoscaling (HPA)
**Problema**: Picos de tráfico saturan instancias.

**Solución**: Auto-scaling basado en CPU/memoria/requests.

```yaml
# Kubernetes HPA
min_replicas: 2
max_replicas: 10
target_cpu_percent: 70
```

**Beneficios**: Escala automática, reducción de costos en baja demanda.

### 6. Distributed Tracing (Jaeger, OpenTelemetry)
**Problema**: Difícil debuggear flows multi-servicio.

**Solución**: Tracing con spans y correlación.

```
Request → Products (span 1) → gRPC → Inventory (span 2) → MongoDB (span 3)
```

**Beneficios**: Visualización de latencia, identificación de bottlenecks.

### 7. CQRS + Materialized Views
**Problema**: Queries complejas lentas en base transaccional.

**Solución**: 
- **Commands** → PostgreSQL (escrituras)
- **Queries** → MongoDB/Elasticsearch (lecturas optimizadas)

**Beneficios**: Queries super-rápidas, escalamiento independiente.

### 8. Multi-Region Deployment
**Problema**: Latencia para usuarios globales.

**Solución**: Desplegar servicios en múltiples regiones (US, EU, ASIA).

```
User (EU) → EU Gateway → EU Services → Regional DB
```

**Beneficios**: <50ms latency global, cumplimiento GDPR.

## 📦 Decisiones de Infraestructura

### Docker + Docker Compose
**Justificación**: Consistencia dev → prod, reproducibilidad.

### Poetry para Dependencias
**Justificación**: Lock file preciso, resolución de conflictos moderna.

### Alembic para Migraciones
**Justificación**: Versionado de schema, rollbacks seguros.

### Pytest con Mocking
**Justificación**: Testing aislado por capas, 80%+ coverage target.

---

**Última Actualización**: 2025-11-07  
**Mantenido por**: JavierFVasquez

