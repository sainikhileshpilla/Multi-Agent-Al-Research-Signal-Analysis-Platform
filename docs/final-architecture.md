# Final Architecture (Beginner Friendly)

## Goal
Build one portfolio project that clearly demonstrates:
- Multi-agent AI
- RAG + vector database
- MLOps lifecycle
- FastAPI backend
- Docker + Kubernetes deployment
- Cloud-ready architecture

## Architecture Layers
1. Data Layer
- Raw data intake from RSS and local files
- Validation and cleaning to processed dataset

2. Agent Orchestration Layer
- Crew of specialized agents (ingestion, research, training, prediction, monitoring, deployment)

3. RAG Layer
- Chunking + embeddings
- Vector database indexing and retrieval

4. ML Layer
- Feature engineering
- Model training and evaluation
- Drift detection and retraining trigger

5. Serving Layer
- FastAPI endpoints for run, status, metrics, deployment, analysis
- Dashboard for beginners to monitor all outputs

6. Platform Layer
- Docker for local reproducible runtime
- Kubernetes manifests for production-style deployment
- Cloud deployment blueprint

## Folder Layout (Target)
.
|-- apps/
|   |-- api/                # FastAPI app entry, routers, schemas
|   `-- dashboard/          # Optional frontend UI (or keep HTML in API first)
|-- services/
|   |-- agents/             # Crew and task orchestration
|   |-- data/               # Ingestion and validation
|   |-- rag/                # Embeddings, vector store, retrieval
|   `-- ml/                 # Training, inference, monitoring, retraining
|-- source_code/            # Current implementation (kept during migration)
|-- infra/
|   |-- docker/             # Dockerfile, compose files
|   |-- k8s/                # Deployments, services, configmaps, hpa
|   `-- cloud/              # Cloud diagrams and IaC notes
|-- docs/                   # Architecture, ADRs, setup guides
|-- scripts/                # Utility scripts
|-- tests/                  # Unit and integration tests
|-- data/
|-- models/
|-- logs/
`-- deployed/

## Mapping from Current Code
- source_code/crew.py -> services/agents/
- source_code/tools/* -> services/* (data/rag/ml split)
- source_code/pipelines/* -> services/data, services/rag, services/ml
- source_code/api.py -> apps/api/
- source_code/main.py -> apps/api or scripts/cli entry

Keep source_code as the stable runtime until migration is complete.
