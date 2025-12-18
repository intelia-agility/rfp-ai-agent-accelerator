# Security Best Practices

## Credentials Management

### ⚠️ IMPORTANT: Never commit credentials to Git!

All sensitive credentials are stored in **Google Cloud Secret Manager** and are NOT in this repository.

### Google Drive Credentials

The application uses a service account to access Google Drive. The credentials are:

1. **Stored in**: Google Cloud Secret Manager
   - Secret name: `google-drive-credentials`
   - Project: `rfp-accelerator-agent`

2. **Accessed by**: Cloud Run services via mounted secrets
   - Backend mounts the secret at `/secrets/key.json`
   - Environment variable `GOOGLE_APPLICATION_CREDENTIALS` points to this path

### How to Update Credentials

If you need to update the Google Drive service account credentials:

```bash
# 1. Create/update the secret in Secret Manager
gcloud secrets create google-drive-credentials \
    --data-file=path/to/your/new-credentials.json \
    --project=rfp-accelerator-agent

# Or update existing secret:
gcloud secrets versions add google-drive-credentials \
    --data-file=path/to/your/new-credentials.json \
    --project=rfp-accelerator-agent

# 2. Redeploy the backend to use the new credentials
# (The deploy script automatically mounts the latest version)
./deploy_gcp.ps1
```

### Local Development

For local development, you can:

1. Download credentials from Secret Manager:
```bash
gcloud secrets versions access latest \
    --secret=google-drive-credentials \
    --project=rfp-accelerator-agent > drive-credentials.json
```

2. Set the environment variable:
```bash
export GOOGLE_APPLICATION_CREDENTIALS=./drive-credentials.json
```

**Remember**: The `drive-credentials.json` file is in `.gitignore` and will NOT be committed to Git.

### Service Account Permissions

The service account `rfp-drive-reader@rfp-accelerator-agent.iam.gserviceaccount.com` has:
- **Google Drive**: Editor access to the "RFP AI Agent" shared folder
- **Vertex AI**: `roles/aiplatform.user` for Gemini API access

## Other Secrets

All other sensitive information (API keys, tokens, etc.) should also be stored in Secret Manager, never in code or Git.
