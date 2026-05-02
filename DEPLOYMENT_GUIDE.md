# 🚀 Testing & Deployment Guide

## Phase 1: Local Testing

### Step 1.1: Setup Local Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your OpenAI key (optional, local embeddings work fine)
# nano .env
# Or keep it as-is to use free local embeddings
```

### Step 1.2: Run Tests

```bash
# Run all tests
uv run pytest tests/ -v

# Expected output: 13 passed ✅
```

### Step 1.3: Start the API Locally

```bash
# Terminal 1: Start the API server
uv run api

# Output should show:
# INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Step 1.4: Test in Browser

Open http://localhost:8000 in your browser and you should see:
- **AI Signal Control Room** dashboard
- Run Pipeline button (will require API key in next step)

### Step 1.5: Test API Endpoints

**Terminal 2: Run these commands**

```bash
# 1. Health check (no auth required)
curl http://localhost:8000/health
# Expected: {"status":"ok"}

# 2. Try to run pipeline without API key (should fail)
curl -X POST http://localhost:8000/run
# Expected: 401 Unauthorized - "Missing API key"

# 3. Try with wrong API key (should fail)
curl -X POST http://localhost:8000/run \
  -H "X-API-Key: wrong-key"
# Expected: 403 Forbidden - "Invalid API key"

# 4. Run pipeline with correct API key ✅
curl -X POST http://localhost:8000/run \
  -H "X-API-Key: dev-key-change-in-production"
# Expected: {"job_id":"...", "status":"queued", ...}

# 5. Check pipeline status
curl http://localhost:8000/status/{job_id}
# Replace {job_id} with actual ID from step 4

# 6. Get metrics
curl http://localhost:8000/metrics

# 7. Get RAG status
curl http://localhost:8000/rag/status

# 8. Rebuild RAG index
curl -X POST http://localhost:8000/rag/rebuild \
  -H "X-API-Key: dev-key-change-in-production"
```

---

## Phase 2: Docker Testing

### Step 2.1: Build Docker Image

```bash
# From repo root
docker build -f infra/docker/Dockerfile -t ai-signal-platform:latest .

# Expected: "Successfully tagged ai-signal-platform:latest"
```

### Step 2.2: Verify Image

```bash
docker images ai-signal-platform:latest

# Should show:
# REPOSITORY              TAG       IMAGE ID      SIZE
# ai-signal-platform     latest    ...           1.42GB
```

### Step 2.3: Run with Docker Compose

```bash
# Start the container
docker compose -f infra/docker/docker-compose.yml up

# Output should show:
# api | INFO:     Uvicorn running on http://0.0.0.0:8000
# api | health check at http://0.0.0.0:8000/health
```

### Step 2.4: Test Docker Deployment

In another terminal:

```bash
# Test health endpoint
curl http://localhost:8000/health

# Test API with auth
curl -X POST http://localhost:8000/run \
  -H "X-API-Key: dev-key-change-in-production"

# Check dashboard
# Open http://localhost:8000 in browser
```

### Step 2.5: Verify Data Persistence

```bash
# Check that data is on your host machine
ls -la data/
ls -la models/
ls -la logs/
ls -la deployed/

# These folders should have files created during pipeline runs
# They'll persist even if container stops
```

### Step 2.6: Stop Docker

```bash
# Stop containers
docker compose -f infra/docker/docker-compose.yml down

# Keep data: volumes persist
# Clean up: docker compose -f infra/docker/docker-compose.yml down -v
```

---

## Phase 3: Kubernetes Testing (Optional - Local)

### Step 3.1: Start Minikube or Kind

```bash
# Option A: Minikube
minikube start --cpus=4 --memory=4096 --driver=docker

# Option B: Kind
kind create cluster --name ai-signal

# Verify cluster is running
kubectl cluster-info
```

### Step 3.2: Load Docker Image

```bash
# Minikube
minikube image load ai-signal-platform:latest

# Kind
kind load docker-image ai-signal-platform:latest --name ai-signal

# Verify
kubectl get nodes  # Should show 1 node ready
```

### Step 3.3: Deploy to Kubernetes

```bash
# From repo root
kubectl apply -k infra/k8s/

# Verify deployment
kubectl get pods -n ai-signal
kubectl get svc -n ai-signal
kubectl get pvc -n ai-signal

# Wait for pod to be Running
kubectl wait --for=condition=ready pod -l app=ai-signal-api -n ai-signal --timeout=300s
```

### Step 3.4: Port Forward & Test

```bash
# Port forward to localhost
kubectl port-forward -n ai-signal svc/ai-signal-api 8000:80

# In another terminal, test it
curl http://localhost:8000/health

# Test API with auth
curl -X POST http://localhost:8000/run \
  -H "X-API-Key: dev-key-change-in-production"
```

### Step 3.5: Monitor Kubernetes

```bash
# Watch pods
kubectl get pods -n ai-signal -w

# Watch autoscaling
kubectl get hpa -n ai-signal -w

# View logs
kubectl logs -n ai-signal -l app=ai-signal-api -f

# Check deployed resources
kubectl get all -n ai-signal
```

### Step 3.6: Cleanup Kubernetes

```bash
# Delete everything
kubectl delete namespace ai-signal

# Or delete cluster
minikube delete
kind delete cluster --name ai-signal
```

---

## Phase 4: Production Deployment Checklist

Before deploying to production (AWS/GCP/Azure):

```
Security:
  ☐ Generate strong API_KEY (don't use default)
  ☐ Set OpenAI API key in secrets management
  ☐ Configure SSL/TLS certificates
  ☐ Set up network policies in K8s

Configuration:
  ☐ Set ENVIRONMENT=production
  ☐ Update image tag (not 'latest')
  ☐ Configure persistent storage (cloud provider)
  ☐ Set resource limits appropriately

Monitoring:
  ☐ Set up log aggregation (CloudWatch, Stackdriver, etc.)
  ☐ Set up alerting for pod failures
  ☐ Configure HPA thresholds
  ☐ Set up health check monitoring

Backup & Recovery:
  ☐ Configure PVC backups
  ☐ Document disaster recovery procedure
  ☐ Test recovery process
```

---

## Phase 5: Troubleshooting

### Local Testing Issues

```bash
# Port 8000 already in use
sudo lsof -i :8000
kill -9 <PID>

# API won't start
uv run api --reload  # Verbose mode
# Check logs for errors

# Tests failing
uv run pytest tests/ -v --tb=short  # More detailed errors
```

### Docker Issues

```bash
# Container won't start
docker compose -f infra/docker/docker-compose.yml logs api

# Data not persisting
docker volume ls
docker inspect <volume_name>

# Rebuild from scratch
docker compose -f infra/docker/docker-compose.yml down -v
docker build --no-cache -f infra/docker/Dockerfile -t ai-signal-platform:latest .
docker compose -f infra/docker/docker-compose.yml up
```

### Kubernetes Issues

```bash
# Pod not starting
kubectl describe pod -n ai-signal <pod-name>
kubectl logs -n ai-signal <pod-name>

# PVC not mounting
kubectl describe pvc -n ai-signal ai-signal-artifacts-pvc

# Image not found
kubectl logs -n ai-signal <pod-name>
# Ensure image is loaded: minikube image load / kind load

# HPA not working
kubectl get hpa -n ai-signal
kubectl describe hpa -n ai-signal ai-signal-api
```

---

## Success Criteria

Your deployment is successful when:

✅ Local API starts and responds to requests  
✅ All 13 tests pass  
✅ Docker image builds without errors  
✅ Docker container runs and persists data  
✅ Kubernetes deployment reaches "Ready" state (if using K8s)  
✅ API key authentication works  
✅ Dashboard loads at http://localhost:8000  
✅ Pipeline can be triggered and completes  

---

## Quick Reference

```bash
# Quick local test
uv run api &
sleep 3
curl -X POST http://localhost:8000/run -H "X-API-Key: dev-key-change-in-production"

# Quick Docker test  
docker compose -f infra/docker/docker-compose.yml up -d
sleep 5
curl http://localhost:8000/health
docker compose -f infra/docker/docker-compose.yml down

# Quick K8s test (requires minikube/kind)
kubectl apply -k infra/k8s/
kubectl wait --for=condition=ready pod -l app=ai-signal-api -n ai-signal --timeout=300s
kubectl port-forward -n ai-signal svc/ai-signal-api 8000:80 &
curl http://localhost:8000/health
kubectl delete namespace ai-signal
```
