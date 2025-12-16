class SharePointClient:
    def __init__(self):
        pass

    def upload_file(self, local_path: str, remote_folder: str):
        print(f"Mock uploading {local_path} to {remote_folder}")
        return True

    def download_file(self, remote_path: str, local_path: str):
        print(f"Mock downloading {remote_path} to {local_path}")
        return True

    def list_files(self, folder_path: str):
        return ["previous_rfp_response.docx", "company_overview.pdf"]
