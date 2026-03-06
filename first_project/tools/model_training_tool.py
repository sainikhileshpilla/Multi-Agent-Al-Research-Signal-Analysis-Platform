import pathlib
from crewai.tools import BaseTool
from first_project.pipelines.train import train_model

PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]


def _resolve(path: str) -> str:
    p = pathlib.Path(path)
    return str(p) if p.is_absolute() else str(PROJECT_ROOT / p)


class ModelTrainingTool(BaseTool):
    name: str = "model_training_tool"
    description: str = (
        "Trains and compares multiple ML models (Logistic Regression, Random Forest, "
        "Gradient Boosting, SVM) on the cleaned financial news dataset. "
        "Accepts the path to the processed CSV file. Selects the best model by F1 score "
        "and saves it to models/signal_model.pkl. Returns a comparison of all models."
    )

    def _run(self, data_path: str) -> str:
        try:
            metrics = train_model(_resolve(data_path))
            best = metrics["best_model"]
            all_models = metrics["all_models"]

            comparison = "\n".join(
                f"  {name}: accuracy={r['accuracy']:.4f}  precision={r['precision']:.4f}"
                f"  recall={r['recall']:.4f}  f1={r['f1_score']:.4f}"
                for name, r in all_models.items()
            )

            return (
                f"Model comparison:\n{comparison}\n\n"
                f"Best model: {best}\n"
                f"Accuracy:  {metrics['accuracy']:.4f}\n"
                f"Precision: {metrics['precision']:.4f}\n"
                f"Recall:    {metrics['recall']:.4f}\n"
                f"F1 Score:  {metrics['f1_score']:.4f}\n"
                f"Saved to models/signal_model.pkl."
            )
        except Exception as e:
            return f"Model training failed: {str(e)}"
