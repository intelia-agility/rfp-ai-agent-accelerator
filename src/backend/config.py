import os
from dotenv import load_dotenv
from services.secret_manager import get_secret

load_dotenv()

class Settings:
    PROJECT_NAME = "RFP AI Agent Accelerator"
    VERSION = "1.0.0"
    
    # GCP
    GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID", "rfp-accelerator-agent")
    GCP_LOCATION = os.getenv("GCP_LOCATION", "us-central1")
    
    # SharePoint
    SHAREPOINT_URL = os.getenv("SHAREPOINT_URL") or get_secret("SHAREPOINT_URL")
    SHAREPOINT_CLIENT_ID = os.getenv("SHAREPOINT_CLIENT_ID") or get_secret("SHAREPOINT_CLIENT_ID")
    SHAREPOINT_CLIENT_SECRET = os.getenv("SHAREPOINT_CLIENT_SECRET") or get_secret("SHAREPOINT_CLIENT_SECRET")
    SHAREPOINT_DOC_LIB = os.getenv("SHAREPOINT_DOC_LIB", "Shared Documents")

settings = Settings()
