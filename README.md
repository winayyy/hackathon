# DataOps Console

A local-first database operations dashboard built with **React, FastAPI, and MySQL**. DataOps Console provides a web interface for running read-only SQL queries, viewing results, inspecting query history, and exporting data.

## Features

- SQL query editor and results table
- SELECT-only SQL validation using SQLGlot
- MySQL integration using SQLAlchemy and PyMySQL
- Query result limit and execution timeout
- Sensitive-value masking
- Query history stored in SQLite
- CSV export with spreadsheet formula-injection protection
- Docker Compose setup for local development
- Kubernetes deployment using Minikube and Kustomize
- Synthetic customer records for demonstration

## Architecture

```text
Browser
   |
   v
React + Nginx
   |
   | /api/*
   v
FastAPI Backend
   |
   v
MySQL Database

FastAPI ----> SQLite Query History
```

Docker Compose runs the frontend, backend, and MySQL as separate services. Nginx serves the React application and forwards API requests to FastAPI.

## Technology Stack

| Component | Technology |
|---|---|
| Frontend | React, Vite, JavaScript |
| Web server | Nginx |
| Backend | Python, FastAPI, Uvicorn |
| SQL validation | SQLGlot |
| Database access | SQLAlchemy, PyMySQL |
| Application database | MySQL 8.4 |
| Query history | SQLite |
| Containers | Docker, Docker Compose |
| Orchestration | Kubernetes, Minikube |
| Kubernetes configuration | Kustomize |
| Testing | pytest |

## Project Structure

```text
dataops-console/
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   ├── requirements-dev.txt
│   ├── Dockerfile
│   ├── .env.example
│   └── tests/
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── App.css
│   │   └── index.css
│   ├── Dockerfile
│   ├── nginx.conf
│   └── package.json
├── db/
│   └── init.sql
├── k8s/
│   ├── base/
│   └── overlays/
│       └── dev/
├── docker-compose.yml
├── .env.example
├── .gitignore
├── README.md
└── command.md
```

## Prerequisites

For the Docker Compose setup:

- Docker Engine
- Docker Compose v2 or compatible
- Git

For the Kubernetes setup, additionally install or configure:

- Minikube
- kubectl
- A working Kubernetes cluster with an Ingress controller

For manual development, additionally install Python and Node.js versions compatible with the project dependencies.

## Quick Start: Docker Compose

### 1. Clone the repository

```bash
git clone https://github.com/winayyy/hackathon.git
cd hackathon
```

### 2. Configure environment variables

Create a local environment file:

```bash
cp .env.example .env
```

Edit `.env` and replace both password placeholders with strong local passwords:

- `MYSQL_ROOT_PASSWORD`
- `MYSQL_PASSWORD`

Never commit `.env` or share its credentials.

### 3. Build and start the services

```bash
docker compose up --build -d
```

Check the service status:

```bash
docker compose ps
```

Check service logs if needed:

```bash
docker compose logs --tail=100
```

### 4. Open the dashboard

Open the application in your browser:

**http://localhost:8082**

### 5. Verify the API and database

```bash
curl -i http://localhost:8082/health
curl -i http://localhost:8082/api/db-health
```

Expected health responses indicate that the API is running and the database is connected.

### 6. Try a sample query

Run this query in the dashboard:

```sql
SELECT id, name, city, status
FROM customers
ORDER BY id;
```

The initialization script supplies synthetic records for Vinay, Srinithi, Shamsul, Sai, and Arup.

### Useful Compose commands

```bash
# Show service status
docker compose ps

# Follow logs
docker compose logs -f

# View backend logs
docker compose logs -f dataops-backend

# Rebuild and restart after code changes
docker compose up --build -d

# Stop services while preserving database and history volumes
docker compose down
```

**Data persistence:** Compose uses dedicated named volumes for MySQL data and query history. The SQL initialization script runs automatically when the MySQL data volume is initialized for the first time. Editing the script later does not automatically update an existing database.

Do not use `docker compose down -v` unless you intentionally want to delete the Compose-managed volumes and their stored data.

## API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/health` | Backend health check |
| GET | `/api/db-health` | Database connectivity check |
| POST | `/api/query` | Validate and execute a query |
| GET | `/api/query-history` | Retrieve query history |

Example query request:

```bash
curl -X POST http://localhost:8082/api/query \
  -H "Content-Type: application/json" \
  -d '{"query":"SELECT id, name, city, status FROM customers"}'
```

## Running Tests

Create and activate a Python virtual environment if one does not already exist:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
python -m pytest tests -q
```

The test suite covers API behavior and security-related functionality. Run it before submitting changes.

## Kubernetes Deployment

The repository includes Kubernetes manifests under `k8s/`, organized into a base and a development overlay.

Render the development manifests:

```bash
kubectl kustomize k8s/overlays/dev
```

Apply the manifests to a configured cluster:

```bash
kubectl apply -k k8s/overlays/dev
```

Inspect the resources:

```bash
kubectl get all -n dataops-console
kubectl get ingress -n dataops-console
```

The Kubernetes deployment uses locally available application images and a persistent volume for query history. Its database connectivity configuration is separate from Docker Compose. Review `k8s/base/backend-configmap.yaml`, the backend Secret configuration, and `command.md` before deploying to another cluster.

The existing development manifests assume that the required images, database connectivity, Secret, storage, and Ingress controller are configured. Rendering the manifests successfully does not by itself guarantee that the application will start.

## Security Considerations

This project is a hackathon prototype and is not a production database administration platform.

- Use synthetic data for demonstrations.
- Use a dedicated database account with only the required permissions.
- Keep passwords in local environment files or Kubernetes Secrets; never commit credentials.
- Validate SQL before execution and retain execution limits.
- Mask sensitive output fields according to your organization's privacy requirements.
- Review query history for sensitive information before storing or exporting it.
- Test SQL validation and permissions independently; application-level SELECT validation is not a replacement for database permissions.
- Review authentication, authorization, audit logging, network restrictions, and secret management before production use.

## Documentation

See [`command.md`](command.md) for operational commands, troubleshooting, and setup details.

## License

No license has been specified yet. Add a license file before distributing the project for reuse.
