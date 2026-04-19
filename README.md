# 🚀 AI Signal Research Platform

**A production-ready multi-agent AI system for financial signal analysis with real-world MLOps and Kubernetes deployment.**

> This is a full-stack portfolio project demonstrating **multi-agent AI orchestration, RAG with vector databases, MLOps lifecycle management, FastAPI, Docker, and Kubernetes** — everything a beginner needs to build and deploy intelligent systems at scale.

---

## 🎯 What It Does

The platform runs a **6-agent AI crew** that autonomously:

1. **📰 Fetches & Cleans** financial news from RSS feeds
2. **🔍 Analyzes** news with semantic search (RAG + ChromaDB)
3. **🤖 Trains** ML models to predict bullish/bearish signals
4. **📊 Makes Predictions** on news sentiment and market impact
5. **📈 Monitors** model performance and detects drift
6. **🚢 Deploys** models to production with versioning

All from **one API call**. Watch it happen in the browser dashboard.

---

## 🏗️ Architecture at a Glance

```
┌─────────────────────────────────────────────────────────────────┐
│                   FastAPI + Web Dashboard                       │
│              (POST /run → Stream pipeline status)               │
└────┬────────────────────────────────────────────────────────────┘
     │
┌────▼────────────────────────────────────────────────────────────┐
│              CrewAI Orchestration Layer (6 Agents)              │
│ ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐   │
│ │  Data Agent  │→ │Research Agent│→ │ ML + Prediction Agts │   │
│ │ (RSS Fetch)  │  │ (RAG + Query)│  │ (Train + Inference) │   │
│ └──────────────┘  └──────────────┘  └──────────────────────┘   │
│                                              ↓                  │
│                                   ┌─────────────────────┐       │
│                                   │ Monitoring Agent    │       │
│                                   │ (Drift Detection)   │       │
│                                   └─────────────────────┘       │
└────┬─────────────────────────────────────────────────────────────┘
     │
┌────┼──────────────────────────────────────────────────────────────┐
│    │           Data & ML Pipeline                                 │
│    └─→ CSV Reader ─→ Feature Engineer ─→ Model Trainer           │
│         │                                    ↓                    │
│         │                          ┌─────────────────┐            │
│         │                          │ Trained Model   │            │
│         │                          │ (signal_model)  │            │
│         │                          └────────┬────────┘            │
│         │                                   │                    │
│         └──────────────────────────────────→│                    │
│              ▲                               ▼                    │
│              │                    ┌─────────────────┐             │
│              └────────────────────│ Predictions &   │             │
│                                   │ Performance Log │             │
│                                   └─────────────────┘             │
└────┬──────────────────────────────────────────────────────────────┘
     │
┌────▼──────────────────────────────────────────────────────────────┐
│     ChromaDB Vector Database (Semantic Search for RAG)            │
│     • Embeddings: OpenAI or local all-MiniLM-L6-v2               │
│     • Queries: Find relevant news articles by meaning            │
│     • Storage: Persistent disk at data/vectorstore/              │
└────────────────────────────────────────────────────────────────────┘

Deployment: Docker Container → Kubernetes Cluster → Production
```

---

## ⚡ Quick Start (< 5 minutes)

### Local Development

**Prerequisites:** Python 3.10+, `uv`, Docker (optional)

```bash
# 1. Clone and install
git clone https://github.com/yourusername/Multi-Agent-AI-Research-Signal-Analysis-Platform.git
cd Multi-Agent-AI-Research-Signal-Analysis-Platform
uv sync

# 2. Run the pipeline
uv run source_code

# 3. Start the API + dashboard
uv run api
# Open: http://localhost:8000
```

### Docker (Recommended)

```bash
# Build the image
docker build -f infra/docker/Dockerfile -t ai-signal-platform .

# Run with compose
docker compose -f infra/docker/docker-compose.yml up

# Access: http://localhost:8000
```

### Kubernetes (Production)

```bash
# Deploy to minikube
minikube start
minikube image load ai-signal-platform:latest
kubectl apply -k infra/k8s/

# Access: http://localhost:8000 (after port-forward)
kubectl port-forward -n ai-signal svc/ai-signal-api 8000:80
```

---

## 🎨 Features & Technologies

### Multi-Agent AI
- **CrewAI** orchestration framework
- 6 specialized agents working in sequence
- Tool-based capabilities (news fetching, model training, monitoring)
- Verbose output for transparency

### Data & ML
- **RAG (Retrieval-Augmented Generation)** with semantic search
- **ChromaDB** vector database (persistent storage on disk)
- **OpenAI embeddings** (or free local all-MiniLM-L6-v2)
- **scikit-learn** models (LogisticRegression, SVM, RandomForest comparison)
- **Drift detection** — automatically flags when model accuracy drops >5%
- **Model versioning** — timestamped artifacts

### API & Frontend
- **FastAPI** with async support
- Interactive **web dashboard** (real-time job monitoring)
- Health checks & status endpoints
- RAG index rebuild trigger
- Job status polling with WebSocket support

### DevOps
- **Docker** with multi-stage builds (fast layer caching)
- **Docker Compose** for local development
- **Kubernetes manifests** for production
  - Deployments, Services, PersistentVolumeClaims
  - ConfigMap + Secret management
  - HorizontalPodAutoscaler (auto-scaling 2-5 replicas)
  - Health probes and resource limits

---

## 📊 API Examples

### Run the full pipeline

```bash
curl -X POST http://localhost:8000/run
```

**Response:**
```json
{
  "job_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "status": "queued",
  "message": "Crew pipeline started in the background."
}
```

### Check job status

```bash
curl http://localhost:8000/status/f47ac10b-58cc-4372-a567-0e02b2c3d479
```

**Response:**
```json
{
  "job_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "status": "completed",
  "started_at": "2026-04-20T12:34:56",
  "finished_at": "2026-04-20T12:45:23",
  "result": "Pipeline completed. 14 articles processed, bullish: 8, bearish: 6..."
}
```

### Get latest model metrics

```bash
curl http://localhost:8000/metrics
```

**Response:**
```json
{
  "timestamp": "2026-04-20T12:45:23",
  "metrics": {
    "best_model": "RandomForest",
    "accuracy": 0.8571,
    "precision": 0.8333,
    "recall": 0.8333,
    "f1_score": 0.8333
  }
}
```

### Rebuild the vector database

```bash
curl -X POST http://localhost:8000/rag/rebuild
```

**Response:**
```json
{
  "status": "built",
  "collection": "financial_news",
  "count": 14,
  "strategy": "chromadb:openai",
  "persist_dir": "/app/data/vectorstore"
}
```

---

## 🗂️ Project Structure

```
├── source_code/              # Core implementation (stable runtime)
│   ├── crew.py              # 6-agent orchestration + task definitions
│   ├── main.py              # CLI entrypoint
│   ├── api.py               # FastAPI app entrypoint
│   ├── runtime.py           # Environment loading + pipeline kickoff
│   ├── paths.py             # Centralized path management
│   ├── tools/               # CrewAI tools (news fetch, model training, etc.)
│   ├── pipelines/           # Data pipelines (ingestion, feature engineering)
│   ├── monitoring/          # MLOps monitoring (drift, retraining, logging)
│
├── services/                 # Refactored domain layers (migration in progress)
│   ├── data/                # Data ingestion + validation
│   ├── rag/                 # RAG layer (ChromaDB + retrieval)
│   ├── ml/                  # ML layer (training, inference, monitoring)
│
├── apps/                     # Application layer
│   ├── api/                 # FastAPI application with routes
│   └── dashboard/           # Frontend (HTML/JS dashboard)
│
├── infra/                    # Infrastructure as Code
│   ├── docker/              # Dockerfile + docker-compose.yml
│   └── k8s/                 # Kubernetes manifests (deployment, service, HPA, PVC)
│
├── data/                     # Data directory
│   ├── raw/                 # Input CSV/RSS data
│   ├── processed/           # Cleaned dataset
│   └── vectorstore/         # ChromaDB persistent storage
│
├── models/                   # ML artifacts
│   └── signal_model.pkl     # Trained model
│
├── logs/                     # Monitoring & metrics
│   └── model_performance.json
│
├── deployed/                 # Production deployment
│   └── deployment_manifest.json
│
├── docs/                     # Architecture & guides
│   ├── final-architecture.md
│   ├── implementation-order.md
│   └── cloud-architecture.md
│
└── pyproject.toml            # Dependencies (uv-managed)
```

---

## 🎓 What This Demonstrates (For Interviews)

### Multi-Agent AI
- **Understand agent design:** Each agent has a specific role, goal, and backstory
- **Orchestration complexity:** Sequential task dependencies, context passing, tool selection
- **Prompt engineering:** How to define agent behavior through goal/backstory

### RAG & Vector Databases
- **Why vector DBs matter:** Semantic search > keyword matching
- **ChromaDB in production:** Persistent storage, subPath organization in Kubernetes
- **Embedding strategies:** OpenAI vs. free local models trade-offs
- **Fallback patterns:** TF-IDF when primary unavailable (production resilience)

### MLOps
- **Full ML lifecycle:** Data ingestion → feature engineering → training → monitoring → retraining
- **Drift detection:** Comparing model accuracy across time
- **Model versioning:** Timestamped artifacts, deployment manifest
- **Experiment tracking:** Logging metrics to JSON (easily extensible to MLflow)

### FastAPI
- **Async patterns:** Background job execution with threading
- **Pydantic validation:** Request/response schemas
- **Dependency injection:** Clean separation of concerns
- **WebSocket-ready:** Dashboard polling pattern scales to real-time

### DevOps & Deployment
- **Docker best practices:** Multi-stage builds, layer caching, minimal base images
- **Kubernetes manifests:** Production patterns (Deployment, Service, HPA, PVC, ConfigMap, Secret)
- **High availability:** Pod anti-affinity, readiness/liveness probes, resource limits
- **Auto-scaling:** HPA based on metrics
- **Secret management:** Environment variables + Kubernetes Secrets

---

## 📈 Performance

| Metric | Result |
|--------|--------|
| **Model Accuracy** | 85.7% (RandomForest) |
| **Embedding Strategy** | OpenAI text-embedding-3-small or free local |
| **API Response Time** | <100ms (health), <5min (full pipeline) |
| **Docker Build Time** | ~2min (with cache: <10s) |
| **Container Size** | 1.42 GB (includes Python, dependencies, models) |
| **K8s Deployment Time** | <30s (rolling update) |

---

## 🚀 Deployment Options

| Environment | Command | Notes |
|---|---|---|
| **Local Dev** | `uv run api` | Fast iteration, single process |
| **Docker** | `docker compose up` | Reproducible, volume mounts for persistence |
| **Minikube** | `kubectl apply -k infra/k8s/` | Local K8s testing, full production patterns |
| **Production (GKE/EKS/AKS)** | Push image + update manifests | Auto-scaling, managed storage, CDN ready |

---

## 📚 Learning Path

**New to these topics?** Start here:

1. **Agent-Based AI:** Read `source_code/crew.py` — understand how agents define roles, goals, tasks
2. **RAG System:** Check `services/rag/rag.py` — see how ChromaDB queries and embeddings work
3. **FastAPI:** Look at `apps/api/app.py` — trace a request from client → dashboard update
4. **MLOps:** Review `source_code/monitoring/` — observe drift detection and metrics logging
5. **Docker:** Run `docker build -f infra/docker/Dockerfile -t test .` — understand layer caching
6. **Kubernetes:** Deploy locally `kubectl apply -k infra/k8s/` — see manifests in action

Detailed guides:
- `docs/final-architecture.md` — System design
- `docs/implementation-order.md` — Build sequence
- `infra/docker/docker-compose.yml` — Development setup
- `infra/k8s/README.md` — Kubernetes deployment

---

## 🔧 Configuration

### Environment Variables

```bash
# Optional: Use OpenAI embeddings (recommended for production)
export OPENAI_API_KEY="sk-..."
export OPENAI_EMBEDDING_MODEL="text-embedding-3-small"

# Without OPENAI_API_KEY, the system uses:
# • Local all-MiniLM-L6-v2 (free, ~80MB download)
# • TF-IDF fallback if ChromaDB unavailable
```

### Data Format

Place CSV files in `data/raw/` with columns:
- `headline` — article title
- `content` — article body
- `timestamp` — publication date
- `source` — news source name

---

## 🤝 Contributing

Want to extend this? Ideas:
- Add a new agent (e.g., sentiment analyzer, risk scorer)
- Integrate additional data sources (Alpha Vantage, finnhub)
- Add more ML models (XGBoost, LightGBM)
- Build advanced dashboards (Plotly, D3.js)
- Add Prometheus/Grafana monitoring
- Implement result caching with Redis

---

## 📦 Dependencies

**Core:**
- `crewai[tools]==1.9.3` — Multi-agent orchestration
- `fastapi>=0.115` — Web framework
- `chromadb>=1.0` — Vector database
- `scikit-learn>=1.3` — ML models
- `pandas>=2.0` — Data manipulation

**Full list:** See `pyproject.toml`

---

## 📝 License

MIT — Use freely in portfolio, production, or learning projects.

---

## 🎯 Next Steps

1. **Run locally:** `uv run api` → http://localhost:8000
2. **Trigger pipeline:** Click "Run Pipeline" or `curl -X POST http://localhost:8000/run`
3. **Explore dashboard:** Watch agents work in real-time
4. **Deploy to Docker:** `docker compose up`
5. **Deploy to Kubernetes:** `kubectl apply -k infra/k8s/`
6. **Read code:** Start with `source_code/crew.py`

---

**Built with ❤️ as a production-ready portfolio project for learning multi-agent AI, RAG, MLOps, and DevOps.**
