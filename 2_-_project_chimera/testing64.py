import hashlib

target = bytes.fromhex("1b40491d416f654000075a465b424c0d4e0a0c53")

def ripemd160(data: bytes):
    try:
        import hashlib as _h
        h = _h.new('ripemd160')
        h.update(data)
        return h.digest()
    except Exception:
        return None  # ripemd160 not available in some Python builds

candidates = [
    "Dr. Alistair Khem","DrAlistairKhem","alistair","AlistairKhem",
    # add more candidates here
]

for s in candidates:
    b = s.encode()
    h_sha1 = hashlib.sha1(b).digest()
    h_sha256_trunc = hashlib.sha256(b).digest()[:20]
    h_rip = ripemd160(b)
    if h_sha1 == target:
        print("SHA1 match:", s)
    if h_rip and h_rip == target:
        print("RIPEMD160 match:", s)
    if h_sha256_trunc == target:
        print("SHA256-trunc(20) match:", s)