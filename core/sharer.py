from Crypto.Protocol.SecretSharing import Shamir

def split_secret(secret_bytes, threshold=3, total=5):
    shares = {i: b'' for i in range(1, total + 1)}
    
    for i in range(0, len(secret_bytes), 16):
        chunk = secret_bytes[i:i+16]
        chunk_shares = Shamir.split(threshold, total, chunk)
        for idx, share_bytes in chunk_shares:
            shares[idx] += share_bytes
            
    binary_shares = []
    for idx, share_data in shares.items():
        full_share = bytes([idx]) + share_data
        binary_str = ''.join(format(b, '08b') for b in full_share)
        binary_shares.append(binary_str)
        
    return binary_shares

def merge_secret(binary_shares):
    parsed_shares = []
    for b_str in binary_shares[:3]: 
        share_bytes = bytes(int(b_str[i:i+8], 2) for i in range(0, len(b_str), 8))
        idx = share_bytes[0]
        data = share_bytes[1:]
        parsed_shares.append((idx, data))
        
    secret = b''
    # FIX: Dynamically check the length of the parsed data instead of hardcoding 64!
    data_length = len(parsed_shares[0][1])
    
    for i in range(0, data_length, 16):
        chunk_shares = [(idx, data[i:i+16]) for idx, data in parsed_shares]
        secret += Shamir.combine(chunk_shares)
        
    return secret