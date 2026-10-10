# DataOps Console

A local-first database operations dashboard built with React, FastAPI, and MySQL.

## Features

- SQL query editor and results table
- FastAPI backend connected to MySQL
- SELECT-only query validation
- Maximum result limit and query timeout
- Basic masking of sensitive values
- Synthetic demo data for local testing

## Technology Stack

- Frontend: React and Vite
- Backend: Python and FastAPI
- Database: MySQL 8
- SQL validation: SQLGlot
- Database access: SQLAlchemy and PyMySQL

## Project Structure

```text
backend/
  main.py
  requirements.txt
  .env.example
frontend/
  src/
  package.json
  package-lock.json
.gitignore
README.md
```

## Prerequisites

- Python 3.11 or newer, compatible with the listed dependencies
- Node.js compatible with the installed Vite version
- MySQL 8

## Setup

### 1. Configure MySQL

Create a local database named `dataops_demo`, a read-only user named `dataops_reader`, and a `customers` table populated with synthetic demo records.

### 2. Configure the backend

From the repository root, copy the example environment file:

```powershell
Copy-Item backend/.env.example backend/.env
```

Edit `backend/.env` with your local database settings. Never commit this file or share its password.

Install and start the API:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn main:app --reload --host 127.0.0.1 --port 8001
```

### 3. Start the frontend

Open a second terminal at the repository root:

```powershell
cd frontend
npm ci
npm run dev
```

Open the local URL printed by Vite, normally `http://localhost:5173`.

## API Endpoints

- `GET /health`
- `GET /api/db-health`
- `POST /api/query`

## Security

This is a hackathon prototype, not a production database administration tool. Use synthetic data and least-privilege database credentials. SQL validation and sensitive-value masking need additional security review before production use.
