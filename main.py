import os
import random
import glob
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from core import encode_image, split_secret
from drive_uploader import upload_to_drive
from dropbox_uploader import upload_to_dropbox

S1, S2, S3 = "storage_1", "storage_2", "storage_3"
PHOTOS_DIR = "photos"
OUTPUT_DIR = "encrypted_output"
DRIVE_FOLDER_ID = "1L8O4vBaSGSd6Ga9ZbLWeGPUgvNHVYNrP"

def encrypt_data(data: bytes, key: bytes) -> bytes:
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)
    return nonce + aesgcm.encrypt(nonce, data, None)

def run_vault():
    print("MULTI-CLOUD VAULT ENGINE")
    
    username = input("Enter username: ").strip().lower().replace(" ", "_")
    files_input = input("Enter filenames (space separated): ").strip()
    file_paths = [f.strip() for f in files_input.split() if os.path.exists(f.strip())]
    
    for folder in [S1, S2, S3, OUTPUT_DIR]: os.makedirs(folder, exist_ok=True)
    
    available_photos = glob.glob(os.path.join(PHOTOS_DIR, "*.png"))
    if len(available_photos) < 5:
        print("Error: Need 5+ photos.")
        return

    for filepath in file_paths:
        vault_id = str(random.randint(1000000, 9999999))
        master_key = AESGCM.generate_key(bit_length=256)
        
        # --- FILENAME SANITIZATION ---
        original_name = os.path.basename(filepath)
        if "____" in original_name:
            print(f"Warning: '{original_name}' contains 4 underscores. Renaming to prevent parsing errors.")
            original_name = original_name.replace("____", "_")
        
        base_name = os.path.splitext(original_name)[0].replace(" ", "_")
        
        # New Strict Format: vaultid_username_filename.enc
        enc_filename = f"{vault_id}_{username}_{base_name}.enc"
        print(f"\n🚀 Securing: {original_name} -> {enc_filename}")
        
        with open(filepath, "rb") as f: file_data = f.read()
        payload = original_name.encode('utf-8') + b'|:VAULT:|' + file_data
        
        with open(os.path.join(OUTPUT_DIR, enc_filename), "wb") as f:
            f.write(encrypt_data(payload, master_key))

        # Erasure Coding Math: Any 3 of 5
        shares = split_secret(master_key, threshold=3, total=5)
        photos = random.sample(available_photos, 5)

        # --- DISTRIBUTION LOGIC ---
        print("Distributing Keys")
        
        # Node 1: Google Drive (Keys 1 & 2)
        for i in range(0, 2):
            fname = f"v_{vault_id}_k{i+1}.png"
            path = os.path.join(S1, fname)
            encode_image(photos[i], shares[i], path)
            upload_to_drive(path, DRIVE_FOLDER_ID)
            os.remove(path)
            print(f"GDrive: {fname}")

        # Node 2: Dropbox (Keys 3 & 4)
        for i in range(2, 4):
            fname = f"v_{vault_id}_k{i+1}.png"
            path = os.path.join(S2, fname)
            encode_image(photos[i], shares[i], path)
            upload_to_dropbox(path)
            os.remove(path)
            print(f"Dropbox: {fname}")
            
        # Node 3: Local S3 (Key 5)
        fname = f"v_{vault_id}_k5.png"
        encode_image(photos[4], shares[4], os.path.join(S3, fname))
        print(f"Local S3: {fname}")

    print("\nProcess Complete.")

if __name__ == "__main__":
    run_vault()