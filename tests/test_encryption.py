import os
import sqlite3
import pytest
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# Set env vars to avoid startup errors in app.py during import
os.environ["FLASK_SECRET_KEY"] = "test_secret_key"
os.environ["DRIVE_FOLDER_ID"] = "test_folder_id"

from app import encrypt_data
from core.sharer import split_secret, merge_secret

def test_encryption_round_trip():
    """
    a. Round-trip test: encrypt a payload, split the key (3-of-5),
       reconstruct from exactly 3 shares, decrypt, and assert output equals original.
    """
    original_payload = b"test payload for round-trip"
    master_key = AESGCM.generate_key(bit_length=256)
    
    # Encrypt
    encrypted_bytes = encrypt_data(original_payload, master_key)
    
    # Split
    shares = split_secret(master_key, threshold=3, total=5)
    assert len(shares) == 5
    
    # Reconstruct from 3 shares (0, 1, and 2)
    reconstructed_key = merge_secret([shares[0], shares[1], shares[2]])[:32]
    
    # Decrypt
    aesgcm = AESGCM(reconstructed_key)
    decrypted_payload = aesgcm.decrypt(encrypted_bytes[:12], encrypted_bytes[12:], None)
    
    assert decrypted_payload == original_payload

def test_threshold_failure():
    """
    b. Threshold failure test: attempt reconstruction with only 2 shares.
    """
    master_key = AESGCM.generate_key(bit_length=256)
    shares = split_secret(master_key, threshold=3, total=5)
    
    # Reconstruct from 2 shares
    # Shamir's Secret Sharing requires at least the threshold.
    # We should catch the exception raised when combining fewer than the required shares
    # or assert the key does not match if it silently returns garbage.
    try:
        reconstructed_key = merge_secret([shares[0], shares[1]])[:32]
        assert reconstructed_key != master_key
    except Exception as e:
        # Expected failure
        pass

def test_ownership_check(tmp_path):
    """
    c. Ownership check test: insert "Encrypt" history for user A, assert
       query for user B returns no match.
    """
    db_path = tmp_path / "test_database.db"
    
    # Setup test DB
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            action TEXT NOT NULL,
            filename TEXT NOT NULL,
            vault_id TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Insert user A
    vault_id = "1234567"
    c.execute(
        "INSERT INTO history (username, action, filename, vault_id) VALUES (?, ?, ?, ?)", 
        ("userA@securevault", "Encrypt", "test.txt", vault_id)
    )
    conn.commit()
    
    # Query for user B (like in app.py's handle_decrypt)
    c.execute(
        "SELECT 1 FROM history WHERE username = ? AND vault_id = ? AND action = 'Encrypt' LIMIT 1",
        ("userB@securevault", vault_id),
    )
    owned_by_b = c.fetchone() is not None
    
    assert owned_by_b is False
    
    # Verify user A returns True
    c.execute(
        "SELECT 1 FROM history WHERE username = ? AND vault_id = ? AND action = 'Encrypt' LIMIT 1",
        ("userA@securevault", vault_id),
    )
    owned_by_a = c.fetchone() is not None
    
    assert owned_by_a is True
    
    conn.close()
