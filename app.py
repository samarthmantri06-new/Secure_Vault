import os
import random
import glob
import zipfile
import io
import sqlite3
import re
from flask import Flask, render_template, request, send_file, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# Import your core engines
from core import encode_image, decode_image, split_secret, merge_secret
from drive_uploader import upload_to_drive, download_vault_from_drive
from dropbox_uploader import upload_to_dropbox, download_from_dropbox

app = Flask(__name__)
app.secret_key = "super_secret_vault_key_change_this_later"

# --- CONSTANTS & FOLDERS ---
S1, S2, S3 = "storage_1", "storage_2", "storage_3"
PHOTOS_DIR = "photos"
UPLOAD_DIR = "temp_uploads"
DRIVE_FOLDER_ID = "1L8O4vBaSGSd6Ga9ZbLWeGPUgvNHVYNrP"

for folder in [S1, S2, S3, UPLOAD_DIR, PHOTOS_DIR]:
    os.makedirs(folder, exist_ok=True)

# --- VALIDATION HELPERS ---
def is_valid_password(password):
    if len(password) < 8: return False
    if not re.search(r"[A-Z]", password): return False
    if not re.search(r"[0-9]", password): return False
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password): return False
    return True

def is_valid_username(username):
    return bool(re.match(r"^[a-zA-Z0-9_]+$", username))

# --- DATABASE SETUP ---
def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            action TEXT NOT NULL,
            filename TEXT NOT NULL,
            vault_id TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_db()

def encrypt_data(data: bytes, key: bytes) -> bytes:
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)
    return nonce + aesgcm.encrypt(nonce, data, None)

# --- AUTHENTICATION ROUTES ---
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        raw_user = request.form['username'].strip()
        password = request.form['password']
        confirm_password = request.form.get('ConfirmPassword')

        if password != confirm_password:
            return "Passwords do not match!", 400
        if not is_valid_username(raw_user):
            return "Username can only contain letters, numbers, and underscores (_).", 400
        if not is_valid_password(password):
            return "Password must be 8+ chars with a Capital, Number, and Special Symbol.", 400

        full_username = f"{raw_user}@securevault"
        hashed_pw = generate_password_hash(password)
        
        try:
            conn = sqlite3.connect('database.db')
            c = conn.cursor()
            c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (full_username, hashed_pw))
            conn.commit()
            conn.close()
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            return f"The username '{full_username}' is already taken.", 400
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        raw_user = request.form['username'].strip()
        password = request.form['password']
        
        # Smart detection: add suffix if user didn't type it
        full_username = raw_user if raw_user.endswith("@securevault") else f"{raw_user}@securevault"
        
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username = ?", (full_username,))
        user = c.fetchone()
        conn.close()
        
        if user and check_password_hash(user[2], password):
            session['username'] = full_username
            return redirect(url_for('home'))
        else:
            return "Invalid username or password!", 401
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))

# --- BASIC WEB ROUTES ---
@app.route('/')
def home(): 
    return render_template('index.html')

@app.route('/encrypt.html')
def encrypt_page(): 
    if 'username' not in session: return redirect(url_for('login'))
    return render_template('encrypt.html')

@app.route('/decrypt.html')
def decrypt_page(): 
    if 'username' not in session: return redirect(url_for('login'))
    return render_template('decrypt.html')

@app.route('/profile.html')
def profile(): 
    if 'username' not in session: return redirect(url_for('login'))
    username = session['username']
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM history WHERE username = ? AND action = 'Encrypt'", (username,))
    enc_count = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM history WHERE username = ? AND action = 'Decrypt'", (username,))
    dec_count = c.fetchone()[0]
    conn.close()
    return render_template('profile.html', username=username, enc_count=enc_count, dec_count=dec_count)

@app.route('/history.html')
def history(): 
    if 'username' not in session: return redirect(url_for('login'))
    username = session['username']
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT action, filename, vault_id, timestamp FROM history WHERE username = ? ORDER BY timestamp DESC", (username,))
    user_history = c.fetchall()
    conn.close()
    return render_template('history.html', history=user_history)

# --- ENCRYPTION ROUTE ---
@app.route('/encrypt', methods=['POST'])
def handle_encrypt():
    if 'username' not in session: return redirect(url_for('login'))
    if 'uploadedFile' not in request.files: return "No file uploaded", 400
    
    files = request.files.getlist('uploadedFile')
    username = session['username'] 
    available_photos = glob.glob(os.path.join(PHOTOS_DIR, "*.png"))
    if len(available_photos) < 5: return "Error: Need 5+ .png photos in the 'photos' folder.", 500

    memory_zip = io.BytesIO()
    with zipfile.ZipFile(memory_zip, 'w', zipfile.ZIP_DEFLATED) as zf:
        for file in files:
            if file.filename == '': continue
            original_name = file.filename.replace("____", "_").replace(" ", "_")
            file_data = file.read()
            vault_id = str(random.randint(1000000, 9999999))
            master_key = AESGCM.generate_key(bit_length=256)
            base_name = os.path.splitext(original_name)[0]
            
            # Use the username with suffix in the filename
            enc_filename = f"{vault_id}_{username}_{base_name}.enc"
            
            payload = original_name.encode('utf-8') + b'|:VAULT:|' + file_data
            encrypted_bytes = encrypt_data(payload, master_key)
            zf.writestr(enc_filename, encrypted_bytes)

            shares = split_secret(master_key, threshold=3, total=5)
            photos = random.sample(available_photos, 5)

            for i in range(0, 2):
                path = os.path.join(S1, f"v_{vault_id}_k{i+1}.png")
                encode_image(photos[i], shares[i], path)
                upload_to_drive(path, DRIVE_FOLDER_ID)
                os.remove(path)
                
            for i in range(2, 4):
                path = os.path.join(S2, f"v_{vault_id}_k{i+1}.png")
                encode_image(photos[i], shares[i], path)
                upload_to_dropbox(path)
                os.remove(path)
                
            encode_image(photos[4], shares[4], os.path.join(S3, f"v_{vault_id}_k5.png"))

            conn = sqlite3.connect('database.db')
            c = conn.cursor()
            c.execute("INSERT INTO history (username, action, filename, vault_id) VALUES (?, ?, ?, ?)", 
                      (username, "Encrypt", original_name, vault_id))
            conn.commit()
            conn.close()

    memory_zip.seek(0)
    return send_file(memory_zip, download_name='SecureVault_Encrypted.zip', as_attachment=True, mimetype='application/zip')

# --- DECRYPTION ROUTE ---
@app.route('/decrypt', methods=['POST'])
def handle_decrypt():
    if 'username' not in session: return redirect(url_for('login'))
    if 'encrypted_file' not in request.files: return "No file uploaded.", 400
        
    files = request.files.getlist('encrypted_file')
    memory_zip = io.BytesIO()
    files_processed = 0
    current_user = session['username'] 
    
    with zipfile.ZipFile(memory_zip, 'w', zipfile.ZIP_DEFLATED) as zf:
        for file in files:
            if file.filename == '': continue
            enc_filename = file.filename
            encrypted_bytes = file.read() 
            if not enc_filename.endswith('.enc'): continue 
            
            try:
                # Splitting updated to handle the username@securevault format correctly
                parts = enc_filename.replace(".enc", "").split("_")
                if len(parts) < 3: continue
                vault_id = parts[0]
                file_owner = parts[1] 

                if file_owner != current_user: continue 

                images = []
                for folder in [S1, S2, S3]: images.extend(glob.glob(os.path.join(folder, f"v_{vault_id}_k*.png")))
                
                if len(images) < 3:
                    try: download_vault_from_drive(vault_id, DRIVE_FOLDER_ID, S1)
                    except TypeError: download_vault_from_drive(file_owner, vault_id, DRIVE_FOLDER_ID, S1)
                    images = [] 
                    for folder in [S1, S2, S3]: images.extend(glob.glob(os.path.join(folder, f"v_{vault_id}_k*.png")))

                if len(images) < 3:
                    for k_num in ["k3", "k4"]: download_from_dropbox(f"v_{vault_id}_{k_num}.png", S2)
                    images = [] 
                    for folder in [S1, S2, S3]: images.extend(glob.glob(os.path.join(folder, f"v_{vault_id}_k*.png")))

                if len(images) < 3: continue

                chunks = [decode_image(img, 520) for img in images[:3]]
                master_key = merge_secret(chunks)[:32]
                aesgcm = AESGCM(master_key)
                decrypted_payload = aesgcm.decrypt(encrypted_bytes[:12], encrypted_bytes[12:], None)
                
                name, data = decrypted_payload.split(b'|:VAULT:|', 1)
                restored_filename = name.decode()
                zf.writestr(restored_filename, data)
                files_processed += 1

                conn = sqlite3.connect('database.db')
                c = conn.cursor()
                c.execute("INSERT INTO history (username, action, filename, vault_id) VALUES (?, ?, ?, ?)", 
                          (current_user, "Decrypt", restored_filename, vault_id))
                conn.commit()
                conn.close()

                for img_path in images:
                    if img_path.startswith(S1) or img_path.startswith(S2):
                        try:
                            if os.path.exists(img_path): os.remove(img_path)
                        except Exception: pass

            except Exception as e:
                print(f"Decryption Error: {e}")
                continue

    if files_processed == 0:
        return "Failed to decrypt. Keys missing or ownership error.", 403

    memory_zip.seek(0)
    return send_file(memory_zip, download_name='SecureVault_Restored.zip', as_attachment=True, mimetype='application/zip')

if __name__ == '__main__':
    app.run(debug=True)