from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

def encrypt_file(file_path):
    key = get_random_bytes(32)
    cipher = AES.new(key, AES.MODE_GCM)
    with open(file_path, 'rb') as f:
        plaintext = f.read()
    ciphertext, tag = cipher.encrypt_and_digest(plaintext)
    # Package: 32 bytes (key) + 16 bytes (nonce) + 16 bytes (tag) = 64 bytes
    secret_package = key + cipher.nonce + tag
    return ciphertext, secret_package

def decrypt_file(ciphertext, secret_package):
    key = secret_package[:32]
    nonce = secret_package[32:48]
    tag = secret_package[48:]
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    return cipher.decrypt_and_verify(ciphertext, tag)