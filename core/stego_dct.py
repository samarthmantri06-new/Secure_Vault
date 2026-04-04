import numpy as np
from PIL import Image

def encode_image(img_path, secret_bits, output_path):
    # Using 'with' ensures the file is automatically closed after reading
    with Image.open(img_path) as img:
        rgb_img = img.convert('RGB')
        pixels = np.array(rgb_img)
        
    flat_pixels = pixels.flatten()
    
    for i, bit in enumerate(secret_bits):
        # FIX: Use 254 (0xFE) instead of ~1 to safely clear the last bit in uint8
        flat_pixels[i] = (flat_pixels[i] & 254) | int(bit)
        
    new_pixels = flat_pixels.reshape(pixels.shape)
    new_img = Image.fromarray(new_pixels.astype('uint8'))
    new_img.save(output_path, "PNG")
    return len(secret_bits)

def decode_image(img_path, num_bits):
    # Using 'with' unlocks the file immediately after we grab the pixels
    with Image.open(img_path) as img:
        rgb_img = img.convert('RGB')
        pixels = np.array(rgb_img).flatten()
        
    bits = ""
    for i in range(num_bits):
        bits += str(pixels[i] & 1)
    return bits