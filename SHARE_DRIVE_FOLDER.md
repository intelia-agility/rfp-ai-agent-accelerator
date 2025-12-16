# Google Drive Setup - FINAL STEP

## ✅ Completed Steps:
1. ✅ Created service account: `rfp-drive-reader`
2. ✅ Generated service account key
3. ✅ Enabled Google Drive API
4. ✅ Created secret in Secret Manager
5. ✅ Granted Cloud Run access to the secret
6. ✅ Updated backend to use the secret
7. ✅ Deploying updated backend code

## 🔴 REQUIRED: Share Google Drive Folder

**You must manually share your Google Drive folder with the service account.**

### Service Account Email:
```
rfp-drive-reader@rfp-accelerator-agent.iam.gserviceaccount.com
```

### Steps to Share:
1. Open your Google Drive folder: https://drive.google.com/drive/folders/1u2VOEVJfEl0JpOdJxlg95CAa_1_4tzVe

2. Right-click the folder and select **"Share"**

3. In the "Add people and groups" field, paste:
   ```
   rfp-drive-reader@rfp-accelerator-agent.iam.gserviceaccount.com
   ```

4. Set the permission level to **"Viewer"**

5. **IMPORTANT**: Uncheck "Notify people" (the service account doesn't need an email notification)

6. Click **"Share"** or **"Send"**

### Verification:
Once you've shared the folder, the application will be able to:
- Read all documents in the folder
- Extract text from DOCX, TXT, and Google Docs files
- Use this content as context when generating RFP responses and questions

The backend is currently deploying with the Google Drive integration enabled!
