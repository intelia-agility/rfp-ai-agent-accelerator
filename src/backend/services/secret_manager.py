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
        project_id = os.getenv("GCP_PROJECT_ID", "rfp-accelerator-agent")
    
    if not project_id:
        logger.warning(f"GCP_PROJECT_ID not set, cannot fetch secret {secret_id}")
        return None

    try:
        client = secretmanager.SecretManagerServiceClient()
        name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
        response = client.access_secret_version(request={"name": name})
        return response.payload.data.decode("UTF-8")
    except Exception as e:
        logger.warning(f"Could not fetch secret {secret_id} from Secret Manager: {e}")
        return None
