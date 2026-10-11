# DataOps Console — Setup and Command Guide

## 1. Project Overview

DataOps Console is a local proof of concept for querying databases through a web dashboard. It combines a React frontend, a FastAPI backend, and a MySQL database.

**GitHub repository:** https://github.com/winayyy/hackathon

### Technology stack

| Component | Technology |
|---|---|
| Frontend | React, Vite |
| Web server | Nginx |
| Backend API | Python, FastAPI |
| Application database | MySQL 8.4 |
| Query history | SQLite |
| SQL validation | SQLGlot |
| Containerization | Docker |
| Local orchestration | Docker Compose |
| Advanced deployment | Kubernetes, Minikube |
| Kubernetes configuration | Kustomize |
| Version control | Git, GitHub |

### Main features

- Execute read-only SQL queries against MySQL.
- Validate SQL before execution.
- Limit query results.
- Apply masking to selected sensitive fields.
- Record query history.
- Check application and database health.
- Run the application using Docker Compose or Kubernetes.

This is a hackathon proof of concept, not a production-ready database administration platform. Use synthetic data only.

---

## 2. Project Structure

The repository is organized as follows:

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
│   │   ├── index.css
│   │   └── main.jsx
│   ├── Dockerfile
│   ├── nginx.conf
│   ├── package.json
│   └── vite.config.js
├── db/
│   └── init.sql
├── k8s/
│   ├── base/
│   │   ├── namespace.yaml
│   │   ├── backend-configmap.yaml
│   │   ├── backend-pvc.yaml
│   │   ├── serviceaccount.yaml
│   │   ├── backend-deployment.yaml
│   │   ├── backend-service.yaml
│   │   ├── frontend-deployment.yaml
│   │   ├── frontend-service.yaml
│   │   ├── ingress.yaml
│   │   └── kustomization.yaml
│   └── overlays/
│       └── dev/
│           └── kustomization.yaml
├── .env.example
├── .gitignore
├── docker-compose.yml
├── README.md
└── command.md
```

Some local development files, such as `.env`, `.venv`, `node_modules`, and generated database files, are intentionally excluded from Git.

---

## 3. Recommended Setup: Docker Compose

Docker Compose is the easiest way to run the application locally. It starts the frontend, backend, and a dedicated MySQL container.

### 3.1 Prerequisites

Install and verify:

- Docker Engine with Docker Compose v2.
- Git.
- A terminal such as WSL Ubuntu.

Check the installed tools:

```bash
docker --version
docker compose version
git --version
```

### 3.2 Clone the repository

If you have not cloned the project:

```bash
git clone https://github.com/winayyy/hackathon.git
cd hackathon
```

If the repository is already present, enter its directory:

```bash
cd ~/dataops-console
```

Use the actual directory containing your project.

### 3.3 Configure environment variables

Create the local environment file from the template:

```bash
cp .env.example .env
```

If `.env` already exists, do not overwrite it. Check its values locally instead.

Edit `.env` and configure:

```dotenv
MYSQL_ROOT_PASSWORD=your_strong_local_root_password
MYSQL_PASSWORD=your_strong_local_reader_password
```

These are placeholders for your local configuration, not passwords to use literally.

Keep `.env` private. Never commit real credentials to Git or paste them into logs, issue reports, or chat.

### 3.4 Build and start the application

From the directory containing `docker-compose.yml`:

```bash
docker compose config -q
docker compose up --build -d
```

Check the containers:

```bash
docker compose ps
```

The expected services are:

- `dataops-mysql`
- `dataops-backend`
- `dataops-frontend`

Docker Compose creates project-scoped container and volume names. These services use their own database volume and do not require deleting or replacing the separate MySQL container used by the Kubernetes environment.

### 3.5 Open the dashboard

Open this URL in your browser:

**http://localhost:8082**

The frontend runs through Nginx, which forwards API requests to the FastAPI backend.

If the UI appears outdated after rebuilding, perform a hard refresh in the browser.

### 3.6 Verify application health

Check the API health endpoint:

```bash
curl -i http://localhost:8082/health
```

Expected response:

```json
{
  "status": "ok",
  "application": "DataOps Console API"
}
```

Check the database connection:

```bash
curl -i http://localhost:8082/api/db-health
```

Expected response:

```json
{
  "status": "connected",
  "database": "dataops_demo"
}
```

### 3.7 Test a read-only query

Execute the following query in the dashboard:

```sql
SELECT id, name, city, status
FROM customers
ORDER BY id;
```

The included initialization script creates synthetic customer records for Vinay, Srinithi, Shamsul, Sai, and Arup.

Other useful queries:

```sql
SELECT COUNT(*) AS total_customers
FROM customers;
```

```sql
SELECT city, COUNT(*) AS customer_count
FROM customers
GROUP BY city
ORDER BY city;
```

```sql
SELECT status, COUNT(*) AS customer_count
FROM customers
GROUP BY status;
```

The backend is intended to accept read-only queries. Do not assume that SQL validation alone guarantees complete database security.

---

## 4. Useful Docker Compose Commands

Run these commands from the directory containing `docker-compose.yml`.

### Check service status

```bash
docker compose ps
```

### View logs

```bash
docker compose logs -f
```

### View backend logs

```bash
docker compose logs --tail=100 dataops-backend
```

### View frontend logs

```bash
docker compose logs --tail=100 dataops-frontend
```

### View MySQL logs

```bash
docker compose logs --tail=100 dataops-mysql
```

### Restart services

```bash
docker compose restart
```

### Rebuild after code changes

```bash
docker compose up --build -d
```

### Stop the application

```bash
docker compose down
```

`docker compose down` stops and removes the Compose containers and network, but preserves the named volumes by default.

**Important:** Do not use `docker compose down -v` unless you intentionally want to delete the Compose-managed MySQL database and query-history data.

### Database initialization behavior

The file `db/init.sql` is mounted into MySQL's initialization directory.

MySQL runs initialization scripts when its data directory is initialized for the first time. Editing `db/init.sql` later does not automatically rerun the script against an existing database volume.

Do not delete the volume simply to rerun initialization. Apply any required SQL changes deliberately to the intended database.

---

## 5. Run the Backend Tests

The backend includes automated tests.

Activate the project's Python virtual environment if needed, then run:

```bash
cd backend
python -m pytest tests -q
```

Return to the repository root afterward:

```bash
cd ..
```

If the virtual environment is not configured, create one and install the development dependencies:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
python -m pytest tests -q
```

The backend Docker image installs the production dependencies from `requirements.txt`.

---

## 6. Important API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/health` | Check API health |
| GET | `/api/db-health` | Check MySQL connectivity |
| POST | `/api/query` | Execute a validated SQL query |
| GET | `/api/query-history` | Retrieve query history |

### Example query request

```bash
curl -i -X POST http://localhost:8082/api/query \
  -H "Content-Type: application/json" \
  -d '{"query":"SELECT id, name, city, status FROM customers ORDER BY id"}'
```

This request uses the frontend's published port and Nginx's API proxy.

### Example database health request

```bash
curl -i http://localhost:8082/api/db-health
```

---

## 7. Advanced Setup: Kubernetes with Minikube

Use this section when you want to learn or demonstrate the Kubernetes deployment.

**Important:** Kubernetes is a separate environment from Docker Compose. It uses its own application pods, Kubernetes configuration, Secret, and query-history persistent volume. It also connects to a separately managed MySQL container.

Do not delete or recreate your existing Minikube cluster or MySQL data volume just to follow this guide.

### 7.1 Prerequisites

Verify the tools:

```bash
docker --version
kubectl version --client
minikube version
```

Check whether Minikube is already running:

```bash
minikube status
kubectl get nodes
```

If your existing cluster is healthy, continue using it.

If this is a genuinely new development machine and no cluster exists, create one using the Docker driver:

```bash
minikube start --driver=docker
```

Enable the Ingress add-on if it is not already enabled:

```bash
minikube addons enable ingress
```

Verify the Ingress controller:

```bash
kubectl get pods -n ingress-nginx
```

### 7.2 Inspect the existing MySQL container

The Kubernetes configuration uses a separately running MySQL container. Before creating or changing anything, inspect the current environment:

```bash
docker ps
docker inspect dataops-mysql
docker network inspect minikube
```

If `dataops-mysql` already exists, reuse it after confirming its database, credentials, network connectivity, and grants.

**Do not create another container with the same name, delete its volume, or reset its database.**

For a new environment without an existing MySQL container, use a separate database setup and initialize it with the schema in `db/init.sql`. Keep its storage persistent and its credentials private.

### 7.3 Connect MySQL to Minikube

Inspect whether the MySQL container is already connected to the Minikube Docker network:

```bash
docker network inspect minikube
```

If the container is not connected, and the network exists, connect it:

```bash
docker network connect minikube dataops-mysql
```

If Docker reports that the container is already connected, no additional action is necessary.

Find its address on the Minikube network:

```bash
docker inspect dataops-mysql
```

Inspect the `Networks` section of the output and identify the IP address associated with the `minikube` network.

Do not assume the address is the same on every machine.

Check that the database is reachable from the Kubernetes environment before proceeding.

### 7.4 Configure the Kubernetes ConfigMap

Open:

```bash
nano k8s/base/backend-configmap.yaml
```

The database settings should be equivalent to:

```yaml
MYSQL_HOST: "YOUR_MYSQL_MINIKUBE_NETWORK_IP"
MYSQL_PORT: "3306"
MYSQL_DATABASE: "dataops_demo"
MYSQL_USER: "dataops_reader"
HISTORY_DB_PATH: "/app/data/query_history.db"
```

Replace `YOUR_MYSQL_MINIKUBE_NETWORK_IP` with the address discovered in the previous step.

Do not put the database password in the ConfigMap.

Save the file and exit.

### 7.5 Create the namespace

From the repository root:

```bash
kubectl apply -f k8s/base/namespace.yaml
```

Confirm that it exists:

```bash
kubectl get namespace dataops-console
```

### 7.6 Create the backend Secret

The Kubernetes backend requires the password for the read-only MySQL user.

Run:

```bash
read -rsp "Enter the MySQL dataops_reader password: " MYSQL_PASSWORD
echo

kubectl create secret generic dataops-backend-secret \
  -n dataops-console \
  --from-literal=MYSQL_PASSWORD="$MYSQL_PASSWORD" \
  --dry-run=client -o yaml | kubectl apply -f -

unset MYSQL_PASSWORD
```

Use the same password configured for the database user.

Do not commit Secret manifests containing real passwords. Kubernetes Secrets also require appropriate access controls and encryption configuration for production use.

### 7.7 Build the application images

From the repository root:

```bash
docker build -t dataops-backend:1.0 ./backend
docker build -t dataops-frontend:1.0 ./frontend
```

Load the images into Minikube:

```bash
minikube image load dataops-backend:1.0
minikube image load dataops-frontend:1.0
```

Verify:

```bash
minikube image ls | grep dataops
```

If you change the application code later, rebuild and reload the relevant image before restarting the corresponding Deployment.

### 7.8 Validate and apply the manifests

Render the configuration first:

```bash
kubectl kustomize k8s/overlays/dev
```

Apply it:

```bash
kubectl apply -k k8s/overlays/dev
```

The deployment uses the resources defined in `k8s/base`, referenced by the development overlay.

### 7.9 Wait for deployments

```bash
kubectl rollout status deployment/dataops-backend \
  -n dataops-console --timeout=120s

kubectl rollout status deployment/dataops-frontend \
  -n dataops-console --timeout=120s
```

Check resources:

```bash
kubectl get deployments,pods,services -n dataops-console
kubectl get configmap,secret,pvc,serviceaccount,ingress -n dataops-console
```

Pods should become ready. If they do not, inspect the resources and logs before changing anything.

### 7.10 Verify Kubernetes health

Get the Minikube IP:

```bash
minikube ip
```

Test the frontend:

```bash
MINIKUBE_IP=$(minikube ip)

curl -i --max-time 10 \
  -H "Host: dataops.local" \
  "http://$MINIKUBE_IP/"
```

Test database health:

```bash
curl -i --max-time 10 \
  -H "Host: dataops.local" \
  "http://$MINIKUBE_IP/api/db-health"
```

Expected results:

- Frontend: HTTP 200 with HTML.
- Database health: HTTP 200 with JSON reporting a connected database.

### 7.11 Open Kubernetes in a Windows browser

For the existing WSL/Minikube setup, forward the Ingress controller to a local port:

```bash
kubectl port-forward -n ingress-nginx \
  svc/ingress-nginx-controller 8081:80
```

Keep this terminal open while accessing the application.

On Windows, edit the hosts file as Administrator:

```text
C:\Windows\System32\drivers\etc\hosts
```

Add the following entry if it is not already present:

```text
127.0.0.1 dataops.local
```

Open:

`http://dataops.local:8081`

If port `8081` is already occupied, choose another free local port and use it consistently in the port-forward command and URL.

---

## 8. Kubernetes Troubleshooting Commands

### Check cluster status

```bash
minikube status
kubectl get nodes
```

### Check application resources

```bash
kubectl get all -n dataops-console
```

### Inspect Ingress

```bash
kubectl get ingress -n dataops-console
kubectl describe ingress dataops-ingress -n dataops-console
```

### Inspect backend logs

```bash
kubectl logs deployment/dataops-backend -n dataops-console
```

### Inspect frontend logs

```bash
kubectl logs deployment/dataops-frontend -n dataops-console
```

### Describe application pods

```bash
kubectl describe pods -n dataops-console
```

### Inspect persistent storage

```bash
kubectl get pvc -n dataops-console
kubectl get pv
```

### Check MySQL container and networks

```bash
docker ps
docker network inspect minikube
docker logs dataops-mysql
```

### Test the backend using port-forward

In one terminal:

```bash
kubectl port-forward -n dataops-console \
  svc/dataops-backend 8000:8000
```

In another terminal:

```bash
curl -i http://127.0.0.1:8000/health
curl -i http://127.0.0.1:8000/api/db-health
```

Stop port-forward processes with `Ctrl + C` in their respective terminals.

Never share passwords or Secret values when collecting troubleshooting output.

---

## 9. Troubleshooting Docker Compose

### Containers are not healthy

```bash
docker compose ps
docker compose logs --tail=100
```

Inspect the failing service and address its logs before restarting everything.

### Database connection fails

```bash
docker compose logs --tail=100 dataops-mysql
docker compose logs --tail=100 dataops-backend
```

Check that the environment variables are configured correctly and that MySQL has completed initialization.

Inside Compose, the backend connects to the MySQL service using the hostname `dataops-mysql`. Do not substitute the host machine's `localhost` for this service hostname.

### Port 8082 is occupied

The frontend publishes port `8082` on `127.0.0.1`.

Check which process is using the port before changing the Compose configuration. If necessary, choose another free host port in `docker-compose.yml` and recreate the frontend service.

### Frontend shows an old version

After rebuilding the frontend:

```bash
docker compose up --build -d dataops-frontend
```

Perform a hard refresh in the browser.

### Query fails

Check the SQL syntax and verify database health:

```bash
curl -i http://localhost:8082/api/db-health
```

Review the backend logs. The application intentionally restricts query execution, so do not attempt write operations to troubleshoot a read-only query interface.

---

## 10. Security Notes

- Use synthetic or otherwise approved non-production data.
- Use a dedicated MySQL application account with `SELECT` privileges only.
- Keep real credentials in local environment files or appropriately managed Secrets.
- Do not commit `.env`, passwords, database dumps, or Secret manifests containing credentials.
- Do not publish the MySQL port to the public internet.
- Preserve database and query-history storage unless deletion is intentional.
- Treat SQL validation, query limits, timeouts, and PII masking as defense-in-depth safeguards rather than a complete security boundary.
- Review authorization, authentication, auditing, logging, and secret management before any production deployment.
- Do not run destructive Docker volume, database, or Kubernetes cleanup commands without confirming their impact.

---

## 11. Git Commands

Check the working tree:

```bash
git status --short
```

Review the changes:

```bash
git diff --check
git diff
```

Add the intended project files:

```bash
git add README.md command.md backend/main.py \
  .env.example db/init.sql docker-compose.yml
```

Review what will be committed:

```bash
git status --short
git diff --cached --check
git diff --cached --stat
```

Confirm that no real environment files, passwords, generated databases, or other secrets are staged.

Commit when the review is complete:

```bash
git commit -m "Document DataOps Console Docker Compose setup"
```

Push only after confirming that the intended remote and branch are correct:

```bash
git branch --show-current
git remote -v
```

Then push to the appropriate branch using your configured Git authentication.

---

## 12. Current Limitations and Future Improvements

The project supports two separate deployment approaches:

- **Docker Compose:** The recommended local setup for development and hackathon demonstrations.
- **Kubernetes with Minikube:** An advanced path for learning container orchestration and deployment.

Current limitations:

1. Kubernetes database connectivity depends on the MySQL address reachable from the cluster.
2. Compose and Kubernetes have separate configurations and storage; they do not automatically share database records or query history.
3. Windows access to the local Minikube Ingress may require port-forwarding and a hosts-file entry.
4. The prototype needs a thorough security review before production use.
5. A clean-clone test should be performed on a separate directory or machine before claiming complete reproducibility.

Potential future improvements include stronger authentication and authorization, configurable query policies, expanded audit logging, automated deployment pipelines, and additional read-only database connectors.

---

## 13. Final Checklist

Before demonstrating the project:

- [ ] `.env` contains valid local passwords and is not staged in Git.
- [ ] `docker compose config -q` succeeds.
- [ ] Docker Compose services are healthy.
- [ ] The dashboard opens at `http://localhost:8082`.
- [ ] `/health` returns a successful response.
- [ ] `/api/db-health` confirms database connectivity.
- [ ] A permitted `SELECT` query returns the expected rows.
- [ ] Backend tests pass.
- [ ] `git diff --check` reports no whitespace errors.
- [ ] No credentials or unintended generated files are included in the commit.

**End of guide.**
