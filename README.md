# 🚀 Hackathon DevOps Hub

A multi-application workspace built using **React, Python FastAPI, .NET 8, Docker, and Docker Compose**. The project brings multiple applications together under a unified interface and provides a foundation for exploring DevOps practices, containerization, and CI/CD automation.

## 📌 Project Overview

DevOps Hub consists of three containerized applications:

- **React** — Frontend dashboard and navigation.
- **Python FastAPI** — Python backend API with interactive API documentation.
- **.NET 8** — Minimal API backend with a health endpoint.

Each application runs in its own Docker container, and Docker Compose manages the multi-container environment.

## 🏗️ Architecture

```text
                 Developer / Browser
                         |
             +-----------+-----------+
             |           |           |
          React       Python        .NET
         Frontend     FastAPI       API
         :3000        :8000        :5000
             |           |           |
             +-----------+-----------+
                         |
                 Docker Compose
                         |
                Docker Containers
```

## 🛠️ Technology Stack

| Technology | Purpose |
|---|---|
| React | Frontend dashboard |
| JavaScript | Frontend development |
| Python | Backend development |
| FastAPI | Python REST API |
| .NET 8 | Backend API |
| Docker | Application containerization |
| Docker Compose | Multi-container orchestration |
| Nginx | Serving the production React build |
| Ubuntu on WSL2 | Local development environment |
| Git and GitHub | Version control and source hosting |

## 📂 Project Structure

```text
Hackathon/
├── docker-compose.yml
├── .gitignore
│
├── react-app/
│   ├── Dockerfile
│   ├── package.json
│   ├── package-lock.json
│   └── src/
│       ├── App.jsx
│       ├── App.css
│       └── components/
│           ├── Navbar.jsx
│           └── Navbar.css
│
├── python-app/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── main.py
│
└── dotnet-app/
    ├── Dockerfile
    ├── Program.cs
    └── dotnet-app.csproj
```

## ⚙️ Prerequisites

Install the following tools before running the project:

- [Docker Engine](https://docs.docker.com/engine/install/)
- [Docker Compose](https://docs.docker.com/compose/install/)
- [Git](https://git-scm.com/downloads)

The Docker installation must support the `docker compose` command.

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/winayyy/hackathon.git
cd hackathon
```

### 2. Build and start the applications

```bash
docker compose up -d --build
```

Docker Compose builds the application images and starts the containers in the background.

### 3. Check container status

```bash
docker compose ps
```

### 4. Access the applications

| Application | URL |
|---|---|
| React Dashboard | http://localhost:3000 |
| Python FastAPI | http://localhost:8000 |
| Python API Documentation | http://localhost:8000/docs |
| Python Health Check | http://localhost:8000/health |
| .NET API | http://localhost:5000 |
| .NET Health Check | http://localhost:5000/health |

The applications are intended for local development. Their `localhost` URLs are not public production endpoints.

## 🐳 Docker Commands

### Start all applications

```bash
docker compose up -d
```

### Rebuild images and start applications

```bash
docker compose up -d --build
```

### View running containers

```bash
docker compose ps
```

### View application logs

```bash
docker compose logs -f
```

View logs for an individual application:

```bash
docker compose logs -f react-app
docker compose logs -f python-app
docker compose logs -f dotnet-app
```

### Stop all applications

```bash
docker compose down
```

Stopping the containers does not delete the project source code.

## 🩺 Health Checks

The backend applications expose health endpoints for basic availability verification.

**Python FastAPI**

```bash
curl http://localhost:8000/health
```

Expected response:

```json
{
  "status": "healthy",
  "service": "python-api"
}
```

**.NET API**

```bash
curl http://localhost:5000/health
```

Expected response:

```json
{
  "status": "healthy",
  "service": "dotnet-api"
}
```

These endpoints provide basic application health information. They do not yet validate external dependencies such as databases or other services.

## 🔄 Development Workflow

1. Modify the source code in the relevant application directory.
2. Rebuild the affected application image.
3. Restart or recreate the affected container.
4. Verify the application using its local URL and logs.
5. Commit changes using Git and push them to GitHub.

Example:

```bash
git status
git add .
git commit -m "Describe your changes"
git push
```

## 🗺️ Future Enhancements

Planned opportunities to expand the project include:

- Integrate the React frontend with the Python and .NET APIs.
- Add automated health checks and improved monitoring.
- Create a GitHub Actions CI/CD pipeline.
- Add automated testing and image build validation.
- Publish container images to a container registry.
- Deploy the applications to Kubernetes.
- Explore Helm for deployment management.
- Implement GitOps deployments using Argo CD.
- Experiment with canary releases and progressive delivery.
- Add Prometheus and Grafana for monitoring and visualization.

## 🔐 Security Notes

- Never commit passwords, API keys, access tokens, or private credentials.
- Keep environment-specific configuration and secrets out of version control.
- Review configuration files before publishing the repository.
- Restrict CORS and network access appropriately before production deployment.
- Use secure authentication and authorization when adding protected APIs.

## 👨‍💻 Project Status

**Current stage:** Local multi-application development and Docker Compose orchestration.

The project provides a starting point for learning containerization, application integration, CI/CD pipelines, Kubernetes, and progressive deployment strategies.

## 📄 License

No license has been specified yet. Add a license before allowing others to reuse or redistribute the project.
