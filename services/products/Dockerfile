FROM python:3.11-slim as builder

WORKDIR /app

RUN pip install --no-cache-dir pants==2.19.0

COPY pants.toml BUILD pyproject.toml ./
COPY 3rdparty ./3rdparty
COPY libs ./libs
COPY services/products ./services/products

RUN pants export --resolve=python-default

FROM python:3.11-slim

WORKDIR /app

COPY --from=builder /app/dist/export/python/virtualenvs/python-default /opt/venv
COPY libs ./libs
COPY services/products ./services/products

ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONPATH=/app

EXPOSE 8001

CMD ["python", "-m", "uvicorn", "services.products.main:app", "--host", "0.0.0.0", "--port", "8001"]

