import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    PROJECT_NAME = "RFP AI Agent Accelerator"
    VERSION = "1.0.0"
    
    # GCP
    GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID")
    GCP_LOCATION = os.getenv("GCP_LOCATION", "australia-southeast2")
    
    # SharePoint
    SHAREPOINT_URL = os.getenv("SHAREPOINT_URL")
    SHAREPOINT_CLIENT_ID = os.getenv("SHAREPOINT_CLIENT_ID")
    SHAREPOINT_CLIENT_SECRET = os.getenv("SHAREPOINT_CLIENT_SECRET")
    SHAREPOINT_DOC_LIB = os.getenv("SHAREPOINT_DOC_LIB", "Shared Documents")

settings = Settings()
