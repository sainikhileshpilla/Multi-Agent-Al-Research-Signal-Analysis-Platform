import json
import os
import threading
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from source_code.paths import DEPLOYMENT_MANIFEST_PATH, PERFORMANCE_LOG_PATH, PROCESSED_NEWS_PATH
from source_code.runtime import run_crew_pipeline


# ─────────────────────────────────────────────────────────────────────────────
# Authentication & Rate Limiting
# ─────────────────────────────────────────────────────────────────────────────

# Get API key from environment or use default (for local development)
VALID_API_KEY = os.environ.get("API_KEY", "dev-key-change-in-production")


def verify_api_key(x_api_key: str = Header(None)) -> str:
    """
    Verify API key from request header.

    In production, set API_KEY env var before deploying.
    For local development, use X-API-Key: dev-key-change-in-production
    """
    if not x_api_key:
        raise HTTPException(status_code=401, detail="Missing API key. Use header: X-API-Key")

    if x_api_key != VALID_API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")

    return x_api_key


# ─────────────────────────────────────────────────────────────────────────────
# FastAPI Application
# ─────────────────────────────────────────────────────────────────────────────

app = FastAPI(title="AI Signal Research API", version="0.1.0")


DASHBOARD_HTML = """
<!doctype html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>AI Signal Control Room</title>
    <style>
        :root {
            --bg: #f4f6ef;
            --bg-panel: #ffffff;
            --ink: #1f2a37;
            --ink-soft: #4a5565;
            --line: #d6decc;
            --accent: #0e7a67;
            --accent-2: #d97b2d;
            --ok: #147d4e;
            --warn: #9a6700;
            --bad: #b42318;
            --radius: 14px;
            --shadow: 0 12px 28px rgba(40, 60, 30, 0.08);
        }

        * {
            box-sizing: border-box;
        }

        body {
            margin: 0;
            font-family: "IBM Plex Sans", "Segoe UI", sans-serif;
            color: var(--ink);
            background:
                radial-gradient(circle at 8% 10%, rgba(14, 122, 103, 0.16), transparent 30%),
                radial-gradient(circle at 90% 0%, rgba(217, 123, 45, 0.2), transparent 34%),
                linear-gradient(160deg, #eef3e4 0%, #f7f3e8 52%, #f4f6ef 100%);
            min-height: 100vh;
        }

        .shell {
            max-width: 1080px;
            margin: 0 auto;
            padding: 28px 18px 36px;
        }

        .hero {
            border: 1px solid var(--line);
            border-radius: var(--radius);
            background: linear-gradient(120deg, rgba(14, 122, 103, 0.95), rgba(14, 122, 103, 0.78));
            color: #f8fffb;
            padding: 22px;
            box-shadow: var(--shadow);
            animation: rise 450ms ease-out;
        }

        .hero h1 {
            margin: 0;
            font-family: "IBM Plex Serif", Georgia, serif;
            letter-spacing: 0.4px;
            font-size: clamp(1.4rem, 4vw, 2rem);
        }

        .hero p {
            margin: 8px 0 0;
            opacity: 0.9;
            max-width: 70ch;
        }

        .grid {
            margin-top: 16px;
            display: grid;
            grid-template-columns: repeat(12, 1fr);
            gap: 14px;
        }

        .card {
            border: 1px solid var(--line);
            border-radius: var(--radius);
            background: var(--bg-panel);
            box-shadow: var(--shadow);
            padding: 16px;
            animation: rise 520ms ease-out;
        }

        .card h2 {
            margin: 0 0 10px;
            font-size: 1rem;
            color: var(--ink-soft);
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.08em;
        }

        .control {
            grid-column: span 12;
        }

        .metrics,
        .deployment,
        .analysis {
            grid-column: span 6;
        }

        .status-dot {
            display: inline-flex;
            width: 10px;
            height: 10px;
            border-radius: 999px;
            margin-right: 6px;
            background: var(--warn);
            vertical-align: middle;
        }

        .status-dot.running { background: var(--accent-2); }
        .status-dot.completed { background: var(--ok); }
        .status-dot.failed { background: var(--bad); }

        .toolbar {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
            align-items: center;
            margin-bottom: 10px;
        }

        button {
            border: 0;
            border-radius: 11px;
            padding: 10px 16px;
            font-weight: 700;
            cursor: pointer;
            background: linear-gradient(145deg, var(--accent), #0a5f50);
            color: white;
            transition: transform 140ms ease, box-shadow 140ms ease, opacity 140ms ease;
            box-shadow: 0 6px 16px rgba(11, 82, 69, 0.28);
        }

        button.secondary {
            background: #edf3e7;
            color: #1f3a2f;
            border: 1px solid var(--line);
            box-shadow: none;
        }

        button:hover { transform: translateY(-1px); }
        button:disabled { opacity: 0.65; cursor: not-allowed; }

        .mono {
            font-family: "IBM Plex Mono", "SFMono-Regular", monospace;
            font-size: 0.92rem;
            white-space: pre-wrap;
            background: #f7faf4;
            border: 1px solid #e3ecd8;
            border-radius: 10px;
            padding: 10px;
            max-height: 300px;
            overflow: auto;
        }

        dl {
            margin: 0;
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 8px 10px;
        }

        dt {
            color: var(--ink-soft);
            font-weight: 600;
        }

        dd {
            margin: 0;
            text-align: right;
            font-weight: 700;
        }

        .subtle {
            color: var(--ink-soft);
            font-size: 0.92rem;
        }

        @media (max-width: 860px) {
            .metrics,
            .deployment,
            .analysis {
                grid-column: span 12;
            }
        }

        @keyframes rise {
            from {
                opacity: 0;
                transform: translateY(10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
    </style>
</head>
<body>
    <main class="shell">
        <section class="hero">
            <h1>AI Signal Control Room</h1>
            <p>Run the crew pipeline, track active jobs, and review model/deployment outcomes from one place.</p>
        </section>

        <section class="grid">
            <article class="card control">
                <h2>Pipeline Control</h2>
                <div class="toolbar">
                    <button id="runBtn">Run Pipeline</button>
                    <button id="refreshBtn" class="secondary">Refresh Data</button>
                    <span id="statusPill" class="subtle"><span class="status-dot"></span>Idle</span>
                </div>
                <p class="subtle" id="jobMeta">No active job.</p>
                <div id="runOutput" class="mono">Run output will appear here.</div>
            </article>

            <article class="card metrics">
                <h2>Latest Metrics</h2>
                <p class="subtle" id="metricsTime">No metrics loaded.</p>
                <dl>
                    <dt>Best Model</dt><dd id="bestModel">-</dd>
                    <dt>Accuracy</dt><dd id="acc">-</dd>
                    <dt>Precision</dt><dd id="prec">-</dd>
                    <dt>Recall</dt><dd id="rec">-</dd>
                    <dt>F1 Score</dt><dd id="f1">-</dd>
                </dl>
            </article>

            <article class="card deployment">
                <h2>Deployment</h2>
                <p class="subtle" id="deployStatus">No deployment data loaded.</p>
                <div id="deployMeta" class="mono">Waiting for deployment info...</div>
            </article>

            <article class="card analysis">
                <h2>Latest Analysis Snapshot</h2>
                <div id="analysisData" class="mono">Loading analysis...</div>
            </article>
        </section>
    </main>

    <script>
        const runBtn = document.getElementById("runBtn");
        const refreshBtn = document.getElementById("refreshBtn");
        const statusPill = document.getElementById("statusPill");
        const jobMeta = document.getElementById("jobMeta");
        const runOutput = document.getElementById("runOutput");

        let activeJobId = null;
        let pollTimer = null;

        function setStatus(status, label) {
            const dotClass = ["running", "completed", "failed"].includes(status) ? status : "";
            statusPill.innerHTML = `<span class="status-dot ${dotClass}"></span>${label}`;
        }

        function formatNumber(value) {
            if (typeof value !== "number") {
                return "-";
            }
            return value.toFixed(4);
        }

        async function fetchJson(url, options) {
            const response = await fetch(url, options || {});
            if (!response.ok) {
                const detail = await response.text();
                throw new Error(`${response.status} ${response.statusText}: ${detail}`);
            }
            return response.json();
        }

        async function loadMetrics() {
            try {
                const payload = await fetchJson("/metrics");
                const metrics = payload.metrics || {};
                document.getElementById("metricsTime").textContent = payload.timestamp
                    ? `Updated: ${payload.timestamp}`
                    : "No timestamp found.";
                document.getElementById("bestModel").textContent = metrics.best_model || "-";
                document.getElementById("acc").textContent = formatNumber(metrics.accuracy);
                document.getElementById("prec").textContent = formatNumber(metrics.precision);
                document.getElementById("rec").textContent = formatNumber(metrics.recall);
                document.getElementById("f1").textContent = formatNumber(metrics.f1_score);
            } catch (error) {
                document.getElementById("metricsTime").textContent = `Metrics unavailable: ${error.message}`;
            }
        }

        async function loadDeployment() {
            const deployStatus = document.getElementById("deployStatus");
            const deployMeta = document.getElementById("deployMeta");
            try {
                const payload = await fetchJson("/deployment");
                deployStatus.textContent = `Status: ${payload.status || "unknown"}`;
                deployMeta.textContent = JSON.stringify(payload, null, 2);
            } catch (error) {
                deployStatus.textContent = `Deployment unavailable: ${error.message}`;
                deployMeta.textContent = "No deployment manifest available yet.";
            }
        }

        async function loadAnalysis() {
            try {
                const payload = await fetchJson("/analysis");
                document.getElementById("analysisData").textContent = JSON.stringify(payload, null, 2);
            } catch (error) {
                document.getElementById("analysisData").textContent = `Analysis unavailable: ${error.message}`;
            }
        }

        async function refreshAll() {
            await Promise.all([loadMetrics(), loadDeployment(), loadAnalysis()]);
        }

        async function pollStatus() {
            if (!activeJobId) {
                return;
            }

            try {
                const status = await fetchJson(`/status/${activeJobId}`);
                jobMeta.textContent = `Job: ${status.job_id} | Started: ${status.started_at}`;

                if (status.status === "running" || status.status === "queued") {
                    setStatus("running", "Running");
                    return;
                }

                if (status.status === "completed") {
                    clearInterval(pollTimer);
                    pollTimer = null;
                    runBtn.disabled = false;
                    setStatus("completed", "Completed");
                    runOutput.textContent = status.result || "Run completed with no output.";
                    await refreshAll();
                    return;
                }

                clearInterval(pollTimer);
                pollTimer = null;
                runBtn.disabled = false;
                setStatus("failed", "Failed");
                runOutput.textContent = status.error || "Run failed with no error details.";
            } catch (error) {
                clearInterval(pollTimer);
                pollTimer = null;
                runBtn.disabled = false;
                setStatus("failed", "Error");
                runOutput.textContent = `Status polling error: ${error.message}`;
            }
        }

        runBtn.addEventListener("click", async () => {
            runBtn.disabled = true;
            runOutput.textContent = "Starting pipeline...";
            setStatus("running", "Queueing");
            jobMeta.textContent = "Creating job...";

            try {
                const payload = await fetchJson("/run", { method: "POST" });
                activeJobId = payload.job_id;
                jobMeta.textContent = `Job: ${activeJobId}`;
                runOutput.textContent = payload.message;
                setStatus("running", "Running");

                if (pollTimer) {
                    clearInterval(pollTimer);
                }
                pollTimer = setInterval(pollStatus, 2500);
                await pollStatus();
            } catch (error) {
                runBtn.disabled = false;
                setStatus("failed", "Error");
                runOutput.textContent = `Failed to start pipeline: ${error.message}`;
            }
        });

        refreshBtn.addEventListener("click", refreshAll);

        refreshAll();
    </script>
</body>
</html>
"""


class RunResponse(BaseModel):
    job_id: str
    status: str
    message: str


class JobStatusResponse(BaseModel):
    job_id: str
    status: str
    started_at: str
    finished_at: str | None = None
    result: str | None = None
    error: str | None = None


_jobs: dict[str, dict[str, Any]] = {}
_jobs_lock = threading.Lock()


def _read_latest_json_line(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    latest_line = None
    with path.open() as handle:
        for line in handle:
            line = line.strip()
            if line:
                latest_line = line

    if latest_line is None:
        raise ValueError(f"No data found in {path}")

    return json.loads(latest_line)


def _execute_job(job_id: str) -> None:
    with _jobs_lock:
        _jobs[job_id]["status"] = "running"

    try:
        result = run_crew_pipeline()
        with _jobs_lock:
            _jobs[job_id]["status"] = "completed"
            _jobs[job_id]["finished_at"] = datetime.utcnow().isoformat()
            _jobs[job_id]["result"] = str(result)
    except Exception as exc:
        with _jobs_lock:
            _jobs[job_id]["status"] = "failed"
            _jobs[job_id]["finished_at"] = datetime.utcnow().isoformat()
            _jobs[job_id]["error"] = str(exc)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/", response_class=HTMLResponse)
def dashboard() -> HTMLResponse:
    return HTMLResponse(content=DASHBOARD_HTML)


@app.post("/run", response_model=RunResponse)
def run_pipeline(api_key: str = Depends(verify_api_key)) -> RunResponse:
    """
    Start the crew pipeline in the background.

    **Authentication:** Required. Pass your API key in the `X-API-Key` header.

    Example:
    ```
    curl -X POST http://localhost:8000/run \\
      -H "X-API-Key: your-api-key"
    ```

    Returns a job ID for polling status.
    """
    job_id = str(uuid.uuid4())
    job_state = {
        "job_id": job_id,
        "status": "queued",
        "started_at": datetime.utcnow().isoformat(),
        "finished_at": None,
        "result": None,
        "error": None,
    }

    with _jobs_lock:
        _jobs[job_id] = job_state

    worker = threading.Thread(target=_execute_job, args=(job_id,), daemon=True)
    worker.start()

    return RunResponse(
        job_id=job_id,
        status="queued",
        message="Crew pipeline started in the background.",
    )


@app.get("/status/{job_id}", response_model=JobStatusResponse)
def get_status(job_id: str) -> JobStatusResponse:
    with _jobs_lock:
        job = _jobs.get(job_id)

    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")

    return JobStatusResponse(**job)


@app.get("/metrics")
def get_metrics() -> dict[str, Any]:
    latest = _read_latest_json_line(PERFORMANCE_LOG_PATH)
    return {
        "timestamp": latest.get("timestamp"),
        "event_type": latest.get("event_type"),
        "metrics": latest.get("metrics", {}),
    }


@app.get("/deployment")
def get_deployment() -> dict[str, Any]:
    if not DEPLOYMENT_MANIFEST_PATH.exists():
        raise HTTPException(status_code=404, detail="Deployment manifest not found")

    return json.loads(DEPLOYMENT_MANIFEST_PATH.read_text())


@app.get("/analysis")
def get_latest_analysis() -> dict[str, Any]:
    analysis: dict[str, Any] = {"metrics": None, "deployment": None}

    if PERFORMANCE_LOG_PATH.exists():
        analysis["metrics"] = _read_latest_json_line(PERFORMANCE_LOG_PATH)

    if DEPLOYMENT_MANIFEST_PATH.exists():
        analysis["deployment"] = json.loads(DEPLOYMENT_MANIFEST_PATH.read_text())

    with _jobs_lock:
        completed_jobs = [job for job in _jobs.values() if job["status"] == "completed"]

    if completed_jobs:
        latest_job = completed_jobs[-1]
        analysis["latest_run"] = {
            "status": latest_job["status"],
            "finished_at": latest_job["finished_at"],
            "result": latest_job["result"],
        }

    return analysis


@app.post("/rag/rebuild")
def rag_rebuild(force: bool = False) -> dict[str, Any]:
    """
    Build (or rebuild) the ChromaDB vector index from the current processed dataset.

    Pass ?force=true to wipe and recreate the collection from scratch.
    This must be called at least once before semantic search works.
    """
    try:
        from services.rag.rag import build_index
        result = build_index(data_path=str(PROCESSED_NEWS_PATH), force_rebuild=force)
        return result
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/rag/status")
def rag_status() -> dict[str, Any]:
    """
    Return the current state of the ChromaDB vector index:
    collection name, number of indexed documents, embedding strategy, and storage path.
    """
    try:
        from services.rag.rag import index_status
        return index_status()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


def serve() -> None:
    import uvicorn

    uvicorn.run("source_code.api:app", host="0.0.0.0", port=8000, reload=False)