"""
Unit Tests for CV Analyzer
Location: tests/test_cv_analyzer.py
"""

import os
import sys

import pytest

from cv_analyzer import CVJobAnalyzer

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))


class TestCVJobAnalyzer:
    def setup_method(self):
        """Setup test fixtures"""
        self.analyzer = CVJobAnalyzer()

        # Sample data
        self.sample_cv = """
        Software Engineer with 5 years of experience in Python, JavaScript, React,
        Docker, AWS, and machine learning. Strong background in agile development
        and team collaboration.
        """

        self.sample_job = """
        Senior Software Engineer position requiring expertise in Python, React,
        AWS, Docker, Kubernetes, machine learning, and agile methodologies.
        Minimum 3 years experience required.
        """

    def test_extract_skills(self):
        """Test skill extraction"""
        skills = self.analyzer.extract_skills(self.sample_cv)

        assert isinstance(skills, list)
        assert len(skills) > 0
        assert any("python" in skill.lower() for skill in skills)
        assert any("react" in skill.lower() for skill in skills)

    def test_calculate_similarity(self):
        """Test similarity calculation"""
        similarity = self.analyzer.calculate_similarity(self.sample_cv, self.sample_job)

        assert isinstance(similarity, float)
        assert 0 <= similarity <= 1
        assert similarity > 0.1  # Should have some similarity

    def test_analyze_match(self):
        """Test complete match analysis"""
        result = self.analyzer.analyze_match(self.sample_cv, self.sample_job)

        # Check result structure
        required_keys = [
            "match_percentage",
            "cv_skills",
            "job_skills",
            "matched_skills",
            "missing_skills",
            "recommendations",
        ]

        for key in required_keys:
            assert key in result

        # Check data types
        assert isinstance(result["match_percentage"], (int, float))
        assert isinstance(result["cv_skills"], list)
        assert isinstance(result["job_skills"], list)
        assert isinstance(result["matched_skills"], list)
        assert isinstance(result["missing_skills"], list)
        assert isinstance(result["recommendations"], list)

        # Check ranges
        assert 0 <= result["match_percentage"] <= 100
        assert len(result["recommendations"]) > 0

    def test_empty_inputs(self):
        """Test handling of empty inputs"""
        result = self.analyzer.analyze_match("", "")

        assert result["match_percentage"] == 0
        assert result["cv_skills"] == []
        assert result["job_skills"] == []

    def test_skills_database_loading(self):
        """Test skills database loading"""
        skills_db = self.analyzer.skills_database

        assert isinstance(skills_db, dict)
        assert "technical_skills" in skills_db
        assert "soft_skills" in skills_db
        assert len(skills_db["technical_skills"]) > 0


class TestMetrics:
    def setup_method(self):
        """Setup metrics test"""
        from metrics import (  # Import ini di dalam method untuk menghindari F401 jika MetricsCollector hanya dipakai di sini
            MetricsCollector,
        )

        self.metrics = MetricsCollector()

    def test_record_analysis(self):
        """Test metrics recording"""
        # Should not raise exceptions
        self.metrics.record_analysis(
            match_percentage=75.5,
            processing_time=1.2,
            cv_length=500,
            job_length=300,
            ai_enhanced=False,
        )

        # Check metrics format
        metrics_output = self.metrics.get_metrics()
        assert isinstance(metrics_output, (str, bytes))
        assert (
            b"cv_analysis_total" in metrics_output.encode()
            if isinstance(metrics_output, str)
            else metrics_output
        )


# Integration tests
class TestIntegration:
    def test_full_pipeline(self):
        """Test full analysis pipeline"""
        analyzer = CVJobAnalyzer()

        cv_text = "Python developer with React and AWS experience"
        job_text = "Looking for Python developer with React and cloud experience"

        result = analyzer.analyze_match(cv_text, job_text)

        assert result["match_percentage"] > 50  # Should be a good match
        assert len(result["matched_skills"]) > 0
        assert "python" in [skill.lower() for skill in result["matched_skills"]]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
