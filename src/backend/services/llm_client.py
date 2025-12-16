import vertexai
from vertexai.generative_models import GenerativeModel, Part
import os

# Initialize Vertex AI
# Ensure you have set GOOGLE_APPLICATION_CREDENTIALS or have run gcloud auth application-default login
# PROJECT_ID = os.getenv("GCP_PROJECT_ID")
# LOCATION = os.getenv("GCP_LOCATION", "us-central1")

# vertexai.init(project=PROJECT_ID, location=LOCATION)

class LLMClient:
    def __init__(self):
        self.model = GenerativeModel("gemini-pro")

    def generate_content(self, prompt: str) -> str:
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"Error generating content: {e}")
            return "Error generating content."
