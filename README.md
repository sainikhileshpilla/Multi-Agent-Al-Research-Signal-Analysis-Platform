# Multi-Agent AI Research Signal Analysis Platform

This repository contains a **CrewAI-based multi-agent machine learning pipeline** designed to ingest, analyze, train, monitor and deploy predictive signals from financial news sources. The system handles multiple data formats, incorporates retrieval-augmented generation (RAG) for contextual analysis, and automatically retrains on drift.

## Features

- Sequential crew of six specialized AI agents:
  1. Financial Data Engineer – ingest/clean multi-source news (CSV, Excel, PDF, RSS).
  2. AI Research Analyst – analyze filtered data and perform RAG retrieval over historical articles.
  3. Machine Learning Engineer – prepare features and train logistic regression model.
  4. AI Prediction Agent – run inference and contextualize predictions.
  5. AI Monitoring Engineer – detect performance drift and trigger retraining.
  6. Model Deployment Agent – package and deploy the trained model with manifest.

- **Multi-format ingestion**: automatically reads and normalizes CSV, XLSX, and PDF files; supports live RSS feeds.
- **Retrieval-augmented generation**: builds an embedding index of historical headlines using OpenAI embeddings, enabling agents to retrieve similar articles for richer insights.
- **Automatic drift detection**: monitors accuracy and triggers retraining when performance drops by more than 5%.
- **Deployment workflow**: copies the model to a `deployed/` directory and writes a deployment manifest containing metadata.
- **Logging & monitoring**: ingestion, performance, and system events are written to JSON logs for auditing.
- **Configurable via `.env`** for secrets such as `OPENAI_API_KEY`.

## Getting Started

### Prerequisites

- Python 3.10+ (3.12 used in development)
- Git

### Setup

```bash
cd /home/scarlett_speedster/source_code
source cleanenv/bin/activate      # activate the provided virtual environment
```

If you prefer a fresh environment:

```bash
python3 -m venv cleanenv
source cleanenv/bin/activate
uv sync                            # install dependencies via uv
``` 

### Running the Pipeline

```bash
# run the full crew pipeline
cleanenv/bin/python -m source_code.main

# or short
uv run source_code
```

### Data

Place any CSV/Excel/PDF files you want to analyze into `data/raw/`.  The data pipeline will normalize columns and combine the sources, expecting at least: `headline`, `content`, `timestamp`, `source`.

Example raw files:
```
data/raw/
├── sample_news.csv
├── earnings_reports.xlsx
└── q1_press_release.pdf
```

### Useful Scripts

- `uv run train` – train the model without running agents.
- `uv run run_with_trigger` – run and retrain if drift detected.

## Project Structure

```
source_code/                # Python package
├── crew.py                   # Crew & agent definitions
├── main.py                   # CLI entrypoint
├── pipelines/                # ingestion, validation, training logic
├── tools/                    # CrewAI tool wrappers
├── monitoring/               # drift detection & logging helpers
├── agents/                   # agent classes (optional)

data/                         # datasets (raw, processed)
models/                       # trained model artifacts
logs/                         # JSON event logs
deployed/                     # deployed model + manifest
cleanenv/                     # virtual environment (ignored by git)
pyproject.toml               # project metadata & dependencies
README.md                    # this file
.gitignore
```

## Contributing

1. Fork the repo.
2. Create a new branch: `git checkout -b feature/my-new-feature`
3. Make your changes and commit: `git commit -m "Add ..."`.
4. Push: `git push origin feature/my-new-feature` and open a pull request.

## License

This project is released under the MIT License.
