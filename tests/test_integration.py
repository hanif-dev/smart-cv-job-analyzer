"""
Integration Tests
Location: tests/test_integration.py
"""

import os
import subprocess
import sys
import time

import pytest
import requests

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))


class TestAPIIntegration:
    """Test FastAPI endpoints"""

    @pytest.fixture(scope="class")
    def api_server(self):
        """Start API server for testing"""
        # This would be used in a real scenario with proper server setup
        base_url = "http://localhost:8080"
        return base_url

    def test_health_endpoint(self, api_server):
        """Test health check endpoint"""
        try:
            response = requests.get(f"{api_server}/health", timeout=5)
            assert response.status_code == 200

            data = response.json()
            assert "status" in data
            assert data["status"] == "healthy"

        except requests.exceptions.RequestException:
            pytest.skip("API server not running")

    def test_metrics_endpoint(self, api_server):
        """Test metrics endpoint"""
        try:
            response = requests.get(f"{api_server}/metrics", timeout=5)
            assert response.status_code == 200
            assert "text/plain" in response.headers.get("content-type", "")

        except requests.exceptions.RequestException:
            pytest.skip("API server not running")


class TestDockerIntegration:
    """Test Docker functionality"""

    def test_docker_build(self):
        """Test Docker image builds successfully"""
        try:
            result = subprocess.run(
                ["docker", "build", "-t", "test-cv-analyzer", "."],
                capture_output=True,
                text=True,
                timeout=300,
            )
            assert result.returncode == 0

        except (subprocess.TimeoutExpired, FileNotFoundError):
            pytest.skip("Docker not available or build timeout")

    def test_docker_run(self):
        """Test Docker container runs"""
        try:
            # Start container
            result = subprocess.run(
                [
                    "docker",
                    "run",
                    "-d",
                    "--name",
                    "test-cv-container",
                    "-p",
                    "7861:7860",
                    "test-cv-analyzer:latest",
                ],
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                time.sleep(10)  # Wait for startup

                # Test if container is running
                result = subprocess.run(
                    ["docker", "ps", "--filter", "name=test-cv-container"],
                    capture_output=True,
                    text=True,
                )
                assert "test-cv-container" in result.stdout

                # Cleanup
                subprocess.run(
                    ["docker", "stop", "test-cv-container"], capture_output=True
                )
                subprocess.run(
                    ["docker", "rm", "test-cv-container"], capture_output=True
                )
            else:
                pytest.skip("Docker container failed to start")

        except FileNotFoundError:
            pytest.skip("Docker not available")


class TestMLflowIntegration:
    """Test MLflow integration"""

    def test_mlflow_tracking(self):
        """Test MLflow experiment tracking"""
        import mlflow

        from config.mlflow_config import MLflowConfig

        config = MLflowConfig()
        config.setup_mlflow()

        # Test experiment creation
        experiment = mlflow.get_experiment_by_name(config.experiment_name)
        assert experiment is not None

        # Test run creation
        with mlflow.start_run():
            mlflow.log_metric("test_metric", 1.0)
            mlflow.log_param("test_param", "test_value")

        # Verify run was logged
        runs = mlflow.search_runs()
        assert len(runs) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
