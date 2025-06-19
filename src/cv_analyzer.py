"""
Core CV-Job Analyzer Logic
Location: src/cv_analyzer.py
"""

import json  # Digunakan di _load_skills_database

# import re # F401: 're' imported but unused - Dihapus karena tidak digunakan
from typing import (  # F401: 'typing.Tuple' imported but unused - 'Tuple' dihapus
    Dict,
    List,
)

import mlflow
import nltk

# import pandas as pd # F401: 'pandas as pd' imported but unused - Dihapus karena tidak digunakan
import spacy
from loguru import logger
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# 'Dict' dan 'List' tetap karena digunakan


# Download required NLTK data
try:
    nltk.download("punkt", quiet=True)
    nltk.download("stopwords", quiet=True)
except Exception as e:  # E722/B110: do not use bare 'except' - Diperbaiki
    logger.warning(
        f"Failed to download NLTK data: {e}"
    )  # Tambahkan logging daripada 'pass'


class CVJobAnalyzer:
    def __init__(self):
        self.nlp = None
        self.skills_database = self._load_skills_database()
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=1000, stop_words="english", ngram_range=(1, 2)
        )
        self._load_spacy_model()

    def _load_spacy_model(self):
        """Load spaCy model for NLP processing"""
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            logger.warning("spaCy model not found. Using basic processing.")
            self.nlp = None

    def _load_skills_database(self) -> Dict:
        """Load skills database from file"""
        try:
            with open("data/processed/skills_database.json", "r") as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning("Skills database not found. Using default skills.")
            return self._create_default_skills_database()

    def _create_default_skills_database(self) -> Dict:
        """Create default skills database"""
        return {
            "technical_skills": [
                "python",
                "java",
                "javascript",
                "react",
                "angular",
                "vue",
                "docker",
                "kubernetes",
                "aws",
                "azure",
                "gcp",
                "machine learning",
                "deep learning",
                "tensorflow",
                "pytorch",
                "sql",
                "postgresql",
                "mysql",
                "mongodb",
                "redis",
                "git",
                "jenkins",
                "ci/cd",
                "devops",
                "agile",
                "scrum",
            ],
            "soft_skills": [
                "communication",
                "leadership",
                "teamwork",
                "problem solving",
                "analytical thinking",
                "creativity",
                "adaptability",
                "time management",
                "project management",
            ],
            "domains": [
                "finance",
                "healthcare",
                "e-commerce",
                "education",
                "manufacturing",
                "retail",
                "telecommunications",
            ],
        }

    def extract_skills(self, text: str) -> List[str]:
        """Extract skills from text using keyword matching and NLP"""
        text_lower = text.lower()
        found_skills = []

        # Extract from all skill categories
        all_skills = []
        for category in self.skills_database.values():
            all_skills.extend(category)

        # Simple keyword matching
        for skill in all_skills:
            if skill.lower() in text_lower:
                found_skills.append(skill)

        # NLP-based extraction if spaCy is available
        if self.nlp:
            doc = self.nlp(text)
            # Extract technical terms and proper nouns
            for token in doc:
                if (
                    token.pos_ in ["NOUN", "PROPN"]
                    and len(token.text) > 2
                    and token.text.lower() not in ["experience", "work", "company"]
                ):
                    if any(skill in token.text.lower() for skill in all_skills):
                        found_skills.append(token.text)

        return list(set(found_skills))  # Remove duplicates

    def calculate_similarity(self, cv_text: str, job_text: str) -> float:
        """Calculate similarity between CV and job description using TF-IDF"""
        try:
            documents = [cv_text, job_text]
            tfidf_matrix = self.tfidf_vectorizer.fit_transform(documents)
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            return float(similarity)
        except Exception as e:
            logger.error(f"Error calculating similarity: {e}")
            return 0.0

    def analyze_match(self, cv_text: str, job_text: str) -> Dict:
        """Analyze match between CV and job description"""
        with mlflow.start_run():
            # Extract skills
            cv_skills = self.extract_skills(cv_text)
            job_skills = self.extract_skills(job_text)

            # Calculate matches
            matched_skills = list(set(cv_skills) & set(job_skills))
            missing_skills = list(set(job_skills) - set(cv_skills))

            # Calculate similarity score
            similarity_score = self.calculate_similarity(cv_text, job_text)

            # Calculate match percentage
            if len(job_skills) > 0:
                match_percentage = (len(matched_skills) / len(job_skills)) * 100
            else:
                match_percentage = 0

            # Combine scores (weighted average)
            final_score = (match_percentage * 0.7) + (similarity_score * 100 * 0.3)

            result = {
                "match_percentage": round(final_score, 2),
                "cv_skills": cv_skills,
                "job_skills": job_skills,
                "matched_skills": matched_skills,
                "missing_skills": missing_skills,
                "similarity_score": round(similarity_score, 4),
                "recommendations": self._generate_recommendations(missing_skills),
            }

            # Log to MLflow
            mlflow.log_metric("match_percentage", result["match_percentage"])
            mlflow.log_metric("similarity_score", result["similarity_score"])
            mlflow.log_metric("cv_skills_count", len(cv_skills))
            mlflow.log_metric("job_skills_count", len(job_skills))
            mlflow.log_metric("matched_skills_count", len(matched_skills))

            return result

    def _generate_recommendations(self, missing_skills: List[str]) -> List[str]:
        """Generate recommendations based on missing skills"""
        if not missing_skills:
            return ["Your CV shows excellent alignment with the job requirements!"]

        recommendations = [
            f"Consider highlighting experience with: {', '.join(missing_skills[:5])}",
            "Add relevant projects or certifications for missing skills",
            "Tailor your CV to include keywords from the job description",
        ]

        if len(missing_skills) > 5:
            recommendations.append(
                f"Focus on the most important skills: {', '.join(missing_skills[:3])}"
            )

        return recommendations
