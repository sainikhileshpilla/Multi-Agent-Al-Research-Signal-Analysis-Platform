# crew.py

from crewai import Agent, Task, Crew, Process
from source_code.tools.data_pipeline_tool import DataPipelineTool
from source_code.tools.financial_news_web_tool import FinancialNewsWebTool
from source_code.tools.csv_reader_tool import CSVReaderTool
from source_code.tools.model_training_tool import ModelTrainingTool
from source_code.tools.model_monitoring_tool import ModelMonitoringTool
from source_code.tools.model_prediction_tool import ModelPredictionTool
from source_code.tools.model_deployment_tool import ModelDeploymentTool

RAW_DATA_PATH = "data/raw/live_news.csv"
PROCESSED_DATA_PATH = "data/processed/news_cleaned.csv"


class AISignalCrew:

    def __init__(self):
        self.data_tool = DataPipelineTool()
        self.web_news_tool = FinancialNewsWebTool()
        self.csv_reader_tool = CSVReaderTool()
        self.model_training_tool = ModelTrainingTool()
        self.model_monitoring_tool = ModelMonitoringTool()
        self.model_prediction_tool = ModelPredictionTool()
        self.model_deployment_tool = ModelDeploymentTool()

        # -------- Agents --------
        self.data_agent = Agent(
            role="Financial Data Engineer",
            goal="Ingest, validate, and structure financial news data for downstream AI workflows.",
            backstory="Expert in building reliable data pipelines for machine learning systems.",
            tools=[self.web_news_tool, self.data_tool],
            verbose=True,
        )

        self.research_agent = Agent(
            role="AI Research Analyst",
            goal="Analyze structured financial news data and extract contextual insights.",
            backstory="Specialist in contextual retrieval and structured analysis.",
            tools=[self.csv_reader_tool],
            verbose=True,
        )

        self.ml_agent = Agent(
            role="Machine Learning Engineer",
            goal="Train predictive models using structured signals and features.",
            backstory="Experienced in building and evaluating ML models with performance tracking.",
            tools=[self.model_training_tool],
            verbose=True,
        )

        self.prediction_agent = Agent(
            role="AI Prediction Agent",
            goal="Run inference using the trained model and summarize financial signal predictions.",
            backstory="Specialist in deploying ML models and interpreting their outputs for actionable insights.",
            tools=[self.model_prediction_tool],
            verbose=True,
        )

        self.deployment_agent = Agent(
            role="Model Deployment Agent",
            goal="Deploy the validated model to production and produce a deployment report.",
            backstory="Expert in ML model deployment, versioning, and release management.",
            tools=[self.model_deployment_tool],
            verbose=True,
        )

        self.monitoring_agent = Agent(
            role="AI Monitoring Engineer",
            goal="Monitor model performance, detect drift, and trigger retraining if needed.",
            backstory="Expert in AI reliability and production monitoring systems.",
            tools=[self.model_monitoring_tool],
            verbose=True,
        )

        # -------- Tasks --------
        self.data_task = Task(
            description=(
                f"Step 1: Use the financial_news_web_tool to fetch live financial news "
                f"from the web. It will save the raw articles to '{RAW_DATA_PATH}'. "
                f"Step 2: Use the data_pipeline_tool with input_path='{RAW_DATA_PATH}' "
                f"and output_path='{PROCESSED_DATA_PATH}' to validate, clean, and "
                f"structure the fetched data."
            ),
            expected_output=(
                "Confirmation of how many live articles were fetched per source, "
                "and that the dataset has been cleaned and saved."
            ),
            agent=self.data_agent,
        )

        self.research_task = Task(
            description=(
                f"Use the csv_reader_tool to read the cleaned financial news dataset at "
                f"'{PROCESSED_DATA_PATH}'. Analyze the records and extract structured insights "
                f"about sentiment distribution, headline patterns, and signals useful for market prediction."
            ),
            expected_output="Structured analytical summary of the financial news dataset.",
            agent=self.research_agent,
        )

        self.ml_task = Task(
            description=(
                f"Use the model_training_tool to train and compare multiple ML models on the "
                f"processed dataset at '{PROCESSED_DATA_PATH}'. Report the comparison across all "
                f"models and identify which performed best."
            ),
            expected_output=(
                "Comparison table of all trained models with accuracy, precision, recall, and F1 score. "
                "Name of the best model and its metrics."
            ),
            agent=self.ml_agent,
        )

        self.prediction_task = Task(
            description=(
                f"Use the model_prediction_tool to run predictions on the processed dataset "
                f"at '{PROCESSED_DATA_PATH}'. Summarize the bullish vs bearish signal distribution "
                f"and highlight any notable patterns in the results. "
                f"The dataset and trained model are confirmed to exist from the previous steps."
            ),
            expected_output=(
                "Prediction summary showing total records, bullish/bearish signal counts, "
                "and a sample of individual predictions."
            ),
            agent=self.prediction_agent,
            context=[self.ml_task],
        )

        self.monitoring_task = Task(
            description=(
                "Use the model_monitoring_tool to read the model performance log, check for "
                "accuracy drift between the two most recent runs, and trigger retraining if "
                "the accuracy has dropped by more than 5%. Report the current metrics and drift status."
            ),
            expected_output="Monitoring report with current model metrics and drift detection result.",
            agent=self.monitoring_agent,
        )

        self.deployment_task = Task(
            description=(
                "Use the model_deployment_tool to deploy the trained model. "
                "It will copy the model to the deployed/ directory and write a deployment manifest. "
                "Report the deployment confirmation including the deployed model path and timestamp."
            ),
            expected_output=(
                "Deployment confirmation report with the deployed model path, "
                "manifest location, and deployment timestamp."
            ),
            agent=self.deployment_agent,
            context=[self.monitoring_task],
        )

    def build(self):
        return Crew(
            agents=[
                self.data_agent,
                self.research_agent,
                self.ml_agent,
                self.prediction_agent,
                self.monitoring_agent,
                self.deployment_agent,
            ],
            tasks=[
                self.data_task,
                self.research_task,
                self.ml_task,
                self.prediction_task,
                self.monitoring_task,
                self.deployment_task,
            ],
            process=Process.sequential,
            verbose=True,
        )
