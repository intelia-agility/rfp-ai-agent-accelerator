from .llm_client import LLMClient

class RFPAnalyzer:
    def __init__(self):
        self.llm = LLMClient()

    def analyze_rfp(self, rfp_text: str):
        prompt = f"""
        You are an expert Sales Solution Architect. Analyze the following RFP text and provide a qualification score (0-100) and recommendation (Pursue/No Pursue).
        
        Evaluate based on these criteria:
        1. Business strategy and priorities
        2. Core offerings and differentiators match
        3. Resource availability and delivery capacity (Assume standard availability if not specified)
        4. Risk, compliance, and financial considerations

        RFP Text Excerpt:
        {rfp_text[:4000]}... (truncated)

        Output as valid JSON:
        {{
            "score": <number>,
            "recommendation": "<Pursue/No Pursue>",
            "criteria_scores": {{
                "strategy": <score>,
                "offerings": <score>,
                "resources": <score>,
                "risks": <score>
            }},
            "reasoning": "<Summary>"
        }}
        """
        # In a real app, we would parse the JSON response.
        # For now, returning mock or raw text.
        # response = self.llm.generate_content(prompt)
        # return response
        
        # Mock response for prototype speed/stability without real api key
        return {
            "score": 88,
            "recommendation": "Pursue",
            "criteria_scores": {
                "strategy": 90,
                "offerings": 95,
                "resources": 80,
                "risks": 85
            },
            "reasoning": "Strong alignment with core offerings. Compliance risks are manageable."
        }
