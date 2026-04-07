import dropbox
import os
import json

# This points directly to your secrets file in the same folder
SECRETS_PATH = os.path.join(os.path.dirname(__file__), 'dropbox_secrets.json')

def authenticate_dropbox():
    try:
        # 1. Read the JSON file
        with open(SECRETS_PATH, 'r') as f:
            secrets = json.load(f)
            
        # 2. Use the secrets to authenticate with a Refresh Token!
        dbx = dropbox.Dropbox(
            app_key=secrets['APP_KEY'], 
            app_secret=secrets['APP_SECRET'], 
            oauth2_refresh_token=secrets['REFRESH_TOKEN']
        )
        dbx.users_get_current_account()
        return dbx
        
    except FileNotFoundError:
        print("Dropbox Auth Failed: Could not find dropbox_secrets.json!")
        return None
    except KeyError as e:
        print(f"Dropbox Auth Failed: Missing {e} inside dropbox_secrets.json!")
        return None
    except Exception as e:
        print(f"Dropbox Auth Failed: {e}")
        return None

def upload_to_dropbox(file_path):
    dbx = authenticate_dropbox()
    if not dbx: return
    
    file_name = os.path.basename(file_path)
    dropbox_path = f"/{file_name}" 
    
    try:
        with open(file_path, 'rb') as f:
            dbx.files_upload(f.read(), dropbox_path, mode=dropbox.files.WriteMode.overwrite)
        print(f"Cloud 2: Uploaded {file_name} to Dropbox!")
    except Exception as e:
        print(f"Dropbox Upload Failed: {e}")

def download_from_dropbox(file_name, download_dir):
    dbx = authenticate_dropbox()
    if not dbx: return False
    
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)
        
    dropbox_path = f"/{file_name}"
    local_path = os.path.join(download_dir, file_name)
    
    try:
        dbx.files_download_to_file(local_path, dropbox_path)
        print(f"Cloud 2: Downloaded backup {file_name} from Dropbox")
        return True
    except Exception as e:
        print(f"Dropbox Download Failed: {e}")
        return False

# --- ISOLATED TEST BLOCK ---
if __name__ == "__main__":
    print("DROPBOX CONNECTION TEST")
    
    # Create a dummy text file to test with
    test_file = "dropbox_test.txt"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write("Node 2 (Dropbox) is officially online!")
    
    print(f"Attempting to upload '{test_file}'...")
    upload_to_dropbox(test_file)
    print("\nTest script finished!")