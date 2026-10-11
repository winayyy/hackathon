# DataOps Console — Setup and Command Guide

This guide explains how to clone and run the current DataOps Console proof of concept.

- Repository: https://github.com/winayyy/hackathon
- Frontend: React + Vite, served by NGINX in the Kubernetes deployment
- Backend: FastAPI
- Database: MySQL 8.4
- Local Kubernetes: Minikube
- Kubernetes manifests: `k8s/base` and `k8s/overlays/dev`

> **Important:** This is a local hackathon proof of concept, not a production-ready database administration tool. Use synthetic data only. The current Kubernetes setup uses a separately running MySQL Docker container, and its IP must match `MYSQL_HOST` in the ConfigMap. Do not commit real passwords or `.env` files.

## 1. Expected setup time

| Situation | Approximate time |
|---|---:|
| Docker, WSL, kubectl, and Minikube already installed | 30–60 minutes |
| First-time setup, including installing tools and learning the steps | 1–2 hours or more |
| Troubleshooting Docker networking or Kubernetes image loading | Additional time may be needed |

These are estimates, not guarantees. First-time Kubernetes setup depends on the computer, internet speed, and whether virtualization/WSL is already configured.

## 2. Prerequisites

For the Kubernetes path in this guide, install/configure:

- Git
- Docker Desktop with WSL 2 integration (for Windows + WSL) or a working Docker Engine
- Minikube
- `kubectl`
- A terminal that can run Bash commands (WSL Ubuntu is used in the examples)

Verify the tools:

```bash
git --version
docker --version
kubectl version --client
minikube version
```

Docker must be running before you continue.

## 3. Clone the repository

```bash
git clone https://github.com/winayyy/hackathon.git
cd hackathon
```

Confirm that the Kubernetes files are present:

```bash
find k8s -maxdepth 3 -type f -print | sort
```

## 4. Start Minikube

If you already have a working Minikube cluster, **do not delete it**. Check it first:

```bash
minikube status
kubectl get nodes
```

If this is a fresh setup, start a local cluster:

```bash
minikube start --driver=docker --nodes=1 --cpus=2 --memory=2500mb
minikube addons enable ingress
kubectl get nodes
kubectl get pods -n ingress-nginx
```

Wait for the ingress controller Pod to become `Running` and ready before continuing.

## 5. Create the MySQL database

The current repository does not include a fully automated database initialization container/Compose workflow. For this proof of concept, create a MySQL 8.4 container and initialize it manually.

### 5.1 Start MySQL

Choose a strong local root password. Do not reuse a real account password.

```bash
read -rsp "Choose a local MySQL root password: " MYSQL_ROOT_PASSWORD
echo

docker volume create dataops-mysql-data

docker run -d \
  --name dataops-mysql \
  --restart unless-stopped \
  -e MYSQL_ROOT_PASSWORD="$MYSQL_ROOT_PASSWORD" \
  -p 127.0.0.1:3306:3306 \
  -v dataops-mysql-data:/var/lib/mysql \
  mysql:8.4

unset MYSQL_ROOT_PASSWORD
```

Wait for MySQL to initialize:

```bash
docker logs dataops-mysql
```

Continue when the log indicates that MySQL is ready for connections. If a container named `dataops-mysql` or the port is already in use, inspect the existing setup instead of deleting it.

### 5.2 Create a demo database, table, and read-only user

Connect to MySQL:

```bash
docker exec -it dataops-mysql mysql -u root -p
```

Enter the root password you selected in Step 5.1. At the MySQL prompt, run the following SQL. Replace `REPLACE_WITH_A_LONG_RANDOM_PASSWORD` with a strong password for the read-only user.

```sql
CREATE DATABASE IF NOT EXISTS dataops_demo;

CREATE TABLE IF NOT EXISTS dataops_demo.customers (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    city VARCHAR(100) NOT NULL,
    status VARCHAR(30) NOT NULL,
    email VARCHAR(255),
    phone VARCHAR(40)
);

INSERT INTO dataops_demo.customers (name, city, status, email, phone)
SELECT 'Aarav Sharma', 'Bengaluru', 'active', 'aarav@example.test', '9000000001'
WHERE NOT EXISTS (SELECT 1 FROM dataops_demo.customers WHERE id = 1);

INSERT INTO dataops_demo.customers (name, city, status, email, phone)
SELECT 'Diya Rao', 'Hyderabad', 'active', 'diya@example.test', '9000000002'
WHERE NOT EXISTS (SELECT 1 FROM dataops_demo.customers WHERE id = 2);

INSERT INTO dataops_demo.customers (name, city, status, email, phone)
SELECT 'Kabir Reddy', 'Chennai', 'inactive', 'kabir@example.test', '9000000003'
WHERE NOT EXISTS (SELECT 1 FROM dataops_demo.customers WHERE id = 3);

CREATE USER IF NOT EXISTS 'dataops_reader'@'%'
  IDENTIFIED BY 'REPLACE_WITH_A_LONG_RANDOM_PASSWORD';

GRANT SELECT ON dataops_demo.* TO 'dataops_reader'@'%';

SHOW GRANTS FOR 'dataops_reader'@'%';
SELECT id, name, city, status FROM dataops_demo.customers;
EXIT;
```

Use synthetic demo data only. The SQL above creates a read-only account for the application; do not give it administrative privileges.

## 6. Connect MySQL to the Minikube Docker network

The backend Pod must be able to reach the MySQL container. The current manifests use `MYSQL_HOST=192.168.49.10` as an example address, so make sure the container actually has that address on the Docker network named `minikube`.

Inspect the network and container first:

```bash
docker network inspect minikube
docker inspect dataops-mysql
```

If the `minikube` Docker network exists and `192.168.49.10` is unused on that network, connect the MySQL container:

```bash
docker network connect --ip 192.168.49.10 minikube dataops-mysql
```

If Docker reports that the container is already connected, do not connect it again. If the address is already in use or the network uses a different subnet, choose a free address within the actual network subnet and use that same address in the next step.

Verify connectivity from the Minikube node:

```bash
minikube ssh -- "nc -vz -w 3 192.168.49.10 3306"
```

If you selected a different IP, replace `192.168.49.10` in the command.

## 7. Configure the Kubernetes manifests

### 7.1 Set the MySQL host

Open:

```text
k8s/base/backend-configmap.yaml
```

Set `MYSQL_HOST` to the IP assigned to `dataops-mysql` on the `minikube` Docker network. Also check that these values match the database/user created above:

```yaml
MYSQL_HOST: "192.168.49.10"
MYSQL_PORT: "3306"
MYSQL_DATABASE: "dataops_demo"
MYSQL_USER: "dataops_reader"
HISTORY_DB_PATH: "/app/data/query_history.db"
```

The IP above is an example used by the current development setup. It may differ on another computer.

### 7.2 Create the Kubernetes Secret

Create the namespace first:

```bash
kubectl apply -f k8s/base/namespace.yaml
```

Create a Secret without putting the password in the command text or committing it to Git:

```bash
read -rsp "Enter the MySQL dataops_reader password: " MYSQL_PASSWORD
echo

kubectl create secret generic dataops-backend-secret \
  -n dataops-console \
  --from-literal=MYSQL_PASSWORD="$MYSQL_PASSWORD" \
  --dry-run=client -o yaml | kubectl apply -f -

unset MYSQL_PASSWORD
```

Use the same password configured for `dataops_reader` in MySQL. Never commit a Secret YAML containing a real password.

## 8. Build and load the application images

The current Kubernetes Deployments use local images with `imagePullPolicy: Never`. Build the images and load them into Minikube.

From the repository root:

```bash
docker build -t dataops-backend:1.0 ./backend
docker build -t dataops-frontend:1.0 ./frontend

minikube image load dataops-backend:1.0
minikube image load dataops-frontend:1.0
```

Verify the images were loaded:

```bash
minikube image ls | grep dataops
```

If you change application code later, rebuild the relevant image and load it into Minikube again before restarting its Deployment.

## 9. Deploy the application

First, render the manifests to validate the Kustomize configuration:

```bash
kubectl kustomize k8s/overlays/dev
```

Apply the resources:

```bash
kubectl apply -k k8s/overlays/dev
```

Wait for the Deployments:

```bash
kubectl rollout status deployment/dataops-backend -n dataops-console --timeout=120s
kubectl rollout status deployment/dataops-frontend -n dataops-console --timeout=120s
```

Inspect the resources:

```bash
kubectl get deployments,pods,services -n dataops-console
kubectl get configmap,secret,pvc,serviceaccount,ingress -n dataops-console
kubectl get pods -n ingress-nginx
```

Pods should become `Running` and ready. If they do not:

```bash
kubectl describe pods -n dataops-console
kubectl logs deployment/dataops-backend -n dataops-console
kubectl logs deployment/dataops-frontend -n dataops-console
```

Do not paste passwords or secret values into issue reports or chat logs.

## 10. Verify the application through Ingress

Get the Minikube IP and test the frontend:

```bash
MINIKUBE_IP=$(minikube ip)

curl -i --max-time 10 \
  -H "Host: dataops.local" \
  "http://$MINIKUBE_IP/"
```

Test the database health endpoint through the same route:

```bash
curl -i --max-time 10 \
  -H "Host: dataops.local" \
  "http://$MINIKUBE_IP/api/db-health"
```

Expected responses:

- Frontend: `HTTP 200 OK` with HTML.
- Database health: `HTTP 200 OK` with JSON showing `"status":"connected"` and `"database":"dataops_demo"`.

If database health fails, check the MySQL host in the ConfigMap, Docker network connectivity, the Secret password, and the MySQL user's grants.

## 11. Open the application in a Windows browser

Because Minikube is running with the Docker driver inside WSL, Windows may not be able to reach the Minikube IP directly. Use a port-forward.

In a WSL terminal, run and keep this process open:

```bash
kubectl port-forward -n ingress-nginx \
  svc/ingress-nginx-controller 8081:80
```

If port `8081` is already in use, use another free local port, for example `8082`, and use that port in the URL below.

On Windows, open the hosts file with an editor running as Administrator:

```text
C:\Windows\System32\drivers\etc\hosts
```

Add this line if it is not already present:

```text
127.0.0.1 dataops.local
```

Save the file. Then open:

```text
http://dataops.local:8081
```

The port-forward terminal must remain running while you use the application through this URL.

## 12. Useful troubleshooting commands

```bash
# Current cluster and nodes
minikube status
kubectl get nodes

# App resources
kubectl get all -n dataops-console

# Ingress
kubectl get ingress -n dataops-console
kubectl describe ingress dataops-ingress -n dataops-console

# Backend logs and health
kubectl logs deployment/dataops-backend -n dataops-console
kubectl port-forward -n dataops-console svc/dataops-backend 8000:8000

# Frontend logs
kubectl logs deployment/dataops-frontend -n dataops-console

# MySQL container and Docker networks
docker ps
docker network inspect minikube
docker logs dataops-mysql
```

When testing the backend port-forward, open a second terminal and use:

```bash
curl -i http://127.0.0.1:8000/health
curl -i http://127.0.0.1:8000/api/db-health
```

Stop a port-forward with `Ctrl+C` in the terminal where it is running.

## 13. Important limitations and recommended improvements

The current repository is a proof of concept and is **not yet a one-command, fully reproducible setup**:

1. MySQL initialization is manual; an SQL initialization script should be added to the repository.
2. The Kubernetes ConfigMap currently has a machine-specific MySQL IP example. A configurable, stable setup would be better.
3. The frontend browser access in this local WSL setup depends on a running port-forward and a Windows hosts-file entry.
4. The local development frontend and API need a documented proxy configuration if users want to run Vite and FastAPI directly rather than through the Kubernetes/Nginx setup.
5. The app's SQL validation and masking are useful safeguards but are not a substitute for a security review.

### Recommended next improvement

Add a `docker-compose.yml` and a `db/init.sql` file so a new user can start MySQL, backend, and frontend with one documented command. Keep the Kubernetes workflow as a separate learning/deployment path. This would make the project significantly easier to evaluate during a hackathon.

## 14. Security reminder

- Use synthetic data only.
- Use a dedicated database account with `SELECT` privileges only.
- Keep `.env` and real passwords out of Git.
- Do not expose MySQL publicly.
- Do not treat this prototype as production-ready without a security review.
