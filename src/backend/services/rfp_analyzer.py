from .llm_client import LLMClient

class RFPAnalyzer:
    def __init__(self):
        self.llm = LLMClient()

    def analyze_rfp(self, rfp_text: str):
        # Mock response for prototype
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
