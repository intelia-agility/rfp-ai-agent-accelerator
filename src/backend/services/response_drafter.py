from .llm_client import LLMClient
from .web_scraper import WebScraper
from .google_drive_client import GoogleDriveClient
import os
import re
try:
    from docx import Document
except ImportError:
    Document = None

class ResponseDrafter:
    def __init__(self):
        self.llm = LLMClient()
        self.scraper = WebScraper()
        self.drive_client = GoogleDriveClient()

    def draft_response(self, rfp_text: str, company_url: str = "") -> str:
        website_content = ""
        if company_url:
            website_content = self.scraper.get_website_content(company_url)

        # Get past RFP responses from Google Drive
        past_rfps = []
        try:
            past_rfps = self.drive_client.get_all_rfp_documents()
        except Exception as e:
            print(f"Could not fetch Google Drive documents: {e}")

        # Build context from past RFPs
        past_rfp_context = ""
        if past_rfps:
            past_rfp_context = "\n\nPAST RFP RESPONSES (for reference):\n"
            for doc in past_rfps[:3]:  # Limit to 3 most recent for token efficiency
                past_rfp_context += f"\n--- {doc['name']} ---\n{doc['content'][:1000]}...\n"

        context_section = ""
        if website_content:
            context_section = f"""
            COMPANY KNOWLEDGE BASE (from website {company_url}):
            {website_content}
            """

        prompt = f"""
        You are an expert Proposal Writer. Draft a professional and persuasive response to the following RFP requirement, utilizing the company's knowledge base and past successful RFP responses.

        {context_section}
        {past_rfp_context}

        RFP REQUIREMENT/TEXT:
        {rfp_text[:5000]}

        INSTRUCTIONS:
        1. Write a response that directly addresses the requirements.
        2. Use a professional, confident tone.
        3. Highlight the company's strengths based on the knowledge base.
        4. Learn from the style and content of past successful RFP responses.
        5. If specific details are missing in the knowledge base, use placeholders like [Insert specific metric].

        RESPONSE:
        """
        
        # Call LLM
        # response = self.llm.generate_content(prompt)
        # return response

        # Mocking for speed/testing if LLM isn't fully configured with quota
        if not company_url:
            return "Please provide a company URL to generate a tailored response."
            
        return f"Based on your website ({company_url}) and {len(past_rfps)} past RFP responses, here is a draft response:\n\n" \
               f"Our company is uniquely positioned to deliver this project given our expertise in {website_content[:50]}...\n\n" \
               f"We understand your requirements for {rfp_text[:50]}... and propose a solution that..."

    def generate_draft_document(self, content: str, input_path: str, output_path: str, company_url: str = ""):
        """
        Finds and replaces placeholder text in the document with AI-generated content.
        """
        if not Document or not input_path.endswith('.docx') or not os.path.exists(input_path):
            return None
            
        try:
            doc = Document(input_path)
            
            # Get company context
            website_content = ""
            if company_url:
                website_content = self.scraper.get_website_content(company_url)
            
            # Find all placeholders in the document
            placeholders = set()
            placeholder_pattern = r'\[([^\]]+)\]'
            
            for paragraph in doc.paragraphs:
                matches = re.findall(placeholder_pattern, paragraph.text)
                placeholders.update(matches)
            
            for table in doc.tables:
                for row in table.rows:
                    for cell in row.cells:
                        for paragraph in cell.paragraphs:
                            matches = re.findall(placeholder_pattern, paragraph.text)
                            placeholders.update(matches)
            
            # Generate replacements for each placeholder
            replacements = {}
            for placeholder in placeholders:
                replacement = self._generate_placeholder_content(placeholder, website_content, company_url)
                replacements[f"[{placeholder}]"] = replacement
            
            # Replace placeholders in paragraphs
            for paragraph in doc.paragraphs:
                for placeholder, replacement in replacements.items():
                    if placeholder in paragraph.text:
                        paragraph.text = paragraph.text.replace(placeholder, replacement)
            
            # Replace placeholders in tables
            for table in doc.tables:
                for row in table.rows:
                    for cell in row.cells:
                        for paragraph in cell.paragraphs:
                            for placeholder, replacement in replacements.items():
                                if placeholder in paragraph.text:
                                    paragraph.text = paragraph.text.replace(placeholder, replacement)
            
            doc.save(output_path)
            return output_path
            
        except Exception as e:
            print(f"Error modifying docx: {e}")
            return None
    
    def _generate_placeholder_content(self, placeholder: str, website_content: str, company_url: str) -> str:
        """
        Generate appropriate content for a specific placeholder based on its name and company context.
        """
        placeholder_lower = placeholder.lower()
        
        # Common placeholder mappings
        if 'trading name' in placeholder_lower or 'company name' in placeholder_lower:
            # Extract company name from URL or website
            if company_url:
                domain = company_url.replace('https://', '').replace('http://', '').replace('www.', '').split('/')[0]
                return domain.split('.')[0].capitalize()
            return "[Company Name]"
        
        elif 'abn' in placeholder_lower or 'acn' in placeholder_lower:
            return "[ABN/ACN Number]"
        
        elif 'address' in placeholder_lower:
            return "[Company Address]"
        
        elif 'phone' in placeholder_lower or 'contact' in placeholder_lower:
            return "[Contact Number]"
        
        elif 'email' in placeholder_lower:
            return "[Email Address]"
        
        elif 'experience' in placeholder_lower or 'capability' in placeholder_lower:
            if website_content:
                return f"With extensive experience in delivering innovative solutions, our team specializes in {website_content[:100]}..."
            return "[Company Experience and Capabilities]"
        
        elif 'detail' in placeholder_lower or 'description' in placeholder_lower:
            if website_content:
                return f"Our approach leverages {website_content[:80]}... to deliver exceptional outcomes."
            return "[Detailed Description]"
        
        else:
            # Generic replacement based on context
            if website_content:
                return f"[Based on our expertise: {website_content[:60]}...]"
            return f"[{placeholder}]"



