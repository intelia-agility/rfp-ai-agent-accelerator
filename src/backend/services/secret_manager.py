import os
import logging
from google.cloud import secretmanager
from google.auth.exceptions import DefaultCredentialsError

logger = logging.getLogger(__name__)

def get_secret(secret_id, project_id=None):
    """
    Get secret from Google Secret Manager.
    """
    if not project_id:
        project_id = os.getenv("GCP_PROJECT_ID") or os.getenv("GOOGLE_CLOUD_PROJECT") or "rfp-accelerator-agent"
    
    logger.info(f"Fetching secret '{secret_id}' from project '{project_id}'")

    try:
        client = secretmanager.SecretManagerServiceClient()
        name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
        response = client.access_secret_version(request={"name": name})
        secret_value = response.payload.data.decode("UTF-8")
        logger.info(f"Successfully retrieved secret '{secret_id}'")
        return secret_value
    except Exception as e:
        logger.warning(f"Could not fetch secret '{secret_id}' from Secret Manager in project '{project_id}': {e}")
        # Log specific error for debugging without revealing secret content
        if "PermissionDenied" in str(e):
            logger.error(f"Permission denied while accessing secret '{secret_id}'. Check service account roles.")
        elif "NotFound" in str(e):
            logger.error(f"Secret '{secret_id}' not found in project '{project_id}'.")
        return None
