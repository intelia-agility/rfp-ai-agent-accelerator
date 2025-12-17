# Quick Deploy Commands for RFP Backend

# Set your project ID first
$env:GCP_PROJECT_ID = "your-project-id-here"
$env:GCP_LOCATION = "australia-southeast2"

# Quick deploy (builds from source)
gcloud run deploy rfp-backend `
    --source . `
    --platform managed `
    --region $env:GCP_LOCATION `
    --allow-unauthenticated `
    --port 8080 `
    --timeout 300 `
    --memory 2Gi `
    --cpu 2 `
    --min-instances 0 `
    --max-instances 10 `
    --set-env-vars "GCP_PROJECT_ID=$env:GCP_PROJECT_ID,GCP_LOCATION=$env:GCP_LOCATION"

# Get service URL
$SERVICE_URL = gcloud run services describe rfp-backend --region $env:GCP_LOCATION --format 'value(status.url)'
Write-Host "Service URL: $SERVICE_URL"

# Test health endpoint
Invoke-WebRequest -Uri "$SERVICE_URL/health"

# View logs
gcloud run services logs read rfp-backend --region $env:GCP_LOCATION --limit 50
