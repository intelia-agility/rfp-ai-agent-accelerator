# Google Drive Integration Setup

This application uses Google Drive API to read past RFP responses and questions from your Google Drive folder.

## Setup Instructions

### 1. Create a Service Account

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select your project: `rfp-accelerator-agent`
3. Navigate to **APIs & Services** > **Credentials**
4. Click **Create Credentials** > **Service Account**
5. Fill in the service account details:
   - Name: `rfp-drive-reader`
   - Description: `Service account for reading RFP documents from Google Drive`
6. Click **Create and Continue**
7. Grant the role: **Viewer** (or no role if you prefer minimal permissions)
8. Click **Done**

### 2. Create and Download Service Account Key

1. Click on the newly created service account
2. Go to the **Keys** tab
3. Click **Add Key** > **Create New Key**
4. Select **JSON** format
5. Click **Create** - this will download a JSON file

### 3. Enable Google Drive API

1. In Google Cloud Console, go to **APIs & Services** > **Library**
2. Search for "Google Drive API"
3. Click on it and click **Enable**

### 4. Share Google Drive Folder with Service Account

1. Open the JSON key file you downloaded
2. Copy the `client_email` value (it looks like: `rfp-drive-reader@rfp-accelerator-agent.iam.gserviceaccount.com`)
3. Go to your Google Drive folder: https://drive.google.com/drive/folders/1u2VOEVJfEl0JpOdJxlg95CAa_1_4tzVe
4. Right-click the folder > **Share**
5. Paste the service account email
6. Set permission to **Viewer**
7. Uncheck "Notify people"
8. Click **Share**

### 5. Deploy the Service Account Key

#### For Local Development:
```bash
# Set environment variable
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/service-account-key.json"
```

#### For Google Cloud Run Deployment:
The application already uses the default service account credentials when running on Cloud Run. You need to:

1. Upload the service account key as a Secret in Google Secret Manager:
```bash
gcloud secrets create rfp-drive-credentials --data-file=/path/to/your/service-account-key.json
```

2. Grant the Cloud Run service account access to the secret:
```bash
gcloud secrets add-iam-policy-binding rfp-drive-credentials \
    --member="serviceAccount:680149411946-compute@developer.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"
```

3. Update the Cloud Run service to mount the secret:
```bash
gcloud run services update rfp-backend \
    --update-secrets=GOOGLE_APPLICATION_CREDENTIALS=/secrets/drive-key:rfp-drive-credentials:latest \
    --region=australia-southeast2
```

## Folder Structure

The application will read all documents from the folder:
- Folder ID: `1u2VOEVJfEl0JpOdJxlg95CAa_1_4tzVe`
- Supported formats: DOCX, TXT, Google Docs

## How It Works

When generating draft responses or questions, the application will:
1. Connect to Google Drive using the service account
2. List all documents in the specified folder
3. Download and extract text content from each document
4. Use this content as additional context for the AI to learn from past successful RFPs
5. Generate more accurate and contextually relevant responses

## Troubleshooting

- **"Failed to initialize Google Drive client"**: Check that `GOOGLE_APPLICATION_CREDENTIALS` is set correctly
- **"Error listing files"**: Verify the service account email has been granted access to the folder
- **"Could not fetch Google Drive documents"**: Check that the Google Drive API is enabled in your project
