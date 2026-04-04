import dropbox
import os

# 🚨 PASTE YOUR MASSIVE TOKEN HERE INSIDE THE QUOTES
DROPBOX_ACCESS_TOKEN = "sl.u.AGZYP9fpxj_p7BLFIEnITLNFbSPPThCGnlX0j3NO1KMPge6xorQ8nYU-vRTTCtw9lS5PhajI_U2dyY4jTAIn2Ui_YWfpaCQhJ7TAg94tkdkxxEvi4RVvDS-YlKm9n0fmCnqUR_CI2NzlUJMMxNtQxBh4AoaQIQymaiWJcbV7a9SH4i7dMKWC_VFrzZVJ1fw_PoUYtp1D0AlqzoffkGXjzMOJrk1jpiuA3qMYuDv4A9yz9JPPKrxUC6CkUV42m7bUkmfF4gFjZqOtTY41VMBld0PvMUFbcPsLBK_sFPtUqnvAyaVQsE-mS5-GsPOPhpgOqh_Ck1ekCvxBr3KLPJrTXvv_mJa-spqt6G-bUD_eJuWASBvNPPkYmayI3M7715cTmJGBf7of1gpFgRwsWJnb4syc3AGuqxPIq7Q3wtmru-OpL4cRGuLbjSw3XqlsHjn0i_8mMVsv1-M7ttNyatrxf4EWcVAZFV-HcbCebgdqfuDMpR6frgjoGsNtvH9IhX-Dg1J0LTui9AiWudSbnpfr0fn0QTCkjuZx4DdP0_hI5ppv2ZiCBAfPHFxLgnvkW9eMcJWPR_y65Dt-Pn0qRZGMbxUOLrgG9ceYfGhKlZvh4QdRWwx19uP-x4yNTrDmo92Hc1oR1oZQtUPRZ_nSZUtAp8F_5Q4138amZo04vcMjtL0XGIUVFI3pg_NY16KaoErykUwxxMAODZJgJNOXGEWhfT2Se6tI2anNoHXH4vgnBN2qKv_DHqKKy5CApQGULEbenegxq-ZAf2wUrwtuMhm7AGO55TAAJey8K8-mdmxMXJ7hnQshHoRhipOQCkcSTFonJFqOxqjMjA_bhcHIZwpcCYa4J4-RmDeZHAhDNk1ugIStODEZ_A36VjxTf3D7R3oEsfDsFXjjdFn91EwCnefwxA5kFLlgZsPUHFtiWOnelIqSi8YcxolumxEdXjpk3YZd4RukT3-z02lZ57EkA_1ZVzDw9otMERNNq_X121VxbLTdljviEsZC6rhDlAZ5rcno-4ANmuBZby-LSsxAGLfnAQqcZIaVQKD3LdO7oH0E0VxpocOvl7r_lknpI4FZrSLgT8s86K-6MfFWoSTNcQGt1fIrNKUzgjfL8spElq8_IGsvEe5Oytl4kIlEqDqOJd_t5jrixMvelJn25Xm8l-LXCqAvtbXd0FjgLat0AoaF2WtdmNbIa7zVg80729BL6MGFUMQLi5N4Nwki7UPl-f1lhhNMWOz2TYWxaN_dylkjSunQuR4CiKIA4lqTLwx6Kg66lnuUvYP1Y19xmC9JkAkF2KAzZKM1xdrWHXQ7_v5Ce3pgH_upZ7tNeU0EZRMU_410IDutv5gFe6ONJj3SLWNxZ6oTeQGSQ2GkFap5oE3K_COQwLXHIz9kiucl0FWQqNL-0TCE_ib2h910R495UQTMtBR4jevmKCdEEHZa8cdASN2eFA"

def authenticate_dropbox():
    try:
        dbx = dropbox.Dropbox(DROPBOX_ACCESS_TOKEN)
        dbx.users_get_current_account()
        return dbx
    except Exception as e:
        print(f"Dropbox Auth Failed: Check your token! Error: {e}")
        return None

def upload_to_dropbox(file_path):
    dbx = authenticate_dropbox()
    if not dbx: return
    
    file_name = os.path.basename(file_path)
    # Dropbox app folders use '/' as the root inside that specific app folder
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
    
    if DROPBOX_ACCESS_TOKEN == "PASTE_YOUR_LONG_TOKEN_HERE":
        print("Wait! You forgot to paste your long token into the script.")
    else:
        # Create a dummy text file to test with
        test_file = "dropbox_test.txt"
        with open(test_file, "w", encoding="utf-8") as f:
            f.write("Node 2 (Dropbox) is officially online!")
        
        print(f"Attempting to upload '{test_file}'...")
        upload_to_dropbox(test_file)
        print("\nTest script finished!")