import os
import glob
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from core import decode_image, merge_secret
from drive_uploader import download_vault_from_drive
from dropbox_uploader import download_from_dropbox

S1, S2, S3 = "storage_1", "storage_2", "storage_3"
OUTPUT_DIR = "encrypted_output"
RESTORE_DIR = "restored_files"
DRIVE_FOLDER_ID = "1L8O4vBaSGSd6Ga9ZbLWeGPUgvNHVYNrP"

def decrypt_data(data: bytes, key: bytes) -> bytes:
    aesgcm = AESGCM(key)
    return aesgcm.decrypt(data[:12], data[12:], None)

def recover_vault():
    print("MULTI-CLOUD RECOVERY ")
    files_input = input("Enter .enc filenames: ").strip()
    enc_filenames = [f.strip() for f in files_input.split() if f.strip().endswith('.enc')]
    
    os.makedirs(RESTORE_DIR, exist_ok=True)

    for enc_filename in enc_filenames:
        try:
            # Parsing the vaultid_username_file.enc format
            parts = enc_filename.replace(".enc", "").split("_")
            vault_id = parts[0]
            username = parts[1]

            # 1. Gather Local Keys
            images = []
            for folder in [S1, S2, S3]:
                images.extend(glob.glob(os.path.join(folder, f"{username}_{vault_id}_k*.png")))
            
            # 2. Try Node 1 (GDrive) if needed
            if len(images) < 3:
                print(f" Hunting GDrive for Vault {vault_id}...")
                download_vault_from_drive(username, vault_id, DRIVE_FOLDER_ID, S1)
                images = [] # Refresh
                for folder in [S1, S2, S3]:
                    images.extend(glob.glob(os.path.join(folder, f"{username}_{vault_id}_k*.png")))

            # 3. Try Node 2 (Dropbox) if still needed
            if len(images) < 3:
                print(f" Hunting Dropbox for Vault {vault_id}...")
                for k_num in ["k3", "k4"]:
                    download_from_dropbox(f"{username}_{vault_id}_{k_num}.png", S2)
                images = [] # Final Refresh
                for folder in [S1, S2, S3]:
                    images.extend(glob.glob(os.path.join(folder, f"{username}_{vault_id}_k*.png")))

            if len(images) < 3:
                print(f"Failed: Only {len(images)}/3 keys found.")
                continue

            # Reconstruct
            print(f"✅ Found {len(images)} keys. Unlocking...")
            chunks = [decode_image(img, 520) for img in images[:3]]
            master_key = merge_secret(chunks)[:32]

            with open(os.path.join(OUTPUT_DIR, enc_filename), "rb") as f:
                decrypted_payload = decrypt_data(f.read(), master_key)
            
            name, data = decrypted_payload.split(b'|:VAULT:|', 1)
            with open(os.path.join(RESTORE_DIR, name.decode()), "wb") as f:
                f.write(data)
            print(f"Restored: {name.decode()}")

            # CLEANUP LOGIC: Delete downloaded keys from S1 and S2
            for img_path in images:
                if img_path.startswith(S1) or img_path.startswith(S2):
                    if os.path.exists(img_path):
                        os.remove(img_path)

        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    recover_vault()