"""
Metrics Collection for Monitoring
Location: src/metrics.py
"""

import threading
import time

import psutil
from loguru import logger
from prometheus_client import (
    CollectorRegistry,
    Counter,
    Gauge,
    Histogram,
    generate_latest,
)


class MetricsCollector:
    def __init__(self):
        self.registry = CollectorRegistry()

        # Define metrics
        self.analysis_counter = Counter(
            "cv_analysis_total",
            "Total number of CV analyses performed",
            ["status"],
            registry=self.registry,
        )

        self.analysis_duration = Histogram(
            "cv_analysis_duration_seconds",
            "Time spent analyzing CV-Job matches",
            ["ai_enhanced"],
            registry=self.registry,
        )

        self.match_score_gauge = Gauge(
            "cv_match_score", "Current match score percentage", registry=self.registry
        )

        self.system_cpu_usage = Gauge(
            "system_cpu_usage_percent",
            "System CPU usage percentage",
            registry=self.registry,
        )

        self.system_memory_usage = Gauge(
            "system_memory_usage_percent",
            "System memory usage percentage",
            registry=self.registry,
        )

        self.active_users = Gauge(
            "active_users_count", "Number of active users", registry=self.registry
        )

        # Start system metrics collection
        self._start_system_metrics_collection()

    def record_analysis(
        self,
        match_percentage: float,
        processing_time: float,
        cv_length: int,
        job_length: int,
        ai_enhanced: bool = False,
    ):
        """Record analysis metrics"""
        try:
            # Update counters and histograms
            self.analysis_counter.labels(status="success").inc()
            self.analysis_duration.labels(ai_enhanced=str(ai_enhanced)).observe(
                processing_time
            )
            self.match_score_gauge.set(match_percentage)

            logger.info(
                f"Recorded metrics: score={match_percentage:.1f}%, time={processing_time:.2f}s"
            )

        except Exception as e:
            logger.error(f"Failed to record metrics: {e}")
            self.analysis_counter.labels(status="error").inc()

    def record_error(self, error_type: str = "unknown"):
        """Record error metrics"""
        self.analysis_counter.labels(status="error").inc()
        logger.warning(f"Recorded error metric: {error_type}")

    def get_metrics(self) -> str:
        """Get metrics in Prometheus format"""
        return generate_latest(self.registry)

    def _start_system_metrics_collection(self):
        """Start background thread for system metrics"""

        def collect_system_metrics():
            while True:
                try:
                    # CPU usage
                    cpu_percent = psutil.cpu_percent(interval=1)
                    self.system_cpu_usage.set(cpu_percent)

                    # Memory usage
                    memory = psutil.virtual_memory()
                    self.system_memory_usage.set(memory.percent)

                    time.sleep(30)  # Collect every 30 seconds

                except Exception as e:
                    logger.error(f"System metrics collection failed: {e}")
                    time.sleep(60)  # Wait longer on error

        metrics_thread = threading.Thread(target=collect_system_metrics, daemon=True)
        metrics_thread.start()
        logger.info("Started system metrics collection thread")

    def update_active_users(self, count: int):
        """Update active users count"""
        self.active_users.set(count)


# Global metrics instance
metrics_collector = MetricsCollector()
