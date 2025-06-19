"""
Data Preparation Script
Location: src/data_preparation.py
"""

import json
from pathlib import Path

from loguru import logger


def create_skills_database():
    """Create comprehensive skills database"""

    skills_database = {
        "technical_skills": [
            # Programming Languages
            "python",
            "java",
            "javascript",
            "typescript",
            "c++",
            "c#",
            "go",
            "rust",
            "php",
            "ruby",
            "swift",
            "kotlin",
            "scala",
            "r",
            "matlab",
            "sql",
            # Web Technologies
            "react",
            "angular",
            "vue",
            "node.js",
            "express",
            "django",
            "flask",
            "fastapi",
            "spring",
            "laravel",
            "rails",
            "asp.net",
            # Databases
            "mysql",
            "postgresql",
            "mongodb",
            "redis",
            "elasticsearch",
            "cassandra",
            "oracle",
            "sqlite",
            "dynamodb",
            "neo4j",
            # Cloud & DevOps
            "aws",
            "azure",
            "gcp",
            "docker",
            "kubernetes",
            "terraform",
            "ansible",
            "jenkins",
            "gitlab ci",
            "github actions",
            "travis ci",
            "circleci",
            # Data & AI
            "machine learning",
            "deep learning",
            "tensorflow",
            "pytorch",
            "scikit-learn",
            "pandas",
            "numpy",
            "spark",
            "hadoop",
            "kafka",
            "airflow",
            # Tools & Platforms
            "git",
            "jira",
            "confluence",
            "slack",
            "figma",
            "adobe",
            "linux",
            "windows",
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
            "critical thinking",
            "collaboration",
            "attention to detail",
            "customer service",
            "negotiation",
            "presentation skills",
            "mentoring",
            "coaching",
        ],
        "domains": [
            "fintech",
            "healthcare",
            "e-commerce",
            "education",
            "manufacturing",
            "retail",
            "telecommunications",
            "automotive",
            "aerospace",
            "gaming",
            "media",
            "marketing",
            "logistics",
            "real estate",
            "insurance",
        ],
        "methodologies": [
            "agile",
            "scrum",
            "kanban",
            "waterfall",
            "lean",
            "six sigma",
            "devops",
            "ci/cd",
            "tdd",
            "bdd",
            "microservices",
            "apis",
        ],
    }

    # Save to file
    output_path = Path("data/processed/skills_database.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w") as f:
        json.dump(skills_database, f, indent=2)

    logger.info(
        f"Skills database created with {sum(len(v) for v in skills_database.values())} total skills"
    )
    return skills_database


def prepare_sample_data():
    """Prepare sample CV and job data for testing"""

    sample_data = {
        "sample_cvs": [
            {
                "id": 1,
                "title": "Senior Python Developer",
                "text": """
                Senior Software Engineer with 7+ years of experience in Python development.
                Expertise in Django, Flask, FastAPI, and RESTful APIs. Strong background in
                AWS cloud services, Docker, and Kubernetes. Experience with machine learning
                using TensorFlow and scikit-learn. Proficient in SQL databases (PostgreSQL, MySQL)
                and NoSQL (MongoDB, Redis). Familiar with agile methodologies and CI/CD pipelines.
                Led teams of 5+ developers in multiple projects.
                """,
            },
            {
                "id": 2,
                "title": "Frontend React Developer",
                "text": """
                Frontend Developer with 4 years of experience specializing in React.js and modern
                JavaScript. Proficient in TypeScript, Redux, and React Hooks. Experience with
                responsive design, CSS3, SASS, and Tailwind CSS. Familiar with testing frameworks
                like Jest and Cypress. Knowledge of Node.js and Express for full-stack development.
                Strong collaboration skills and experience with agile development processes.
                """,
            },
        ],
        "sample_jobs": [
            {
                "id": 1,
                "title": "Senior Python Engineer",
                "text": """
                We are seeking a Senior Python Engineer to join our growing team. The ideal candidate
                will have 5+ years of experience with Python, Django/Flask, and cloud technologies.
                Must have experience with AWS, Docker, and microservices architecture. Knowledge of
                machine learning and data analysis is a plus. Strong problem-solving skills and
                experience with agile development methodologies required.
                """,
            },
            {
                "id": 2,
                "title": "React Frontend Developer",
                "text": """
                Looking for a skilled React Developer to build modern web applications. Requirements
                include 3+ years of React experience, proficiency in JavaScript/TypeScript, and
                knowledge of state management (Redux/Context API). Experience with testing frameworks,
                responsive design, and modern CSS techniques required. Bonus points for Node.js
                experience and full-stack capabilities.
                """,
            },
        ],
    }

    # Save sample data
    output_path = Path("data/raw/sample_data.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w") as f:
        json.dump(sample_data, f, indent=2)

    logger.info(
        f"Sample data created with {len(sample_data['sample_cvs'])} CVs and {len(sample_data['sample_jobs'])} jobs"
    )
    return sample_data


if __name__ == "__main__":
    logger.info("Starting data preparation...")

    # Create skills database
    skills_db = create_skills_database()

    # Prepare sample data
    sample_data = prepare_sample_data()

    logger.info("Data preparation completed successfully!")
