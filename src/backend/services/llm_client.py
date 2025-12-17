import vertexai
from vertexai.generative_models import GenerativeModel, Part
import os
import logging

logger = logging.getLogger(__name__)

class LLMClient:
    def __init__(self):
        """Initialize Vertex AI and the Gemini model with proper error handling."""
        self.model = None
        try:
            # Get GCP configuration from environment
            project_id = os.getenv("GCP_PROJECT_ID")
            location = os.getenv("GCP_LOCATION", "us-central1")
            
            if not project_id:
                logger.warning("GCP_PROJECT_ID not set - LLM client may not work properly")
                # Try to initialize anyway, it might work with default credentials
            
            # Initialize Vertex AI
            vertexai.init(project=project_id, location=location)
            
            # Initialize the model
            self.model = GenerativeModel("gemini-1.5-flash")
            logger.info("LLM Client initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing LLM client: {e}")
            # Don't raise - allow the app to start even if LLM isn't available

    def generate_content(self, prompt: str) -> str:
        """Generate content using the Gemini model."""
        if not self.model:
            logger.error("LLM model not initialized")
            return "Error: LLM service not available."
            
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Error generating content: {e}")
            return f"Error generating content: {str(e)}"

