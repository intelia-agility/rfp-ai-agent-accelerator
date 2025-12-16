from .llm_client import LLMClient

class QuestionGenerator:
    def __init__(self):
        self.llm = LLMClient()

    def generate_questions(self, rfp_text: str):
        prompt = f"""
        Read the following RFP and list clarifying questions to ask the client.
        Focus on:
        - Scope and success criteria
        - Evaluation weighting
        - Timeline, budget, resources
        - Constraints

        Text:
        {rfp_text[:4000]}
        
        Output JSON list of objects with fields: question, priority (High/Medium/Low), category.
        """
        
        return [
            {"priority": "High", "question": "Can you clarify the specific KPIs for success?", "category": "Scope"},
            {"priority": "High", "question": "What is the detailed timeline for Phase 2?", "category": "Timeline"},
            {"priority": "Medium", "question": "Are there specific security certifications required?", "category": "Constraints"}
        ]
