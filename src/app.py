"""
Gradio UI Application with FastAPI Metrics Integration
Location: src/app.py
"""

import os
import threading
import time

import gradio as gr
import pandas as pd
import uvicorn

# FastAPI imports
from fastapi import FastAPI
from fastapi.responses import Response
from loguru import logger

from ai_enhancement import AIEnhancer
from cv_analyzer import CVJobAnalyzer
from metrics import MetricsCollector

# Initialize components
analyzer = CVJobAnalyzer()
ai_enhancer = AIEnhancer()
metrics = MetricsCollector()

# Initialize FastAPI app for metrics
app = FastAPI(title="CV Analyzer API", version="1.0.0")


@app.get("/metrics")
async def get_metrics():
    """Prometheus metrics endpoint"""
    return Response(content=metrics.get_metrics(), media_type="text/plain")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "service": "cv-analyzer",
        "version": "1.0.0",
    }


@app.get("/stats")
async def get_stats():
    """Get application statistics"""
    return {
        "total_analyses": metrics.get_total_analyses(),
        "average_match_score": metrics.get_average_match_score(),
        "average_processing_time": metrics.get_average_processing_time(),
        "uptime": (
            time.time() - metrics.start_time if hasattr(metrics, "start_time") else 0
        ),
    }


def analyze_cv_job_match(cv_text, job_text, use_ai_enhancement=False):
    """Main function to analyze CV-Job match"""
    start_time = time.time()

    try:
        # Validate inputs
        if not cv_text.strip() or not job_text.strip():
            return "Error: Please provide both CV text and job description.", None, None

        # Basic analysis
        result = analyzer.analyze_match(cv_text, job_text)

        # AI enhancement if requested
        if use_ai_enhancement:
            try:
                enhanced_result = ai_enhancer.enhance_analysis(
                    cv_text, job_text, result
                )
                result.update(enhanced_result)
            except Exception as e:
                logger.error(f"AI enhancement failed: {e}")
                result["ai_enhancement_error"] = str(e)

        # Record metrics
        processing_time = time.time() - start_time
        metrics.record_analysis(
            match_percentage=result["match_percentage"],
            processing_time=processing_time,
            cv_length=len(cv_text),
            job_length=len(job_text),
            ai_enhanced=use_ai_enhancement,
        )

        # Format output
        summary = f"""
        ## 📊 Match Analysis Results

        **Overall Match Score: {result['match_percentage']:.1f}%**

        ### ✅ Matched Skills ({len(result['matched_skills'])})
        {', '.join(result['matched_skills']) if result['matched_skills'] else 'None found'}

        ### ❌ Missing Skills ({len(result['missing_skills'])})
        {', '.join(result['missing_skills']) if result['missing_skills'] else 'None'}

        ### 🎯 Recommendations
        {chr(10).join(f"• {rec}" for rec in result['recommendations'])}

        ### 📈 Technical Details
        - **Similarity Score:** {result['similarity_score']:.4f}
        - **CV Skills Found:** {len(result['cv_skills'])}
        - **Job Skills Required:** {len(result['job_skills'])}
        - **Processing Time:** {processing_time:.2f}s
        - **AI Enhanced:** {'Yes' if use_ai_enhancement else 'No'}
        """

        # Create skills comparison dataframe
        skills_df = pd.DataFrame(
            {
                "Skill": result["job_skills"],
                "Status": [
                    "✅ Matched" if skill in result["matched_skills"] else "❌ Missing"
                    for skill in result["job_skills"]
                ],
            }
        )

        return summary, skills_df, result["match_percentage"]

    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        # Record failed analysis
        metrics.record_error("analysis_failed", str(e))
        return f"Error: {str(e)}", None, None


def create_gradio_interface():
    """Create Gradio interface"""

    with gr.Blocks(
        title="Smart CV-Job Analyzer",
        theme=gr.themes.Soft(),
        css="""
        .gradio-container {
            font-family: 'Arial', sans-serif;
        }
        .match-score {
            font-size: 24px;
            font-weight: bold;
            text-align: center;
            padding: 20px;
            border-radius: 10px;
            margin: 10px 0;
        }
        .info-box {
            background-color: #f0f0f0;
            padding: 15px;
            border-radius: 8px;
            margin: 10px 0;
        }
        """,
    ) as demo:
        gr.Markdown(
            """
        # 🎯 Smart CV-Job Analyzer

        **Analyze how well your CV matches a job description using AI-powered insights.**

        Simply paste your CV text and the job description below to get instant analysis!

        ---
        """
        )

        with gr.Row():
            with gr.Column(scale=1):
                cv_input = gr.Textbox(
                    label="📄 Your CV Text",
                    placeholder="Paste your CV content here...",
                    lines=10,
                    max_lines=15,
                )

            with gr.Column(scale=1):
                job_input = gr.Textbox(
                    label="💼 Job Description",
                    placeholder="Paste the job description here...",
                    lines=10,
                    max_lines=15,
                )

        with gr.Row():
            with gr.Column(scale=3):
                ai_enhancement = gr.Checkbox(
                    label="🤖 Use AI Enhancement (IBM Granite)",
                    value=False,
                    info="Enable AI-powered analysis for deeper insights",
                )
            with gr.Column(scale=1):
                analyze_btn = gr.Button(
                    "🔍 Analyze Match", variant="primary", size="lg"
                )

        with gr.Row():
            with gr.Column(scale=2):
                result_output = gr.Markdown(label="📊 Analysis Results")

            with gr.Column(scale=1):
                match_score = gr.Number(label="🎯 Match Score (%)", precision=1)

        skills_table = gr.Dataframe(
            label="📋 Skills Breakdown",
            headers=["Skill", "Status"],
            datatype=["str", "str"],
            wrap=True,
        )

        # Event handlers
        analyze_btn.click(
            fn=analyze_cv_job_match,
            inputs=[cv_input, job_input, ai_enhancement],
            outputs=[result_output, skills_table, match_score],
        )

        # Examples
        gr.Examples(
            examples=[
                [
                    "Software Engineer with 5 years experience in Python, JavaScript, React, Docker, AWS, "
                    "machine learning, and agile development. Strong background in full-stack development "
                    "and DevOps practices.",
                    False,
                ],
                [
                    "Looking for Senior Software Engineer with expertise in Python, React, AWS, Docker, "
                    "Kubernetes, machine learning, and experience with agile methodologies. Must have 3+ "
                    "years experience in full-stack development.",
                    True,
                ],
            ],
            inputs=[cv_input, job_input, ai_enhancement],
        )

        with gr.Accordion("📊 System Information", open=False):
            gr.Markdown(
                """
            ### 🔧 Service Endpoints:
            - **Gradio UI:** http://localhost:7860
            - **Metrics:** http://localhost:8080/metrics
            - **Health Check:** http://localhost:8080/health
            - **Statistics:** http://localhost:8080/stats

            ### 💡 Tips for Better Results:
            - Include specific technical skills and tools in your CV
            - Use keywords from the job description
            - Mention relevant experience and projects
            - Be specific about your expertise level

            ### 🔧 Powered by:
            - **NLP Processing:** spaCy + NLTK
            - **AI Enhancement:** IBM Granite via Replicate
            - **MLOps:** MLflow tracking + Prometheus metrics
            - **UI:** Gradio + FastAPI
            """
            )

    return demo


def run_fastapi():
    """Run FastAPI server for metrics"""
    logger.info("Starting FastAPI metrics server on port 8080...")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8080,
        log_level="info",
        access_log=False,  # Reduce log noise
    )


def setup_directories():
    """Create necessary directories"""
    directories = ["logs", "data/raw", "data/processed", "models", "metrics"]
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        logger.info(f"Created directory: {directory}")


if __name__ == "__main__":
    # Setup directories
    setup_directories()

    # Setup logging
    logger.add(
        "logs/app.log",
        rotation="1 day",
        retention="7 days",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
    )
    logger.info("Starting Smart CV-Job Analyzer...")

    # Initialize metrics start time
    metrics.start_time = time.time()

    # Start FastAPI server in background thread
    logger.info("Initializing FastAPI metrics server...")
    fastapi_thread = threading.Thread(target=run_fastapi, daemon=True)
    fastapi_thread.start()

    # Give FastAPI time to start
    time.sleep(2)
    logger.info("FastAPI metrics server started successfully")

    # Create and launch Gradio interface
    logger.info("Initializing Gradio interface...")
    demo = create_gradio_interface()

    logger.info("Launching Gradio application...")
    logger.info("Access the application at: http://localhost:7860")
    logger.info("Access metrics at: http://localhost:8080/metrics")
    logger.info("Access health check at: http://localhost:8080/health")

    # Launch Gradio with custom settings
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        debug=True,
        show_error=True,
        show_tips=True,
        enable_queue=True,
    )
