# Kubernetes App Orchestration

A production-style Kubernetes project demonstrating the deployment and orchestration of a containerized Flask application. This project showcases core Kubernetes concepts such as Deployments, Services, ConfigMaps, Secrets, Health Probes, Self-Healing, and Scaling using Minikube.

---

## Project Overview

This project demonstrates how a real-world web application can be containerized using Docker and orchestrated using Kubernetes.

The sample application is a **Flask-based URL Shortener** with analytics, custom aliases, and click tracking, deployed on a Kubernetes cluster.

---

## Features

* URL Shortening
* Custom URL Aliases
* Click Analytics
* Browser & Platform Detection
* SQLite Database
* Dockerized Application
* Kubernetes Deployment
* NodePort Service
* ConfigMap for Configuration Management
* Secret for Sensitive Data
* Liveness & Readiness Probes
* Rolling Updates
* Self-Healing
* Horizontal Scaling

---

## Tech Stack

| Category           | Technology     |
| ------------------ | -------------- |
| Backend            | Flask (Python) |
| Database           | SQLite         |
| Containerization   | Docker         |
| Container Registry | Docker Hub     |
| Orchestration      | Kubernetes     |
| Local Cluster      | Minikube       |
| CLI                | kubectl        |

---

## Project Structure

```text
kubernetes-app-orchestration/
│
├── app.py
├── Dockerfile
├── requirements.txt
├── schema.sql
├── .gitignore
├── .dockerignore
│
├── static/
├── templates/
│
└── k8s/
    ├── deployment.yaml
    ├── service.yaml
    ├── configmap.yaml
    └── secret.yaml
```

---

## Kubernetes Architecture

```text
                    Browser
                        │
                        ▼
                NodePort Service
                        │
                        ▼
                  Deployment
                        │
               ReplicaSet
                        │
          ┌─────────────┴─────────────┐
          ▼                           ▼
      Flask Pod                   Flask Pod
          │                           │
          └─────────────┬─────────────┘
                        │
                ConfigMap + Secret
                        │
                        ▼
                 Flask Application
                        │
                        ▼
                  SQLite Database
```

---

## Kubernetes Resources Used

### Deployment

* Manages application Pods
* Supports rolling updates
* Enables self-healing
* Controls replica count

### Service

* Exposes the application using NodePort
* Provides a stable network endpoint
* Load balances traffic between Pods

### ConfigMap

Stores application configuration such as:

* Database path
* Short URL length

### Secret

Stores sensitive information such as:

* Flask Secret Key

### Health Probes

**Liveness Probe**

* Detects unhealthy containers
* Automatically restarts failed Pods

**Readiness Probe**

* Ensures traffic is only routed to healthy Pods

---

## Kubernetes Concepts Demonstrated

* Pods
* Deployments
* ReplicaSets
* Services
* Labels & Selectors
* ConfigMaps
* Secrets
* Environment Variables
* NodePort
* Health Checks
* Rolling Updates
* Self-Healing
* Scaling

---

## Docker

Build the image

```bash
docker build -t raheemd/myapp:v3 .
```

Run locally

```bash
docker run -p 5000:5000 raheemd/myapp:v3
```

Push to Docker Hub

```bash
docker push raheemd/myapp:v3
```

---

## Deploy to Kubernetes

Apply Kubernetes manifests

```bash
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secret.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
```

Verify deployment

```bash
kubectl get pods
kubectl get deployments
kubectl get services
```

Access the application

```bash
minikube service url-shortener-service
```

---

## Demonstrated Kubernetes Operations

### Scaling

```bash
kubectl scale deployment url-shortener --replicas=5
```

### Self-Healing

```bash
kubectl delete pod <pod-name>
```

### Logs

```bash
kubectl logs <pod-name>
```

### Execute inside Pod

```bash
kubectl exec -it <pod-name> -- sh
```

### Deployment Details

```bash
kubectl describe deployment url-shortener
```

---

## Learning Outcomes

Through this project, I gained hands-on experience with:

* Containerizing applications using Docker
* Deploying workloads on Kubernetes
* Managing Deployments and Services
* Configuring applications using ConfigMaps
* Securing sensitive data using Secrets
* Implementing Health Probes
* Performing Rolling Updates
* Scaling applications
* Understanding Kubernetes Self-Healing capabilities

---

## Future Improvements

* Replace SQLite with PostgreSQL
* Persistent Volumes (PV)
* Persistent Volume Claims (PVC)
* Ingress Controller
* Helm Charts
* CI/CD Pipeline using GitHub Actions or Jenkins
* Monitoring with Prometheus & Grafana

---

## Author

**Abdul Raheem**

If you found this project useful, feel free to ⭐ the repository.
