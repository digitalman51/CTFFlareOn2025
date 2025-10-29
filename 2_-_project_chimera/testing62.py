# run this locally in a safe, offline Python environment
import zlib, base64, marshal, hashlib

# Replace these with the bytes from the code (example variable names)
LEAD_RESEARCHER_SIGNATURE = bytes.fromhex("6d1b40491d416f654000075a465b424c0d4e0a0c53")  # put exact 20-byte hex here
ENCRYPTED_CHIMERA_FORMULA = bytes.fromhex("7232622d0d9ef21f70183582cffc9014f14fad235df3...")      # put exact encrypted-blob hex here

# RC4 implementation
def rc4(key, data):
    S = list(range(256))
    j = 0
    key_bytes = key if isinstance(key, bytes) else key.encode()
    for i in range(256):
        j = (j + S[i] + key_bytes[i % len(key_bytes)]) & 0xff
        S[i], S[j] = S[j], S[i]
    i = j = 0
    out = bytearray()
    for b in data:
        i = (i + 1) & 0xff
        j = (j + S[i]) & 0xff
        S[i], S[j] = S[j], S[i]
        out.append(b ^ S[(S[i] + S[j]) & 0xff])
    return bytes(out)

# Try using the signature directly as RC4 key and then zlib decompress
decrypted = rc4(LEAD_RESEARCHER_SIGNATURE, ENCRYPTED_CHIMERA_FORMULA)
try:
    print(zlib.decompress(decrypted).decode('utf-8'))
except Exception as e:
    print("Decompression/decoding failed — wrong key or different derivation:", e)