import os
import io
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload

SCOPES = ['https://www.googleapis.com/auth/drive']

def authenticate_gdrive():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('client_secret.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('drive', 'v3', credentials=creds)

def upload_to_drive(file_path, folder_id):
    service = authenticate_gdrive()
    file_name = os.path.basename(file_path)
    file_metadata = {'name': file_name, 'parents': [folder_id]}
    media = MediaFileUpload(file_path, resumable=True)
    try:
        service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        print(f"Cloud: Uploaded {file_name}")
    except Exception as e:
        print(f"Cloud Upload Failed: {e}")
        
def download_vault_from_drive(username, vault_id, folder_id, download_dir):
    service = authenticate_gdrive()
    # Only pull carrier images for this user+vault
    query = f"'{folder_id}' in parents and name contains '{username}_{vault_id}_' and trashed=false"
    results = service.files().list(q=query, fields="files(id, name)").execute()
    items = results.get('files', [])
    
    if not items: 
        return False
    
    if not os.path.exists(download_dir): 
        os.makedirs(download_dir)

    for item in items:
        request = service.files().get_media(fileId=item['id'])
        file_path = os.path.join(download_dir, item['name'])
        with io.FileIO(file_path, 'wb') as fh:
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while not done:
                _, done = downloader.next_chunk()
        print(f"Cloud: Downloaded backup {item['name']}")
    return True