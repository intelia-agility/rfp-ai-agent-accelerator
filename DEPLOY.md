
# Deployment Guide

This guide describes how to deploy the RFP AI Agent Accelerator to Google Cloud Platform (GCP).

## Prerequisites
1.  **Google Cloud SDK (gcloud)** installed and initialized.
    - Run `gcloud auth login`
    - Run `gcloud config set project YOUR_PROJECT_ID`
2.  **Docker** installed (optional, but good for local testing).

## Architecture
We will deploy two Cloud Run services:
1.  **rfp-backend**: The FastAPI Python backend.
2.  **rfp-frontend**: The Next.js frontend.

## Step 1: Deploy Backend

1.  Navigate to the backend directory:
    ```bash
    cd src/backend
    ```

2.  Deploy to Cloud Run:
    ```bash
    gcloud run deploy rfp-backend --source . --allow-unauthenticated --region us-central1
    ```
    *Note: Replace `us-central1` with your preferred region.*
    *Note: We use `--allow-unauthenticated` for demo purposes. Secure it as needed.*

3.  **Copy the Backend URL**. You will need this for the frontend configuration.
    Example: `https://rfp-backend-xyz.a.run.app`

## Step 2: Deploy Frontend

1.  Navigate to the frontend directory:
    ```bash
    cd ../frontend
    ```

2.  Build the container (Next.js requires build args for env vars if baking them in, but we can also use runtime env vars with some setup. The easiest way for simple deployment is purely checking the URL). 
    
    *Important: For Next.js to talk to the backend, we need to set the API Base URL.*
    
    Create/Update a `.env.production` file in `src/frontend`:
    ```env
    NEXT_PUBLIC_API_URL=https://rfp-backend-xyz.a.run.app
    ```

3.  Deploy to Cloud Run:
    ```bash
    gcloud run deploy rfp-frontend --source . --allow-unauthenticated --region us-central1
    ```

4.  **Access the App**: Click the URL provided by the deployment command (e.g., `https://rfp-frontend-xyz.a.run.app`).

## Troubleshooting
- **Permissions**: Ensure your active account has `run.services.create` and `artifactregistry.repositories.create` permissions.
- **APIs**: Ensure `run.googleapis.com` and `artifactregistry.googleapis.com` are enabled.
  ```bash
  gcloud services enable run.googleapis.com artifactregistry.googleapis.com cloudbuild.googleapis.com
  ```
