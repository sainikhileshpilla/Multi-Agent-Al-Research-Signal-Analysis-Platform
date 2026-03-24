import json
import pathlib
import shutil
from datetime import datetime
from crewai.tools import BaseTool


PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]
MODEL_PATH = PROJECT_ROOT / "models" / "signal_model.pkl"
DEPLOY_DIR = PROJECT_ROOT / "deployed"
MANIFEST_PATH = DEPLOY_DIR / "deployment_manifest.json"


class ModelDeploymentTool(BaseTool):
    name: str = "model_deployment_tool"
    description: str = (
        "Deploys the trained signal model by copying it to the deployed/ directory "
        "and writing a deployment manifest with metadata. "
        "Returns a deployment confirmation report."
    )

    def _run(self) -> str:
        try:
            if not MODEL_PATH.exists():
                return f"Deployment failed: trained model not found at '{MODEL_PATH}'."

            DEPLOY_DIR.mkdir(parents=True, exist_ok=True)

            deployed_model_path = DEPLOY_DIR / "signal_model.pkl"
            shutil.copy2(str(MODEL_PATH), str(deployed_model_path))

            manifest = {
                "status": "deployed",
                "deployed_at": datetime.now().isoformat(),
                "source_model": str(MODEL_PATH),
                "deployed_model": str(deployed_model_path),
            }
            MANIFEST_PATH.write_text(json.dumps(manifest, indent=2))

            return (
                f"Model deployed successfully.\n"
                f"Deployed model: {deployed_model_path}\n"
                f"Manifest written: {MANIFEST_PATH}\n"
                f"Deployed at: {manifest['deployed_at']}"
            )
        except Exception as e:
            return f"Deployment failed: {str(e)}"
