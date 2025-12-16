from .llm_client import LLMClient
from .web_scraper import WebScraper
from .google_drive_client import GoogleDriveClient

class QuestionGenerator:
    def __init__(self):
        self.llm = LLMClient()
        self.scraper = WebScraper()
        self.drive_client = GoogleDriveClient()

    def generate_questions(self, rfp_text: str, company_url: str = ""):
        website_content = ""
        if company_url:
            website_content = self.scraper.get_website_content(company_url)

        # Get past RFP documents for reference
        past_rfps = []
        try:
            past_rfps = self.drive_client.get_all_rfp_documents()
        except Exception as e:
            print(f"Could not fetch Google Drive documents: {e}")

        past_rfp_context = ""
        if past_rfps:
            past_rfp_context = "\n\nPAST RFP QUESTIONS (for reference):\n"
            for doc in past_rfps[:2]:
                past_rfp_context += f"\n--- {doc['name']} ---\n{doc['content'][:800]}...\n"

        context_section = ""
        if website_content:
            context_section = f"""
            MY COMPANY CONTEXT (from {company_url}):
            {website_content}
            """

        prompt = f"""
        Act as a Bid Manager. Read the following RFP and my company's background. 
        Generate intelligent clarifying questions to ask the client.
        
        {context_section}
        {past_rfp_context}

        RFP TEXT:
        {rfp_text[:4000]}
        
        Guidelines:
        - Identify ambiguous requirements.
        - Ask questions that highlight our specific strengths (found in the context).
        - Clarify constraints (timeline, budget).
        - Learn from the types of questions asked in past successful RFPs.
        
        Output JSON list of objects with fields: question, priority (High/Medium/Low), category, rationale.
        """
        
        # Mocking for prototype
        if not company_url:
             return [
                {"priority": "High", "question": "Can you clarify the specific KPIs for success?", "category": "Scope", "rationale": "KPIs are not defined."},
                {"priority": "High", "question": "What is the detailed timeline for Phase 2?", "category": "Timeline", "rationale": "Phase 2 dates are missing."},
            ]

        return [
            {"priority": "High", "question": "Can you clarify the specific KPIs for success?", "category": "Scope", "rationale": "KPIs are not defined."},
            {"priority": "High", "question": f"Given our expertise in cloud migration (as seen on our site) and {len(past_rfps)} past projects, are you open to a hybrid approach?", "category": "Technical", "rationale": "Leverages our specific cloud strengths."},
            {"priority": "Medium", "question": "Are there specific security certifications required?", "category": "Constraints", "rationale": "Compliance check needed."}
        ]


