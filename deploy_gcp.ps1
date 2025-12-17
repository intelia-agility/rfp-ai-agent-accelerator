
# Deployment Script for RFP AI Agent Accelerator
# Requirements: Google Cloud SDK (gcloud) installed and authenticated.

$ErrorActionPreference = "Stop"

$REGION = "australia-southeast2"
$BACKEND_SERVICE_NAME = "rfp-backend"
$FRONTEND_SERVICE_NAME = "rfp-frontend"

Write-Host "Checking for gcloud CLI..."
if (-not (Get-Command gcloud.cmd -ErrorAction SilentlyContinue)) {
    Write-Error "Error: 'gcloud.cmd' command not found. Please install the Google Cloud SDK and ensure it's in your PATH."
    exit 1
}

Write-Host "Enabling necessary APIs..."
gcloud.cmd services enable run.googleapis.com artifactregistry.googleapis.com cloudbuild.googleapis.com
if ($LASTEXITCODE -ne 0) { Write-Error "Failed to enable APIs"; exit 1 }

Write-Host "Deploying Backend..."
cd src/backend
# Deploy source directly (Cloud Build will build the Dockerfile)
# Added --memory 2Gi to prevent build/runtime memory issues
# Added --update-secrets to mount Google Drive credentials
gcloud.cmd run deploy $BACKEND_SERVICE_NAME --source . --allow-unauthenticated --region $REGION --memory 2Gi --update-secrets=GOOGLE_APPLICATION_CREDENTIALS=google-drive-credentials:latest --format="value(status.url)" > backend_url.txt

if ($LASTEXITCODE -ne 0) { 
    Write-Error "Backend deployment failed. Check the logs above."
    cd ../..
    exit 1 
}

$BACKEND_URL = Get-Content backend_url.txt
if ([string]::IsNullOrWhiteSpace($BACKEND_URL)) {
    Write-Error "Backend URL could not be retrieved. Deployment might have failed silently."
    cd ../..
    exit 1
}
Write-Host "Backend deployed at: $BACKEND_URL"

cd ../frontend

Write-Host "Deploying Frontend..."
# Create env vars for build/runtime
# Write .env.production for the build process to pick up NEXT_PUBLIC_API_URL
Set-Content -Path ".env.production" -Value "NEXT_PUBLIC_API_URL=$BACKEND_URL"

gcloud.cmd run deploy $FRONTEND_SERVICE_NAME --source . --allow-unauthenticated --region $REGION --set-env-vars NEXT_PUBLIC_API_URL=$BACKEND_URL


if ($LASTEXITCODE -ne 0) { 
    Write-Error "Frontend deployment failed."
    cd ../..
    exit 1 
}

Write-Host "Deployment Complete."
Write-Host "Backend: $BACKEND_URL"
# Fetch Frontend URL
$FRONTEND_URL = gcloud.cmd run services describe $FRONTEND_SERVICE_NAME --platform managed --region $REGION --format="value(status.url)"
Write-Host "Frontend: $FRONTEND_URL"

cd ../..
