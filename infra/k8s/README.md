# Kubernetes Deployment Guide

Deploy the AI Signal platform to any Kubernetes cluster (local or cloud).

## Prerequisites

### Local Testing (Minikube or Kind)

**Minikube:**
```bash
minikube start --cpus=4 --memory=4096 --driver=docker
minikube image load ai-signal-platform:latest
```

**Kind:**
```bash
kind create cluster --name ai-signal
kind load docker-image ai-signal-platform:latest --name ai-signal
```

### Cloud Cluster (EKS, GKE, AKS)

1. Push the image to your registry:
   ```bash
   docker tag ai-signal-platform:latest gcr.io/my-project/ai-signal:v1.0
   docker push gcr.io/my-project/ai-signal:v1.0
   ```

2. Update `deployment.yaml`:
   - Change `image: ai-signal-platform:latest` to your registry URL
   - Change `imagePullPolicy: IfNotPresent` to `Always`

3. Configure persistent storage:
   - Update `pvc.yaml` with your cloud provider's storage class
   - Example for GKE: `storageClassName: "standard-rwo"`

4. Ensure metrics-server is installed (required by HPA):
   ```bash
   kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
   ```

## Deploy

### All at Once (Recommended)

```bash
kubectl apply -k infra/k8s/
```

### Individual Resources

If you prefer step-by-step deployment:

```bash
kubectl apply -f infra/k8s/namespace.yaml
kubectl apply -f infra/k8s/configmap.yaml
kubectl apply -f infra/k8s/secret.yaml
kubectl apply -f infra/k8s/pvc.yaml
kubectl apply -f infra/k8s/deployment.yaml
kubectl apply -f infra/k8s/service.yaml
kubectl apply -f infra/k8s/hpa.yaml
```

## Setup: Add Your OpenAI API Key

### Option 1: Update the Secret Manifest (Recommended for Version Control)

1. Encode your key:
   ```bash
   echo -n "sk-your-actual-key-here" | base64
   ```

2. Edit `secret.yaml` and replace the empty `OPENAI_API_KEY` value with the base64-encoded key

3. Re-deploy:
   ```bash
   kubectl apply -f infra/k8s/secret.yaml
   ```

### Option 2: Create Secret via kubectl (Better for Secrets Management)

```bash
kubectl create secret generic ai-signal-secrets \
  --from-literal=OPENAI_API_KEY=sk-your-actual-key \
  -n ai-signal --dry-run=client -o yaml | kubectl apply -f -
```

### Option 3: Skip It (Use Local Embeddings)

Leave `OPENAI_API_KEY` empty. The platform will use the built-in `all-MiniLM-L6-v2` model (free, local, first run downloads ~80MB).

## Check Deployment Status

```bash
# Watch rollout
kubectl rollout status -n ai-signal deployment/ai-signal-api

# See pods
kubectl get pods -n ai-signal

# See events (if something failed)
kubectl describe pod -n ai-signal <pod-name>

# View logs
kubectl logs -n ai-signal -l app=ai-signal-api -f
```

## Access the API

### Local (Minikube/Kind)

**Option A: Port Forward**
```bash
kubectl port-forward -n ai-signal svc/ai-signal-api 8000:80
# Open: http://localhost:8000
```

**Option B: NodePort (if service type is NodePort)**
```bash
kubectl get svc -n ai-signal
# Find the NodePort (e.g., 30000)
# Then: http://<node-ip>:30000
```

### Cloud Cluster

```bash
kubectl get svc -n ai-signal ai-signal-api
# Copy the EXTERNAL-IP and visit: http://<EXTERNAL-IP>
# (May take a minute to provision)
```

## Monitoring Deployment

### View Current Replicas

```bash
kubectl get deployment -n ai-signal ai-signal-api
```

### Watch Autoscaling

```bash
kubectl get hpa -n ai-signal -w
```

### Check PVC Usage

```bash
kubectl get pvc -n ai-signal
kubectl describe pvc -n ai-signal ai-signal-artifacts-pvc
```

## Run a Pipeline Job

Once the API is accessible, trigger a pipeline run:

```bash
curl -X POST http://localhost:8000/run
# Returns: { "job_id": "...", "status": "queued", ... }

# Check status
curl http://localhost:8000/status/<job_id>
```

Or open the dashboard at `http://localhost:8000`.

## Rebuild Vector Index Inside Cluster

```bash
curl -X POST http://localhost:8000/rag/rebuild
```

## Scaling

### Manual Scaling

```bash
kubectl scale deployment -n ai-signal ai-signal-api --replicas=5
```

### Autoscaling

HPA automatically scales between 2-5 replicas based on CPU usage. Check status:

```bash
kubectl get hpa -n ai-signal -o wide
```

## Troubleshooting

### Pods Not Starting

```bash
kubectl describe pod -n ai-signal <pod-name>
# Look for events and error messages
```

### Image Pull Errors

- **Local:** Ensure you loaded the image: `minikube image load ai-signal-platform:latest`
- **Cloud:** Ensure image is pushed to registry and image pull secret is configured

### PVC Not Mounting

```bash
kubectl describe pvc -n ai-signal ai-signal-artifacts-pvc
# Check that storage class exists and has available space
```

### Metrics Server Issues

HPA won't scale without metrics-server:

```bash
kubectl get deployment -n kube-system metrics-server
# If missing:
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
```

## Clean Up

```bash
# Delete everything in the namespace
kubectl delete namespace ai-signal

# Or individual resources
kubectl delete -k infra/k8s/
```

## Production Checklist

Before running in production:

- [ ] Push image to your registry with a version tag (not `latest`)
- [ ] Update `deployment.yaml` with the versioned image URL
- [ ] Set up proper secrets management (don't commit API keys)
- [ ] Configure storage class to match your cloud provider
- [ ] Set up persistent backups for the PVC
- [ ] Configure resource limits and requests based on your workload
- [ ] Add ingress for HTTPS and domain routing
- [ ] Set up monitoring and alerting (Prometheus, Grafana)
- [ ] Configure network policies for security
- [ ] Test disaster recovery (pod eviction, node failures)

## Next Steps

- Add **Ingress** for domain routing and HTTPS
- Add **Network Policies** for security
- Set up **Prometheus** for monitoring
- Configure **LogLevel** and **Structured Logging**
- Add **Pod Disruption Budgets** for safer deployments
