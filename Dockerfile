FROM python:3.10-slim-buster

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Tambahkan baris ini untuk memastikan Pydantic v2.x terinstal dengan benar
RUN pip install --no-cache-dir "pydantic>=2.0.0,<3.0.0"

# Download spacy model
RUN python -m spacy download en_core_web_sm

# Copy application code
COPY . .

# Expose ports
EXPOSE 7860 8080

# Default command
CMD ["python", "src/app.py"]
