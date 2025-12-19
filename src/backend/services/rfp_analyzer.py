from .llm_client import LLMClient

class RFPAnalyzer:
    def __init__(self):
        self.llm = LLMClient()

    def analyze_rfp(self, rfp_text: str):
        prompt = f"""
        Analyze the following RFP document text and provide a evaluation in JSON format.
        
        RFP TEXT:
        {rfp_text[:10000]}
        
        EVALUATE AGAINST:
        1. Business strategy and alignment.
        2. Core offerings fit.
        3. Resource availability.
        4. Risk and compliance.
        
        RETURN JSON ONLY:
        {{
            "score": (integer 0-100),
            "recommendation": "Pursue" or "No-Pursue",
            "criteria_scores": {{
                "strategy": (0-100),
                "offerings": (0-100),
                "resources": (0-100),
                "risks": (0-100)
            }},
            "reasoning": "Brief explanation of the score"
        }}
        """
        try:
            import json
            import re
            response = self.llm.generate_content(prompt)
            # Extract JSON
            json_match = re.search(r'(\{.*\})', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1))
            return {"error": "Failed to parse analysis results"}
        except Exception as e:
            return {"error": f"Analysis failed: {str(e)}"}
