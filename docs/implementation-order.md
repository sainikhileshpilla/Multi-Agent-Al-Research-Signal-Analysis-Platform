# Exact Implementation Order

## Phase 1: Stabilize Current Baseline (Day 1)
1. Keep current source_code runtime as the production baseline.
2. Ensure pyproject scripts run: source_code, run_crew, api.
3. Update README to match current scripts and API endpoints.
4. Add any missing dependencies used in code (example: pdfplumber if PDF ingestion is used).

Exit criteria:
- uv run source_code works.
- uv run api starts and dashboard loads.

## Phase 2: Organize by Domain (Day 2)
1. Create target folders under services and apps.
2. Copy modules into new folders in small chunks (do not delete originals yet).
3. Introduce import shims so old and new imports both work.
4. Run quick smoke test after each move.

Exit criteria:
- Project still runs from old entrypoints.
- New folder structure contains mirrored logic.

## Phase 3: RAG + Vector DB Upgrade (Day 3)
1. Choose one vector DB for beginner setup (Chroma local first).
2. Add embedding pipeline and vector index build step.
3. Make retrieval read from vector DB, with fallback to current method.
4. Expose endpoint to refresh/rebuild index.

Exit criteria:
- RAG retrieval returns context from vector DB.
- Works with and without OPENAI_API_KEY.

## Phase 4: MLOps Hardening (Day 4)
1. Version model artifacts with timestamp/model id.
2. Add dataset snapshot metadata to logs.
3. Add simple experiment tracking file or MLflow optional.
4. Expand drift report endpoint and retraining logs.

Exit criteria:
- Each training run creates traceable artifacts.
- Monitoring output is understandable from API.

## Phase 5: FastAPI Production Structure (Day 5)
1. Split API into routers: run, status, metrics, deployment, analysis.
2. Add pydantic request/response schemas.
3. Add API key auth for run endpoint.
4. Add health and readiness checks.

Exit criteria:
- Clean OpenAPI docs.
- Protected run trigger.

## Phase 6: Docker (Day 6)
1. Add Dockerfile for API service.
2. Add docker-compose for api + vector db.
3. Mount persistent volumes for data/models/logs/deployed.
4. Validate local container run.

Exit criteria:
- docker compose up works end-to-end.

## Phase 7: Kubernetes (Day 7)
1. Add k8s manifests: deployment, service, configmap, secret.
2. Add PVC for artifacts.
3. Add HPA for API service.
4. Add ingress example.

Exit criteria:
- App deploys on local k8s (kind/minikube) or managed cluster.

## Phase 8: Cloud Architecture (Day 8)
1. Document one cloud reference architecture (AWS or Azure).
2. Map each component: API, storage, vector DB, model artifacts, observability.
3. Add deployment checklist and cost-aware starter sizing.

Exit criteria:
- docs include architecture diagram and deployment steps.

## Phase 9: Portfolio Polish (Day 9)
1. Add architecture diagram and short demo GIF.
2. Add clear project story in README.
3. Add sample API calls and expected outputs.
4. Add interview-ready section: what you built and why.

Exit criteria:
- Repo is easy to understand in under 5 minutes.
- Recruiter can run it locally with 3 commands.
