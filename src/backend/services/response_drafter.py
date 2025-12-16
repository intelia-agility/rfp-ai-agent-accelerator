from .llm_client import LLMClient
from .web_scraper import WebScraper

class ResponseDrafter:
    def __init__(self):
        self.llm = LLMClient()
        self.scraper = WebScraper()

    def draft_response(self, rfp_text: str, company_url: str = "") -> str:
        website_content = ""
        if company_url:
            website_content = self.scraper.get_website_content(company_url)

        context_section = ""
        if website_content:
            context_section = f"""
            COMPANY KNOWLEDGE BASE (from website {company_url}):
            {website_content}
            """

        prompt = f"""
        You are an expert Proposal Writer. Draft a professional and persuasive response to the following RFP requirement, utilizing the company's knowledge base.

        {context_section}

        RFP REQUIREMENT/TEXT:
        {rfp_text[:5000]}

        INSTRUCTIONS:
        1. Write a response that directly addresses the requirements.
        2. Use a professional, confident tone.
        3. Highlight the company's strengths based on the knowledge base.
        4. If specific details are missing in the knowledge base, use placeholders like [Insert specific metric].

        RESPONSE:
        """
        
        # Call LLM
        # response = self.llm.generate_content(prompt)
        # return response

        # Mocking for speed/testing if LLM isn't fully configured with quota
        if not company_url:
            return "Please provide a company URL to generate a tailored response."
            
        return f"Based on your website ({company_url}), here is a draft response:\n\n" \
               f"Our company is uniquely positioned to deliver this project given our expertise in {website_content[:50]}...\n\n" \
               f"We understand your requirements for {rfp_text[:50]}... and propose a solution that..."

