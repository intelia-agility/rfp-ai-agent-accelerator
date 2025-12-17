# Cloud Run Deployment Guide

## Issue Fixed

The Cloud Run deployment was failing with the error:
> "The user-provided container failed to start and listen on the port defined provided by the PORT=8080 environment variable"

### Root Causes Identified and Fixed:

1. **Missing Vertex AI Initialization** - The `LLMClient` was trying to use `GenerativeModel` without calling `vertexai.init()` first, causing startup failures.
2. **Blocking Service Initialization** - Services were initialized at module level, which could block container startup if credentials weren't available.
3. **Missing Health Check Endpoint** - Cloud Run needs a quick-responding health check endpoint.
4. **Port Configuration Issues** - The PORT environment variable wasn't properly handled in the Dockerfile.

### Changes Made:

1. **`main.py`**:
   - Added lazy service initialization with `@app.on_event("startup")`
   - Added `/health` endpoint for Cloud Run health checks
   - Improved error handling to allow app to start even if some services fail

2. **`services/llm_client.py`**:
   - Added proper `vertexai.init()` call with project configuration
   - Added comprehensive error handling
   - Changed model to `gemini-1.5-flash` (more reliable)

3. **`Dockerfile`**:
   - Set default PORT=8080
   - Fixed PORT variable syntax to `${PORT}`
   - Added timeout configuration

4. **`.dockerignore`**:
   - Created to exclude unnecessary files from Docker build
   - Reduces image size and build time

## Deployment Instructions

### Prerequisites

1. **GCP Project Setup**:
   ```bash
   export GCP_PROJECT_ID="your-project-id"
   export GCP_LOCATION="australia-southeast2"  # or your preferred region
   ```

2. **Enable Required APIs**:
   ```bash
   gcloud services enable cloudbuild.googleapis.com
   gcloud services enable run.googleapis.com
   gcloud services enable aiplatform.googleapis.com
   ```

3. **Service Account** (if using Google Drive):
   ```bash
   # Create service account
   gcloud iam service-accounts create rfp-backend-sa \
       --display-name="RFP Backend Service Account"
   
   # Grant necessary permissions
   gcloud projects add-iam-policy-binding ${GCP_PROJECT_ID} \
       --member="serviceAccount:rfp-backend-sa@${GCP_PROJECT_ID}.iam.gserviceaccount.com" \
       --role="roles/aiplatform.user"
   
   # Create and download key
   gcloud iam service-accounts keys create key.json \
       --iam-account=rfp-backend-sa@${GCP_PROJECT_ID}.iam.gserviceaccount.com
   ```

### Option 1: Deploy Using gcloud CLI (Recommended)

```bash
# Navigate to backend directory
cd src/backend

# Build and deploy in one command
gcloud run deploy rfp-backend \
    --source . \
    --platform managed \
    --region ${GCP_LOCATION} \
    --allow-unauthenticated \
    --port 8080 \
    --timeout 300 \
    --memory 2Gi \
    --cpu 2 \
    --min-instances 0 \
    --max-instances 10 \
    --set-env-vars "GCP_PROJECT_ID=${GCP_PROJECT_ID},GCP_LOCATION=${GCP_LOCATION}"
```

### Option 2: Deploy Using the Deployment Script

```bash
cd src/backend
chmod +x deploy.sh
./deploy.sh
```

### Option 3: Manual Build and Deploy

```bash
# Build the container
gcloud builds submit --tag gcr.io/${GCP_PROJECT_ID}/rfp-backend

# Deploy to Cloud Run
gcloud run deploy rfp-backend \
    --image gcr.io/${GCP_PROJECT_ID}/rfp-backend \
    --platform managed \
    --region ${GCP_LOCATION} \
    --allow-unauthenticated \
    --port 8080 \
    --timeout 300 \
    --memory 2Gi \
    --cpu 2 \
    --set-env-vars "GCP_PROJECT_ID=${GCP_PROJECT_ID},GCP_LOCATION=${GCP_LOCATION}"
```

## Environment Variables

The following environment variables are required:

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `GCP_PROJECT_ID` | Your GCP Project ID | Yes | - |
| `GCP_LOCATION` | GCP region for Vertex AI | No | australia-southeast2 |
| `GOOGLE_APPLICATION_CREDENTIALS` | Path or JSON content of service account key | No (uses default) | - |
| `PORT` | Port for the service to listen on | No | 8080 |

### Setting Environment Variables in Cloud Run

```bash
gcloud run services update rfp-backend \
    --region ${GCP_LOCATION} \
    --set-env-vars "GCP_PROJECT_ID=${GCP_PROJECT_ID},GCP_LOCATION=${GCP_LOCATION}"
```

### Adding Google Drive Credentials

If you need Google Drive integration:

```bash
# Option 1: Use Secret Manager (Recommended)
gcloud secrets create google-drive-credentials \
    --data-file=key.json

gcloud run services update rfp-backend \
    --region ${GCP_LOCATION} \
    --update-secrets=GOOGLE_APPLICATION_CREDENTIALS=google-drive-credentials:latest

# Option 2: Set as environment variable (less secure)
gcloud run services update rfp-backend \
    --region ${GCP_LOCATION} \
    --set-env-vars "GOOGLE_APPLICATION_CREDENTIALS=$(cat key.json)"
```

### Google Drive Folder Structure

The application expects the following folder structure in the Service Account's Google Drive (or shared with it):

- **RFP AI Agent** (Parent Folder)
  - **Source Information** (Folder for knowledge base/supporting documents)
  - **RFP Output** (Folder where draft responses will be saved)

The application will automatically discover these folders by name (or use the hardcoded default ID for the parent folder). Ensure the Service Account has **Editor** access to the parent folder.

## Testing the Deployment

### 1. Health Check
```bash
SERVICE_URL=$(gcloud run services describe rfp-backend --region ${GCP_LOCATION} --format 'value(status.url)')
curl ${SERVICE_URL}/health
```

Expected response:
```json
{"status": "healthy", "service": "rfp-backend"}
```

### 2. Root Endpoint
```bash
curl ${SERVICE_URL}/
```

Expected response:
```json
{"message": "RFP AI Agent Accelerator API is running", "status": "healthy"}
```

### 3. Test File Upload (Assess Endpoint)
```bash
curl -X POST ${SERVICE_URL}/assess \
    -F "file=@sample.pdf"
```

## Troubleshooting

### Check Logs
```bash
gcloud run services logs read rfp-backend --region ${GCP_LOCATION} --limit 50
```

### Common Issues

1. **"Container failed to start"**
   - Check logs for initialization errors
   - Verify environment variables are set correctly
   - Ensure service account has proper permissions

2. **"Vertex AI initialization failed"**
   - Verify `GCP_PROJECT_ID` is set
   - Ensure Vertex AI API is enabled
   - Check service account has `roles/aiplatform.user` role

3. **"Google Drive not available"**
   - This is expected if credentials aren't provided
   - The app will still start and work for other features
   - Add credentials using Secret Manager if needed

4. **Timeout errors**
   - Increase timeout: `--timeout 600`
   - Increase memory: `--memory 4Gi`
   - Check if cold start is causing issues

### View Service Details
```bash
gcloud run services describe rfp-backend --region ${GCP_LOCATION}
```

### Update Service Configuration
```bash
# Increase timeout
gcloud run services update rfp-backend \
    --region ${GCP_LOCATION} \
    --timeout 600

# Increase memory
gcloud run services update rfp-backend \
    --region ${GCP_LOCATION} \
    --memory 4Gi

# Set minimum instances (reduce cold starts)
gcloud run services update rfp-backend \
    --region ${GCP_LOCATION} \
    --min-instances 1
```

## Monitoring

### View Metrics
```bash
# In GCP Console
https://console.cloud.google.com/run/detail/${GCP_LOCATION}/rfp-backend/metrics
```

### Set Up Alerts
```bash
# Create alert for high error rate
gcloud alpha monitoring policies create \
    --notification-channels=CHANNEL_ID \
    --display-name="RFP Backend High Error Rate" \
    --condition-display-name="Error rate > 5%" \
    --condition-threshold-value=5 \
    --condition-threshold-duration=60s
```

## Rollback

If you need to rollback to a previous version:

```bash
# List revisions
gcloud run revisions list --service rfp-backend --region ${GCP_LOCATION}

# Rollback to specific revision
gcloud run services update-traffic rfp-backend \
    --region ${GCP_LOCATION} \
    --to-revisions REVISION_NAME=100
```

## Clean Up

To delete the service:

```bash
gcloud run services delete rfp-backend --region ${GCP_LOCATION}
```

## Next Steps

1. Set up CI/CD pipeline for automated deployments
2. Configure custom domain
3. Set up monitoring and alerting
4. Implement authentication if needed
5. Configure VPC connector for private resources
