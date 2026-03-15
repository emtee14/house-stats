# House Stats API
[![Ruff Linter](https://github.com/emtee14/house-stats/actions/workflows/pylint.yml/badge.svg)](https://github.com/emtee14/house-stats/actions/workflows/pylint.yml)
[![Pytest](https://github.com/emtee14/house-stats/actions/workflows/pytest.yml/badge.svg)](https://github.com/emtee14/house-stats/actions/workflows/pytest.yml)
[![Build Web-API Docker Image](https://github.com/emtee14/house-stats/actions/workflows/docker-image.yml/badge.svg)](https://github.com/emtee14/house-stats/actions/workflows/docker-image.yml)
[![Publish Web API container](https://github.com/emtee14/house-stats/actions/workflows/docker-publish.yml/badge.svg)](https://github.com/emtee14/house-stats/actions/workflows/docker-publish.yml)
## Overview

[API HERE](https://api.housestats.co.uk)

House Stats API is a data-driven web service that provides statistical insights into the UK housing market. The API aggregates data from the UK Land Registry Price Paid Dataset and Energy Performance Certificates (EPC) to enable querying, analysis, and statistical summaries of property transactions.

The system exposes RESTful endpoints that allow users to retrieve property sales statistics, aggregated metrics, and other housing insights derived from these datasets.

The project demonstrates the design and implementation of a modern data-focused web API, including database integration, authentication, asynchronous processing, and scalable deployment.

---

## Components

### Web API

The main HTTP interface for the system built using **FastAPI**.

Responsibilities:

- Expose REST endpoints
- Handle authentication and authorisation
- Validate requests and return JSON responses
- Dispatch long-running tasks to the worker queue
- Record API usage for billing

---

### Celery Worker

Handles asynchronous and long-running operations.

Responsibilities:

- Background statistics aggregation
- Usage logging
- Billing aggregation tasks
- Scheduled background jobs

Using Celery allows expensive computations to run outside of the request lifecycle, improving API latency and scalability.

---

### Data Loader

A standalone ingestion tool used to import large datasets into PostgreSQL.

Responsibilities:

- Parse source datasets
- Transform data into the internal schema
- Bulk load large datasets efficiently

The loader is implemented in Rust to allow fast ingestion of large datasets such as the Price Paid dataset and EPC records.

---

## Architecture

The platform is composed of several services working together:

- FastAPI Web API for request handling
- Celery workers for asynchronous tasks
- PostgreSQL for data storage
- Redis for task queuing
- Docker / Kubernetes for deployment

---

## Development

### Requirements

- Python 3.13+
- PostgreSQL
- Redis
- Docker (recommended)

---

### Running Locally

Clone the repository:

```bash
git clone https://github.com/yourusername/house-stats-api.git
cd house-stats-api
```

Switch to Web Server
```bash
cd web-api
```

Install dependencies:

```bash
uv sync
```

Run the API:

```bash
uv run fastapi dev app/main.py
```

Start the Celery worker:

```bash
uv run celery -A app.celery:celery_worker worker -B
```

---

### Docker Compose

The project can be run locally using Docker Compose:

```bash
docker compose up
```

This will start:

- PostgreSQL
- Redis
- Web API
- Celery worker

---

## Deployment

### Database

A PostgreSQL instance is required for production deployments. Database migrations are managed using Alembic.

### Kubernetes

The API and worker services can be deployed to Kubernetes to provide scalability and fault tolerance.

Typical deployment architecture:

- Web API deployment
- Celery worker deployment
- Redis service
- PostgreSQL database
- Ingress or Cloudflare Tunnel for external access

Swith to k8s directory Services
```bash
cd k8s
```

Apply secrets
```bash
kubectl apply -f secrets.yaml
```

Create persistant storages
```bash
kubectl apply -f postgres-svc.yaml
```
```bash
kubectl apply -f redis-pvc.yaml
```

Start Redis and Postgres
```bash
kubectl apply -f postgres.yaml	
```
```bash
kubectl apply -f redis.yaml	
```

Start their associated services
```bash
kubectl apply -f postgres-svc.yaml	
```
```bash
kubectl apply -f redis-svc.yaml	
```

Start Web API, Celery Workers and Celery Beat
```bash
kubectl apply -f web-api.yaml
```
```bash
kubectl apply -f celery-worker.yaml
```
```bash
kubectl apply -f celery-beat.yaml		

```

Start Web API service and Cloudflare tunnel
```bash
kubectl apply -f web-api-svc.yaml
```
```bash
kubectl apply -f cloudflared.yaml	
```

---

## Data Ingest

### Building
```bash
cd data-loader
```

```bash
cargo build --package data-loader --bin data-loader --profile release
```

Define environment variables
```
DATABASE_URL = "host=localhost user=postgres password=mysecretpassword dbname=house_stats"
DATABASE_NAME = "house_stats"
```

```bash
./data-loader
```


## API Documentation

API documentation is automatically generated using **OpenAPI**.

Once the server is running it can be accessed at:

```
/docs
```

---

## Data Sources

This project uses publicly available datasets including:

- UK Land Registry **Price Paid Dataset**
- UK **Energy Performance Certificates (EPC)** dataset

---

## License

This project was developed as part of the **COMP3011 Web Services and Web Data** coursework at the University of Leeds.
