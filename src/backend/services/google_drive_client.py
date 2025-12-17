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
        # Folder IDs - will be dynamically found or can be set via environment variables
        self.source_folder_id = os.environ.get('GOOGLE_DRIVE_SOURCE_FOLDER_ID')  # Source Information folder
        self.output_folder_id = os.environ.get('GOOGLE_DRIVE_OUTPUT_FOLDER_ID')  # RFP Output folder
        self.parent_folder_name = "RFP AI Agent"
        self.source_folder_name = "Source Information"
        self.output_folder_name = "RFP Output"
        
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
            
            # Auto-discover folder IDs if not set
            if not self.source_folder_id or not self.output_folder_id:
                self._discover_folders()
                
        except Exception as e:
            logger.warning(f"Google Drive client not available: {e}")
            self.service = None

    def _discover_folders(self):
        """
        Automatically discover the Source Information and RFP Output folder IDs.
        Uses GOOGLE_DRIVE_PARENT_FOLDER_ID if set, otherwise searches for parent folder by name.
        """
        if not self.service:
            return
            
        try:
            # Default to the provided shared folder ID if environment variable is not set
            parent_id = os.environ.get('GOOGLE_DRIVE_PARENT_FOLDER_ID', '0AJriKoRrgD4nUk9PVA')
            
            if not parent_id:
                # Find the parent folder "RFP AI Agent" by name
                parent_folder = self._find_folder_by_name(self.parent_folder_name)
                if not parent_folder:
                    logger.warning(f"Parent folder '{self.parent_folder_name}' not found")
                    return
                parent_id = parent_folder['id']
                logger.info(f"Found parent folder by name: {self.parent_folder_name} (ID: {parent_id})")
            else:
                logger.info(f"Using configured parent folder ID: {parent_id}")
            
            # Find Source Information folder
            if not self.source_folder_id:
                source_folder = self._find_folder_by_name(self.source_folder_name, parent_id)
                if source_folder:
                    self.source_folder_id = source_folder['id']
                    logger.info(f"Found source folder: {self.source_folder_name} (ID: {self.source_folder_id})")
                else:
                    logger.warning(f"Source folder '{self.source_folder_name}' not found in parent")
            
            # Find RFP Output folder
            if not self.output_folder_id:
                output_folder = self._find_folder_by_name(self.output_folder_name, parent_id)
                if output_folder:
                    self.output_folder_id = output_folder['id']
                    logger.info(f"Found output folder: {self.output_folder_name} (ID: {self.output_folder_id})")
                else:
                    logger.warning(f"Output folder '{self.output_folder_name}' not found in parent - attempting to create")
                    try:
                        self.output_folder_id = self.create_folder(self.output_folder_name, parent_id)
                        logger.info(f"Created output folder: {self.output_folder_name} (ID: {self.output_folder_id})")
                    except Exception as e:
                        logger.error(f"Failed to create output folder: {e}")
                    
        except Exception as e:
            logger.error(f"Error discovering folders: {e}")

    def _find_folder_by_name(self, folder_name: str, parent_id: str = None):
        """
        Find a folder by name, optionally within a specific parent folder.
        Returns the first matching folder or None.
        """
        if not self.service:
            return None
            
        try:
            query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
            if parent_id:
                query += f" and '{parent_id}' in parents"
            
            results = self.service.files().list(
                q=query,
                pageSize=10,
                fields="files(id, name)"
            ).execute()
            
            files = results.get('files', [])
            return files[0] if files else None
            
        except Exception as e:
            logger.error(f"Error finding folder '{folder_name}': {e}")
            return None


    def create_folder(self, folder_name, parent_id):
        """Create a new folder in Google Drive."""
        if not self.service:
            return None
        try:
            file_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder',
                'parents': [parent_id]
            }
            file = self.service.files().create(body=file_metadata, fields='id').execute()
            return file.get('id')
        except Exception as e:
            logger.error(f"Error creating folder '{folder_name}': {e}")
            raise e

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
        Get all supporting documents from the Source Information folder.
        Returns a list of dicts with file metadata and content.
        """
        if not self.source_folder_id:
            logger.warning("Source folder ID not set - cannot retrieve documents")
            return []
            
        files = self.list_files_in_folder(self.source_folder_id)
        documents = []
        
        for file in files:
            # Only process document files
            if file['mimeType'] in [
                'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                'text/plain',
                'application/vnd.google-apps.document',
                'application/pdf'
            ]:
                content = self.get_file_content_as_text(file['id'])
                if content:
                    documents.append({
                        'id': file['id'],
                        'name': file['name'],
                        'content': content,
                        'modified': file.get('modifiedTime', '')
                    })
                    logger.info(f"Loaded source document: {file['name']}")
        
        logger.info(f"Retrieved {len(documents)} source documents from '{self.source_folder_name}' folder")
        return documents

    def upload_file(self, file_path, filename=None, folder_id=None):
        """
        Upload a file to Google Drive RFP Output folder.
        Returns the file ID if successful, None otherwise.
        """
        if not self.service:
            logger.warning("Google Drive service not initialized")
            return None
        
        # Use output folder by default
        if not folder_id:
            folder_id = self.output_folder_id
            
        if not folder_id:
            logger.error("No output folder ID available for upload")
            return None
        
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
            
            # Convert DOCX to Google Doc to avoid storage quota issues for Service Accounts
            if filename.endswith('.docx'):
                file_metadata['mimeType'] = 'application/vnd.google-apps.document'
            
            media = MediaFileUpload(file_path, mimetype=mime_type, resumable=False)
            
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, name, webViewLink'
            ).execute()
            
            logger.info(f"File uploaded successfully to '{self.output_folder_name}' folder: {file.get('name')} (ID: {file.get('id')})")
            logger.info(f"View file at: {file.get('webViewLink')}")
            return {
                'id': file.get('id'),
                'url': file.get('webViewLink'),
                'name': file.get('name')
            }
            
        except Exception as e:
            error_msg = str(e)
            if "storageQuotaExceeded" in error_msg:
                msg = "Upload Failed: Service Account storage quota exceeded. Please move the 'RFP Accelerator Artefacts' folder to a Google Shared Drive (Team Drive) to enable uploads."
                logger.error(msg)
                raise Exception(msg)
            
            logger.error(f"Error uploading file to Google Drive: {e}")
            raise e

