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
            # Force us-central1 for Model Availability reliability
            # australia-southeast2 may not support all Gemini 1.5 features
            location = os.getenv("GCP_LOCATION", "us-central1")
            
            if not project_id:
                logger.warning("GCP_PROJECT_ID not set - LLM client may not work properly")
                # Try to initialize anyway, it might work with default credentials
            
            # Initialize Vertex AI
            vertexai.init(project=project_id, location=location)
            
            # Initialize the model
            from vertexai.generative_models import HarmCategory, HarmBlockThreshold
            self.safety_settings = {
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_ONLY_HIGH,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
            }
            self.model = GenerativeModel("gemini-2.5-flash")
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
            logger.info(f"Sending request to LLM. Prompt length: {len(prompt)} chars")
            # Log first 100 chars to verify content
            logger.info(f"Prompt preview: {prompt[:100]}...")
            
            response = self.model.generate_content(
                prompt,
                generation_config={
                    "temperature": 0.2,
                    "max_output_tokens": 8192,
                },
                safety_settings=self.safety_settings
            )
            return response.text
        except Exception as e:
            logger.error(f"Error generating content: {e}")
            # If it's a 400/403, try to extract more details
            if hasattr(e, 'message'):
                logger.error(f"Error details: {e.message}")
            return f"Error generating content: {str(e)}"

