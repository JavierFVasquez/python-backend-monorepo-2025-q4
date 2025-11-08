.PHONY: help install test lint format run-products run-inventory docker-up docker-down db-up db-down clean proto migrate migrate-create migrate-rollback migrate-history seed seed-clear seed-inventory seed-inventory-clear seed-all

help:
	@echo "📦 Comandos Disponibles"
	@echo ""
	@echo "🔧 Setup:"
	@echo "  make install           - Instalar pyenv, Poetry y dependencias"
	@echo "  make proto             - Generar código desde archivos .proto"
	@echo "  make migrate           - Ejecutar migraciones de BD"
	@echo "  make seed              - Insertar datos de prueba (productos)"
	@echo "  make seed-inventory    - Insertar datos de prueba (inventario)"
	@echo "  make seed-all          - Insertar datos en todas las BD"
	@echo ""
	@echo "🧪 Testing:"
	@echo "  make test              - Run tests (Poetry)"
	@echo "  make test-pants        - Run tests (Pants - monorepo)"
	@echo ""
	@echo "🔍 Linting & Formatting:"
	@echo "  make lint              - Lint (black, ruff, mypy)"
	@echo "  make format               - Format código"
	@echo "  make lint-pants        - Lint con Pants (monorepo)"
	@echo "  make format-pants         - Format con Pants (monorepo)"
	@echo ""
	@echo "🚀 Run Services (Local):"
	@echo "  make run-products      - Run products service (HTTP:8001 + gRPC:50051)"
	@echo "  make run-inventory     - Run inventory service (HTTP:8002)"
	@echo ""
	@echo "🐳 Docker:"
	@echo "  make docker-up         - Start all services con docker-compose"
	@echo "  make docker-down       - Stop all services"
	@echo "  make db-up             - Solo PostgreSQL local (para desarrollo)"
	@echo "  make db-down           - Detener PostgreSQL"
	@echo ""
	@echo "🧹 Cleanup:"
	@echo "  make clean             - Clean build artifacts"

install:
	@echo "🚀 Configurando el proyecto..."
	@echo "1. Verificando pyenv..."
	@command -v pyenv >/dev/null 2>&1 || { echo "   pyenv no instalado. Instalando..."; brew install pyenv; }
	@eval "$$(pyenv init -)" && pyenv local 3.11.11 2>/dev/null || { echo "   Python 3.11.11 no instalado. Instalando..."; pyenv install 3.11.11; pyenv local 3.11.11; }
	@echo "2. Verificando Poetry..."
	@command -v poetry >/dev/null 2>&1 || { echo "   Poetry no instalado. Instalando..."; curl -sSL https://install.python-poetry.org | python3 -; }
	@export PATH="$$HOME/.local/bin:$$PATH" && poetry config virtualenvs.in-project true
	@echo "3. Instalando dependencias con Poetry..."
	@export PATH="$$HOME/.local/bin:$$PATH" && eval "$$(pyenv init -)" && poetry install
	@echo "4. Generando código gRPC..."
	@./scripts/generate_proto.sh
	@echo "5. Exportando requirements.txt para Pants..."
	@export PATH="$$HOME/.local/bin:$$PATH" && poetry export -f requirements.txt --output 3rdparty/python/requirements.txt --without-hashes --with dev 2>/dev/null || true
	@echo ""
	@echo "✅ Instalación completada!"

# Generar código Python desde archivos .proto
proto:
	@./scripts/generate_proto.sh

# Database Migrations (Products Service)
migrate:
	@echo "🔄 Running database migrations..."
	@export PATH="$$HOME/.local/bin:$$PATH" && eval "$$(pyenv init -)" && cd services/products && poetry run alembic upgrade head
	@echo "✅ Migrations completed!"

migrate-create:
	@echo "📝 Creating new migration..."
	@export PATH="$$HOME/.local/bin:$$PATH" && eval "$$(pyenv init -)" && cd services/products && \
	read -p "Migration name: " name && \
	poetry run alembic revision -m "$$name"

migrate-rollback:
	@echo "⏪ Rolling back last migration..."
	@export PATH="$$HOME/.local/bin:$$PATH" && eval "$$(pyenv init -)" && cd services/products && poetry run alembic downgrade -1

migrate-history:
	@echo "📜 Migration history:"
	@export PATH="$$HOME/.local/bin:$$PATH" && eval "$$(pyenv init -)" && cd services/products && poetry run alembic history

# Database Seeds - Products (PostgreSQL)
seed:
	@echo "🌱 Seeding products database with test data..."
	@export PATH="$$HOME/.local/bin:$$PATH" && eval "$$(pyenv init -)" && cd services/products && poetry run python -m seeds.seed_products

seed-clear:
	@echo "🗑️  Clearing products database..."
	@export PATH="$$HOME/.local/bin:$$PATH" && eval "$$(pyenv init -)" && cd services/products && poetry run python -m seeds.seed_products --clear

# Database Seeds - Inventory (MongoDB)
seed-inventory:
	@echo "🌱 Seeding inventory database with test data..."
	@export PATH="$$HOME/.local/bin:$$PATH" && eval "$$(pyenv init -)" && cd services/inventory && poetry run python -m seeds.seed_inventory --real

seed-inventory-clear:
	@echo "🗑️  Clearing inventory database..."
	@export PATH="$$HOME/.local/bin:$$PATH" && eval "$$(pyenv init -)" && cd services/inventory && poetry run python -m seeds.seed_inventory --clear

# Seed all databases
seed-all:
	@echo "🌱 Seeding all databases..."
	@make seed
	@make seed-inventory

# Tests principales (Poetry - recomendado para desarrollo)
test:
	@echo "🧪 Running tests with Poetry..."
	@export PATH="$$HOME/.local/bin:$$PATH" && eval "$$(pyenv init -)" && poetry run pytest

test-pants:
	@echo "🧪 Running tests with Pants (advanced)..."
	@eval "$$(pyenv init -)" && pants test ::

# Linting principal (Poetry - recomendado para desarrollo)
lint:
	@echo "🔍 Running linters..."
	@export PATH="$$HOME/.local/bin:$$PATH" && eval "$$(pyenv init -)" && poetry run black --check . && poetry run ruff check . && poetry run mypy .

lint-pants:
	@echo "🔍 Running linters with Pants (advanced)..."
	@eval "$$(pyenv init -)" && pants lint ::

# Formatting principal (Poetry - recomendado para desarrollo)
format:
	@echo "✨ Formatting code..."
	@export PATH="$$HOME/.local/bin:$$PATH" && eval "$$(pyenv init -)" && poetry run black . && poetry run ruff check --fix .

format-pants:
	@echo "✨ Formatting code with Pants (advanced)..."
	@eval "$$(pyenv init -)" && pants format ::

run-products:
	@echo "🚀 Running products service (HTTP:8001 + gRPC:50051)..."
	@export PATH="$$HOME/.local/bin:$$PATH" && eval "$$(pyenv init -)" && cd services/products && poetry run python main.py

run-inventory:
	@echo "🚀 Running inventory service (HTTP:8002)..."
	@export PATH="$$HOME/.local/bin:$$PATH" && eval "$$(pyenv init -)" && cd services/inventory && poetry run uvicorn main:app --reload --host 0.0.0.0 --port 8002

docker-up:
	@echo "Starting services with docker-compose..."
	docker-compose up --build

docker-down:
	@echo "Stopping services..."
	docker-compose down

# Solo PostgreSQL local para desarrollo
db-up:
	@echo "🐳 Starting PostgreSQL local..."
	docker-compose up -d postgres
	@echo "✅ PostgreSQL running on localhost:54321"
	@echo "   Database: products_db"
	@echo "   User: postgres"
	@echo "   Password: postgres"
	@echo ""
	@echo "Ahora ejecuta: make migrate"

db-down:
	@echo "🛑 Stopping PostgreSQL..."
	docker-compose down postgres

clean:
	@echo "🧹 Limpiando artifacts de build..."
	rm -rf .pants.d dist/ .pytest_cache htmlcov/ .coverage coverage.json
	rm -rf .venv poetry.lock
	rm -rf ~/.cache/pants ~/.pex
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	@echo "✅ Limpieza completada!"

