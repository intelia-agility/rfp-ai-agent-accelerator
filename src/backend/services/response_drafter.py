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
        """
        Draft a response using company website and source documents from Google Drive.
        """
        website_content = ""
        if company_url:
            website_content = self.scraper.get_website_content(company_url)

        # Get supporting documents from Google Drive Source Information folder
        source_documents = []
        try:
            source_documents = self.drive_client.get_all_rfp_documents()
        except Exception as e:
            print(f"Could not fetch Google Drive source documents: {e}")

        # Build context from source documents
        source_context = ""
        if source_documents:
            source_context = "\n\nSOURCE INFORMATION (from Google Drive):\n"
            for doc in source_documents:
                # Include full content of source documents for better context
                source_context += f"\n--- {doc['name']} ---\n{doc['content']}\n"

        context_section = ""
        if website_content:
            context_section = f"""
            COMPANY KNOWLEDGE BASE (from website {company_url}):
            {website_content}
            """

        prompt = f"""
        You are an expert Proposal Writer. Draft a professional and persuasive response to the following RFP requirement, 
        utilizing the company's knowledge base and source information documents.

        {context_section}
        {source_context}

        RFP REQUIREMENT/TEXT:
        {rfp_text[:5000]}

        INSTRUCTIONS:
        1. Write a response that directly addresses the requirements.
        2. Use information from the source documents to provide specific, accurate details.
        3. Use a professional, confident tone.
        4. Highlight the company's strengths based on the knowledge base and source documents.
        5. If specific details are missing, use descriptive placeholders like [Insert specific metric].
        6. Ensure the response is comprehensive and well-structured.

        RESPONSE:
        """
        
        # Call LLM to generate response
        try:
            response = self.llm.generate_content(prompt)
            return response
        except Exception as e:
            print(f"Error generating LLM response: {e}")
            # Fallback response
            if not source_documents and not company_url:
                return "Please provide a company URL or ensure source documents are available in Google Drive to generate a tailored response."
                
            return f"Based on {len(source_documents)} source documents from Google Drive and website content, here is a draft response:\n\n" \
                   f"Our company is uniquely positioned to deliver this project. We have extensive experience and capabilities " \
                   f"as documented in our source materials. We understand your requirements and propose a comprehensive solution..."

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
            
            # Get source documents from Google Drive
            source_documents = []
            try:
                source_documents = self.drive_client.get_all_rfp_documents()
            except Exception as e:
                print(f"Could not fetch source documents: {e}")
            
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
            
            # Generate replacements for each placeholder using source documents
            replacements = {}
            for placeholder in placeholders:
                replacement = self._generate_placeholder_content(
                    placeholder, 
                    website_content, 
                    company_url,
                    source_documents
                )
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
    
    def _generate_placeholder_content(self, placeholder: str, website_content: str, company_url: str, source_documents: list = None) -> str:
        """
        Generate appropriate content for a specific placeholder based on its name, 
        company context, and source documents from Google Drive.
        """
        if source_documents is None:
            source_documents = []
            
        placeholder_lower = placeholder.lower()
        
        # Search source documents for relevant information
        def search_source_docs(keywords):
            """Search source documents for content matching keywords."""
            for doc in source_documents:
                content_lower = doc['content'].lower()
                if any(keyword in content_lower for keyword in keywords):
                    # Return a relevant excerpt
                    for keyword in keywords:
                        if keyword in content_lower:
                            idx = content_lower.find(keyword)
                            # Get context around the keyword
                            start = max(0, idx - 100)
                            end = min(len(doc['content']), idx + 200)
                            return doc['content'][start:end].strip()
            return None
        
        # Common placeholder mappings with source document search
        if 'trading name' in placeholder_lower or 'company name' in placeholder_lower:
            # Search source docs for company name
            company_info = search_source_docs(['company name', 'trading name', 'business name'])
            if company_info:
                return company_info
            # Extract company name from URL or website
            if company_url:
                domain = company_url.replace('https://', '').replace('http://', '').replace('www.', '').split('/')[0]
                return domain.split('.')[0].capitalize()
            return "[Company Name]"
        
        elif 'abn' in placeholder_lower or 'acn' in placeholder_lower:
            # Search for ABN/ACN in source documents
            abn_info = search_source_docs(['abn', 'acn', 'australian business number'])
            if abn_info:
                return abn_info
            return "[ABN/ACN Number]"
        
        elif 'address' in placeholder_lower:
            # Search for address in source documents
            address_info = search_source_docs(['address', 'location', 'office'])
            if address_info:
                return address_info
            return "[Company Address]"
        
        elif 'phone' in placeholder_lower or 'contact' in placeholder_lower:
            # Search for contact info
            contact_info = search_source_docs(['phone', 'contact', 'telephone', 'mobile'])
            if contact_info:
                return contact_info
            return "[Contact Number]"
        
        elif 'email' in placeholder_lower:
            # Search for email
            email_info = search_source_docs(['email', '@', 'contact'])
            if email_info:
                return email_info
            return "[Email Address]"
        
        elif 'experience' in placeholder_lower or 'capability' in placeholder_lower:
            # Search source docs for experience/capability info
            exp_info = search_source_docs(['experience', 'capability', 'expertise', 'track record'])
            if exp_info:
                return exp_info
            if website_content:
                return f"With extensive experience in delivering innovative solutions, our team specializes in {website_content[:100]}..."
            return "[Company Experience and Capabilities]"
        
        elif 'detail' in placeholder_lower or 'description' in placeholder_lower:
            # Search for relevant details
            detail_info = search_source_docs(['description', 'details', 'overview'])
            if detail_info:
                return detail_info
            if website_content:
                return f"Our approach leverages {website_content[:80]}... to deliver exceptional outcomes."
            return "[Detailed Description]"
        
        else:
            # Generic replacement - try to find relevant content from source docs
            keywords = placeholder_lower.split()
            generic_info = search_source_docs(keywords)
            if generic_info:
                return generic_info
            
            # Use LLM to generate content if we have source documents
            if source_documents and len(source_documents) > 0:
                try:
                    # Build context from source documents
                    context = "\n".join([f"{doc['name']}: {doc['content'][:500]}" for doc in source_documents[:3]])
                    prompt = f"""Based on the following source documents, provide appropriate content for the placeholder "{placeholder}":
                    
                    SOURCE DOCUMENTS:
                    {context}
                    
                    Provide a concise, professional response (2-3 sentences maximum) that would be appropriate for this placeholder in an RFP response.
                    """
                    response = self.llm.generate_content(prompt)
                    if response and len(response) > 10:
                        return response.strip()
                except Exception as e:
                    print(f"Error using LLM for placeholder: {e}")
            
            # Fallback
            if website_content:
                return f"[Based on our expertise: {website_content[:60]}...]"
            return f"[{placeholder}]"



