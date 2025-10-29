# reproduce_attempts.py
# Reproduces the decryption attempts I ran against the uploaded testing2.py constants.
# Paste the two hex values exactly as shown above into the SIG_HEX and ENC_HEX variables.

import binascii, zlib, itertools, hashlib
from typing import Iterable

SIG_HEX = "6d1b40491d416f6540075a465b424c0d4e0a0c53"
ENC_HEX = "7232622d0d9ef21f70183582cffc9014f14fad235df3e2c04cd0c1650ceaecae1162a78caa21a19dc290"

SIG = binascii.unhexlify(SIG_HEX)
ENC = binascii.unhexlify(ENC_HEX)

def rc4(key: bytes, data: bytes) -> bytes:
    # simple RC4/ARC4 implementation
    S = list(range(256))
    j = 0
    key_bytes = key if isinstance(key, (bytes, bytearray)) else key.encode()
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

def try_decrypt_with_key(key_bytes: bytes):
    dec = rc4(key_bytes, ENC)
    # try zlib decompress
    try:
        plain = zlib.decompress(dec)
        try:
            text = plain.decode('utf-8')
        except Exception:
            text = repr(plain)
        return ("zlib_ok", text)
    except Exception:
        # also check for printable ASCII
        if all(32 <= b < 127 or b in (9,10,13) for b in dec):
            return ("printable", dec.decode('latin1'))
        return (None, None)

# ---------------------------
# Candidate key generation
# ---------------------------

# Small deterministic set of candidates I tried in the automated pass:
base_candidates = [
    SIG,                          # raw signature bytes
    SIG.hex().encode(),           # signature hex as ASCII
    binascii.b2a_base64(SIG).strip(), # signature base64
    SIG[::-1],                    # reversed raw signature
    b"Dr. Alistair Khem",
    b"Dr Alistair Khem",
    b"AlistairKhem",
    b"alistairkhem",
    b"alistair.khem",
    b"DrAlistairKhem",
    b"ALISTAIRKHEM",
    b"alistair",
    b"khem",
    b"ARC4" + SIG,                # 'ARC4' prefixed
    b"ARC4" + SIG.hex().encode(),
]

# add hashed variants (SHA1 / MD5) of a few names
names = [b"Dr. Alistair Khem", b"Alistair Khem", b"alistairkhem", b"alistair", b"khem"]
for n in names:
    base_candidates.append(hashlib.sha1(n).digest())
    base_candidates.append(hashlib.md5(n).digest())
    base_candidates.append(hashlib.sha1(n).hexdigest().encode())
    base_candidates.append(hashlib.md5(n).hexdigest().encode())

# Also some derived combos
extra = []
for b in list(base_candidates)[:]:
    extra.append(b + SIG)        # name + signature
    extra.append(SIG + b)        # signature + name
    extra.append(b * 2)          # repeated
base_candidates += extra

# truncate/pad to reasonable lengths if needed (rc4 accepts any key bytes)
seen = set()
candidates = []
for b in base_candidates:
    if not isinstance(b, (bytes, bytearray)):
        b = str(b).encode()
    if b in seen:
        continue
    seen.add(b)
    candidates.append(b)

# ---------------------------
# Run attempts
# ---------------------------
found = []
for idx, key in enumerate(candidates):
    status, out = try_decrypt_with_key(key)
    if status:
        print(f"[+] Candidate #{idx} key={repr(key)[:180]} -> {status}")
        print("    Output (first 500 chars):")
        print(out[:500])
        found.append((key, status, out))

if not found:
    print("No candidate in this set produced a zlib-decompressible plaintext or clear ASCII output.")
else:
    print("Successful candidates:", found)