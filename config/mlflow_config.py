"""
MLflow Configuration
Location: config/mlflow_config.py
"""

import os

import mlflow
from mlflow.tracking import MlflowClient


class MLflowConfig:
    def __init__(self):
        self.tracking_uri = os.getenv("MLFLOW_TRACKING_URI", "sqlite:///mlflow.db")
        self.experiment_name = "cv-job-analyzer"
        self.artifact_location = "./mlruns"

    def setup_mlflow(self):
        """Initialize MLflow tracking"""
        mlflow.set_tracking_uri(self.tracking_uri)

        # Create experiment if it doesn't exist
        try:
            experiment = mlflow.get_experiment_by_name(self.experiment_name)
            if experiment is None:
                mlflow.create_experiment(
                    name=self.experiment_name, artifact_location=self.artifact_location
                )
        except Exception as e:
            print(f"Error setting up MLflow: {e}")

        mlflow.set_experiment(self.experiment_name)

    def get_client(self):
        """Get MLflow client"""
        return MlflowClient(tracking_uri=self.tracking_uri)
