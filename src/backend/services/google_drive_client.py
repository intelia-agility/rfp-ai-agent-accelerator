try:
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaIoBaseDownload
    GOOGLE_DRIVE_AVAILABLE = True
except ImportError:
    GOOGLE_DRIVE_AVAILABLE = False
    
import io
import os
import json
import tempfile
import logging

logger = logging.getLogger(__name__)

class GoogleDriveClient:
    def __init__(self):
        """
        Initialize Google Drive client using service account credentials.
        Expects GOOGLE_APPLICATION_CREDENTIALS environment variable to be set.
        """
        self.service = None
        self.folder_id = "1yWaMl4qXUnXHp5m15lL8JChBNKgEZoe4"  # Your RFP folder (read/write)
        
        if not GOOGLE_DRIVE_AVAILABLE:
            logger.info("Google Drive libraries not available - integration disabled")
            return
        
        try:
            creds_path_or_json = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
            
            if not creds_path_or_json:
                logger.info("GOOGLE_APPLICATION_CREDENTIALS not set - Google Drive integration disabled")
                return
            
            # Check if it's a JSON string or file path
            if creds_path_or_json.strip().startswith('{'):
                # It's JSON content from secret
                creds_data = json.loads(creds_path_or_json)
                credentials = service_account.Credentials.from_service_account_info(
                    creds_data,
                    scopes=[
                        'https://www.googleapis.com/auth/drive.file',
                        'https://www.googleapis.com/auth/drive.readonly'
                    ]
                )
            else:
                # It's a file path
                if not os.path.exists(creds_path_or_json):
                    logger.warning(f"Credentials file not found: {creds_path_or_json}")
                    return
                    
                credentials = service_account.Credentials.from_service_account_file(
                    creds_path_or_json,
                    scopes=[
                        'https://www.googleapis.com/auth/drive.file',
                        'https://www.googleapis.com/auth/drive.readonly'
                    ]
                )
            
            self.service = build('drive', 'v3', credentials=credentials)
            logger.info("Google Drive client initialized successfully")
        except Exception as e:
            logger.warning(f"Google Drive client not available: {e}")
            self.service = None

    def list_files_in_folder(self, folder_id=None):
        """
        List all files in the specified Google Drive folder.
        """
        if not self.service:
            logger.warning("Google Drive service not initialized")
            return []
        
        if not folder_id:
            folder_id = self.folder_id
            
        try:
            query = f"'{folder_id}' in parents and trashed=false"
            results = self.service.files().list(
                q=query,
                pageSize=100,
                fields="files(id, name, mimeType, modifiedTime)"
            ).execute()
            
            files = results.get('files', [])
            return files
        except Exception as e:
            logger.error(f"Error listing files from Google Drive: {e}")
            return []

    def download_file(self, file_id, output_path):
        """
        Download a file from Google Drive.
        """
        if not self.service:
            return None
            
        try:
            request = self.service.files().get_media(fileId=file_id)
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            
            done = False
            while not done:
                status, done = downloader.next_chunk()
                
            fh.seek(0)
            with open(output_path, 'wb') as f:
                f.write(fh.read())
                
            return output_path
        except Exception as e:
            logger.error(f"Error downloading file {file_id}: {e}")
            return None

    def get_file_content_as_text(self, file_id):
        """
        Download and extract text content from a file.
        Supports DOCX and TXT files.
        """
        if not self.service:
            return ""
            
        try:
            # Get file metadata
            file_metadata = self.service.files().get(fileId=file_id, fields='name,mimeType').execute()
            file_name = file_metadata.get('name', 'unknown')
            mime_type = file_metadata.get('mimeType', '')
            
            # Download to temp location
            temp_path = f"temp_drive_{file_id}_{file_name}"
            downloaded = self.download_file(file_id, temp_path)
            
            if not downloaded:
                return ""
            
            # Extract text based on file type
            text = ""
            if temp_path.endswith('.docx') or 'wordprocessingml' in mime_type:
                try:
                    from docx import Document
                    doc = Document(temp_path)
                    text = '\n'.join([para.text for para in doc.paragraphs])
                except Exception as e:
                    logger.error(f"Error reading DOCX: {e}")
            elif temp_path.endswith('.txt') or 'text/plain' in mime_type:
                with open(temp_path, 'r', encoding='utf-8') as f:
                    text = f.read()
            
            # Cleanup
            if os.path.exists(temp_path):
                os.remove(temp_path)
                
            return text
        except Exception as e:
            logger.error(f"Error getting file content: {e}")
            return ""

    def get_all_rfp_documents(self):
        """
        Get all RFP documents from the folder as a knowledge base.
        Returns a list of dicts with file metadata and content.
        """
        files = self.list_files_in_folder()
        documents = []
        
        for file in files:
            # Only process document files
            if file['mimeType'] in [
                'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                'text/plain',
                'application/vnd.google-apps.document'
            ]:
                content = self.get_file_content_as_text(file['id'])
                if content:
                    documents.append({
                        'id': file['id'],
                        'name': file['name'],
                        'content': content,
                        'modified': file.get('modifiedTime', '')
                    })
        
        return documents

    def upload_file(self, file_path, filename=None, folder_id=None):
        """
        Upload a file to Google Drive.
        Returns the file ID if successful, None otherwise.
        """
        if not self.service:
            logger.warning("Google Drive service not initialized")
            return None
        
        if not folder_id:
            folder_id = self.folder_id
        
        if not filename:
            filename = os.path.basename(file_path)
        
        try:
            if not GOOGLE_DRIVE_AVAILABLE:
                return None
                
            from googleapiclient.http import MediaFileUpload
            
            # Determine MIME type based on file extension
            mime_type = 'application/octet-stream'
            if filename.endswith('.docx'):
                mime_type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            elif filename.endswith('.txt'):
                mime_type = 'text/plain'
            elif filename.endswith('.pdf'):
                mime_type = 'application/pdf'
            
            file_metadata = {
                'name': filename,
                'parents': [folder_id]
            }
            
            media = MediaFileUpload(file_path, mimetype=mime_type, resumable=True)
            
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, name, webViewLink'
            ).execute()
            
            logger.info(f"File uploaded successfully: {file.get('name')} (ID: {file.get('id')})")
            return file.get('id')
            
        except Exception as e:
            logger.error(f"Error uploading file to Google Drive: {e}")
            return None

