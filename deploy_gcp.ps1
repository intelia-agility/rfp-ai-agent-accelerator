
# Deployment Script for RFP AI Agent Accelerator
# Requirements: Google Cloud SDK (gcloud) installed and authenticated.

$ErrorActionPreference = "Stop"

$REGION = "australia-southeast2"
$BACKEND_SERVICE_NAME = "rfp-backend"
$FRONTEND_SERVICE_NAME = "rfp-frontend"

Write-Host "Checking for gcloud CLI..."
if (-not (Get-Command gcloud -ErrorAction SilentlyContinue)) {
    Write-Error "Error: 'gcloud' command not found. Please install the Google Cloud SDK and ensure it's in your PATH."
    exit 1
}

Write-Host "Enabling necessary APIs..."
gcloud services enable run.googleapis.com artifactregistry.googleapis.com cloudbuild.googleapis.com

Write-Host "Deploying Backend..."
cd src/backend
# Deploy source directly (Cloud Build will build the Dockerfile)
# Added --memory 2Gi to prevent build/runtime memory issues
gcloud run deploy $BACKEND_SERVICE_NAME --source . --allow-unauthenticated --region $REGION --memory 2Gi --format="value(status.url)" > backend_url.txt

$BACKEND_URL = Get-Content backend_url.txt
Write-Host "Backend deployed at: $BACKEND_URL"

cd ../frontend

Write-Host "Deploying Frontend..."
# Create env vars for build/runtime
# Note: Next.js standalone output with runtime config might need specific handling, 
# but simply passing the env var to Cloud Run often works for server-side calls.
# For client-side NEXT_PUBLIC_ vars, they usually need to be present at BUILD time.
# gcloud run deploy typically builds in the cloud. We need to pass build-args.

gcloud run deploy $FRONTEND_SERVICE_NAME --source . --allow-unauthenticated --region $REGION --set-env-vars NEXT_PUBLIC_API_URL=$BACKEND_URL

Write-Host "Deployment Complete."
Write-Host "Backend: $BACKEND_URL"
# Fetch Frontend URL
$FRONTEND_URL = gcloud run services describe $FRONTEND_SERVICE_NAME --platform managed --region $REGION --format="value(status.url)"
Write-Host "Frontend: $FRONTEND_URL"

cd ../..
