"""
AI Enhancement using IBM Granite via Replicate
Location: src/ai_enhancement.py
"""

import os
import time
from typing import Dict

import replicate
from loguru import logger


class AIEnhancer:
    def __init__(self):
        self.client = None
        self.model_name = "ibm-granite/granite-3.0-8b-instruct"
        self._setup_replicate()

    def _setup_replicate(self):
        """Setup Replicate client"""
        api_token = os.getenv("REPLICATE_API_TOKEN")
        if not api_token:
            logger.warning("REPLICATE_API_TOKEN not found. AI enhancement disabled.")
            return

        try:
            os.environ["REPLICATE_API_TOKEN"] = api_token
            self.client = replicate
            logger.info("Replicate client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Replicate client: {e}")

    def enhance_analysis(self, cv_text: str, job_text: str, basic_result: Dict) -> Dict:
        """Enhance analysis using IBM Granite AI"""
        if not self.client:
            return {"ai_enhancement": "AI enhancement not available"}

        try:
            # Prepare prompt for AI analysis
            prompt = self._create_analysis_prompt(cv_text, job_text, basic_result)

            # Call IBM Granite model
            start_time = time.time()
            response = self.client.run(
                self.model_name,
                input={
                    "prompt": prompt,
                    "max_tokens": 1000,
                    "temperature": 0.3,
                    "top_p": 0.9,
                },
            )

            # Process response
            ai_response = (
                "".join(response) if isinstance(response, list) else str(response)
            )
            processing_time = time.time() - start_time

            # Parse AI insights
            ai_insights = self._parse_ai_response(ai_response)

            return {
                "ai_insights": ai_insights,
                "ai_processing_time": processing_time,
                "ai_model_used": self.model_name,
            }

        except Exception as e:
            logger.error(f"AI enhancement failed: {e}")
            return {"ai_enhancement_error": str(e)}

    def _create_analysis_prompt(
        self, cv_text: str, job_text: str, basic_result: Dict
    ) -> str:
        """Create structured prompt for AI analysis"""
        prompt = f"""
        You are an expert HR analyst and career advisor. Analyze the following CV and job description match.

        BASIC ANALYSIS RESULTS:
        - Match Score: {basic_result['match_percentage']:.1f}%
        - Matched Skills: {', '.join(basic_result['matched_skills'])}
        - Missing Skills: {', '.join(basic_result['missing_skills'])}

        CV TEXT (first 500 chars):
        {cv_text[:500]}...

        JOB DESCRIPTION (first 500 chars):
        {job_text[:500]}...

        Please provide:
        1. DETAILED ASSESSMENT: Analyze the candidate's fit beyond just keyword matching
        2. SKILL GAPS: Identify the most critical missing skills and why they matter
        3. STRENGTHS: Highlight the candidate's strongest points for this role
        4. RECOMMENDATIONS: Specific, actionable advice to improve the match
        5. INTERVIEW TIPS: What the candidate should emphasize if they get an interview

        Format your response as clear, actionable insights that would help both the candidate and hiring manager.
        """

        return prompt

    def _parse_ai_response(self, response: str) -> Dict:
        """Parse AI response into structured insights"""
        insights = {
            "detailed_assessment": "",
            "critical_gaps": [],
            "key_strengths": [],
            "specific_recommendations": [],
            "interview_tips": [],
            "raw_response": response,
        }

        try:
            # Simple parsing - look for numbered sections
            sections = response.split("\n")
            current_section = None

            for line in sections:
                line = line.strip()
                if not line:
                    continue

                # Identify sections
                if "DETAILED ASSESSMENT" in line.upper():
                    current_section = "detailed_assessment"
                elif "SKILL GAPS" in line.upper() or "GAPS" in line.upper():
                    current_section = "critical_gaps"
                elif "STRENGTHS" in line.upper():
                    current_section = "key_strengths"
                elif "RECOMMENDATIONS" in line.upper():
                    current_section = "specific_recommendations"
                elif "INTERVIEW" in line.upper():
                    current_section = "interview_tips"
                else:
                    # Add content to current section
                    if current_section == "detailed_assessment":
                        insights["detailed_assessment"] += line + " "
                    elif current_section and line.startswith(
                        ("-", "•", "1.", "2.", "3.")
                    ):
                        clean_line = line.lstrip("-•123456789. ")
                        if clean_line:
                            insights[current_section].append(clean_line)

            # Clean up detailed assessment
            insights["detailed_assessment"] = insights["detailed_assessment"].strip()

        except Exception as e:
            logger.error(f"Error parsing AI response: {e}")
            insights["parsing_error"] = str(e)

        return insights

    def generate_cover_letter_tips(self, cv_text: str, job_text: str) -> str:
        """Generate cover letter tips using AI"""
        if not self.client:
            return "AI enhancement not available"

        try:
            prompt = f"""
            Based on this CV and job description, provide 3-5 specific tips for writing a compelling cover letter:

            CV: {cv_text[:300]}...
            Job: {job_text[:300]}...

            Focus on:
            - Key achievements to highlight
            - How to address potential gaps
            - Specific language to use
            - Company/role-specific angles
            """

            response = self.client.run(
                self.model_name,
                input={"prompt": prompt, "max_tokens": 500, "temperature": 0.4},
            )

            return "".join(response) if isinstance(response, list) else str(response)

        except Exception as e:
            logger.error(f"Cover letter tips generation failed: {e}")
            return f"Error generating tips: {str(e)}"
