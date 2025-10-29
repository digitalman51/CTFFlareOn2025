# KDF/HMAC-style derivation attempts (visible execution)
# Uses the extracted signature and encrypted blob, generates candidate keys (same family as before),
# and applies several derivation functions per candidate:
#  - HMAC-SHA1(sig, candidate)
#  - HMAC-SHA1(candidate, sig)
#  - SHA1(candidate + sig)
#  - SHA1(sig + candidate)
#  - PBKDF2-HMAC-SHA1(candidate, salt=sig, iterations=100,1000,4096)
#  - PBKDF2-HMAC-SHA256(candidate, salt=sig, iterations=100,1000)
# For each derived key we try it directly as RC4 key (raw bytes) and also try hex/hexdigest/base64 forms.
# If any key produces zlib-decompressible plaintext, it's printed.
#
# Note: this is an exploratory run with a moderate number of candidates (~17k) and derivations.
# It may try up to a couple hundred thousand RC4 attempts; we'll cap total attempts to keep runtime reasonable.
# Executing now.

import binascii, zlib, hashlib, hmac, base64, time
from typing import List
import itertools

SIG_HEX = "6d1b40491d416f6540075a465b424c0d4e0a0c53"
ENC_HEX = "7232622d0d9ef21f70183582cffc9014f14fad235df3e2c04cd0c1650ceaecae1162a78caa21a19dc290"

SIG = binascii.unhexlify(SIG_HEX)
ENC = binascii.unhexlify(ENC_HEX)

def rc4(key: bytes, data: bytes) -> bytes:
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
    try:
        plain = zlib.decompress(dec)
        try:
            text = plain.decode('utf-8')
        except Exception:
            text = repr(plain)
        return ("zlib_ok", text)
    except Exception:
        if len(dec) > 0 and all(32 <= b < 127 or b in (9,10,13) for b in dec):
            return ("printable", dec.decode('latin1'))
        return (None, None)

# Candidate generation (reuse of previous list)
common_passwords = [
"password","123456","123456789","12345678","12345","qwerty","abc123","football","monkey","letmein",
"dragon","111111","baseball","iloveyou","master","sunshine","ashley","bailey","welcome","admin",
"flower","shadow","purple","hottie","lovely","loveme","zaq1zaq1","password1","passw0rd","secret",
"trustno1","thomas","harley","qazwsx","michael","superman","internet","pokemon","starwars","freedom",
"whatever","qwerty123","1q2w3e4r","cheese","cheesecake","chelsea","buster","soccer","harry","ginger",
"pepper","mickey","cookie","alex","mark","jack","daniel","jessica","liverpool","qwertyuiop","1qaz2wsx",
"1q2w3e","000000","121212","access","password123","welcome1","admin123","admin1","administrator",
"1234","1234567","1111","0000","loveyou","7777777","88888888","1q2w3e4r5t","asdfgh","q1w2e3r4",
"pass","shadow1","tigger","robert","football1","baseball1","maggie","matthew","jordan","jennifer",
"jasmine","jordan23","flower123","hello","iloveu","summer","autumn","winter","spring","office",
"creator","contact","manager","support","flare","flareon","flare-on","flareon2025","flare2025","flareon!",
"flare_on","flare.on","flareon123","flareon1","flareon!123","research","researcher","lead","lead1",
"lead_researcher","lead.researcher","lead-researcher","alistair","alistairkhem","alistair.khem",
"alistair123","alistair1","alistair2025","alistair_khem","alistair-khem","alistair_khem1","alistair!",
"khem","khem123","khem1","dralistair","dr.alistair","dr_alistair","dralistairkhem","dr_khem",
"adminflare","flareadmin","admin@flare-on.com","research@flare-on.com","lead@flare-on.com",
"alistair@flare-on.com","alistair@flare-on.com","a.khem@flare-on.com","a.khem@flareon.com",
"alistair.khem@flare-on.com","alistair.khem@flareon.com","alistairkhem@flareon.com",
"alistairkhem@flare-on.com","alistairkhem@flareon2025","flareonadmin",
"flareonlead","secretformula","chimera","chimera123","chimera!","formula","secretformula123",
"secret!","password!","password!123","pass123","letmein123","letmein!","biometric","biometrickey",
"biometric123","biokey","bio_key","fingerprint","fingerprint123","fingerprint!","signature","sig123",
"sig!","sig2025","6d1b40491d416f6540075a465b424c0d4e0a0c53",
]

def generate_variants(words, domain="@flare-on.com", max_numeric_suffix=20):
    variants = []
    for w in words:
        variants.append(w)
        if "@" not in w:
            variants.append(w + domain)
            variants.append(w + domain.replace("flare-on","flareon"))
            variants.append(w + "@flareon.com")
        lw = w.replace("a","@").replace("o","0").replace("i","1").replace("e","3").replace("s","5")
        if lw != w: variants.append(lw)
        variants.append(w.lower()); variants.append(w.upper()); variants.append(w.title())
        for n in (1,12,123,2025,42):
            variants.append(f"{w}{n}"); variants.append(f"{w}_{n}"); variants.append(f"{w}-{n}")
        for n in range(2, min(max_numeric_suffix,20)):
            variants.append(f"{w}{n}")
    # hashed variants
    for w in words[:200]:
        b = w.encode('utf-8')
        variants.append(hashlib.sha1(b).hexdigest())
        variants.append(hashlib.md5(b).hexdigest())
        variants.append(hashlib.sha1(b).digest())
        variants.append(hashlib.md5(b).digest())
    # include raw signature bytes + combos
    variants.append(SIG)
    base = list(variants)[:5000]
    for v in base:
        try:
            vb = v if isinstance(v, (bytes,bytearray)) else str(v).encode('utf-8')
            variants.append(vb + SIG); variants.append(SIG + vb)
        except:
            pass
    # dedupe & return bytes
    seen = set(); out = []
    for v in variants:
        key = v if isinstance(v, (bytes,bytearray)) else v.encode('utf-8')
        if key in seen: continue
        seen.add(key); out.append(key)
    return out

candidates = generate_variants(common_passwords, domain="@flare-on.com", max_numeric_suffix=30)
print(f"[+] Generated {len(candidates)} raw candidates.")

# Derivation functions to attempt
def derive_hmac_sha1(key, msg): return hmac.new(key, msg, hashlib.sha1).digest()
def derive_hmac_sha1_hex(key, msg): return hmac.new(key, msg, hashlib.sha1).hexdigest().encode()
def derive_sha1(a): return hashlib.sha1(a).digest()
def derive_sha1_hex(a): return hashlib.sha1(a).hexdigest().encode()
def derive_pbkdf2_sha1(password, salt, iterations): return hashlib.pbkdf2_hmac('sha1', password, salt, iterations)
def derive_pbkdf2_sha256(password, salt, iterations): return hashlib.pbkdf2_hmac('sha256', password, salt, iterations)

derivations = []

# For each candidate, we will produce several derived keys
def generate_derived_keys(candidate_bytes):
    res = []
    cb = candidate_bytes
    # direct candidate
    res.append(cb)
    # candidate hex/ascii forms
    try:
        res.append(cb.hex().encode())
    except:
        pass
    # HMAC variants (sig as key, candidate as msg) and reverse
    res.append(derive_hmac_sha1(SIG, cb))
    res.append(derive_hmac_sha1(cb, SIG))
    res.append(derive_hmac_sha1_hex(SIG, cb))
    res.append(derive_hmac_sha1_hex(cb, SIG))
    # SHA1 concatenations
    res.append(derive_sha1(cb + SIG))
    res.append(derive_sha1(SIG + cb))
    res.append(derive_sha1_hex(cb + SIG))
    res.append(derive_sha1_hex(SIG + cb))
    # PBKDF2 variants (small iterations)
    for iters in (100, 1000, 4096):
        try:
            res.append(derive_pbkdf2_sha1(cb, SIG, iters))
        except Exception:
            pass
    for iters in (100, 1000):
        try:
            res.append(derive_pbkdf2_sha256(cb, SIG, iters))
        except Exception:
            pass
    # base64 of some digests
    res.append(base64.b64encode(hashlib.sha1(cb).digest()))
    res.append(base64.b64encode(hashlib.md5(cb).digest()))
    # ensure bytes uniqueness
    uniq = []
    seen = set()
    for r in res:
        if not isinstance(r, (bytes,bytearray)):
            rr = str(r).encode('utf-8')
        else:
            rr = r
        if rr in seen: continue
        seen.add(rr); uniq.append(rr)
    return uniq

# Iterate, apply derivations and test. Cap total RC4 attempts to avoid runaway runtime.
max_total_attempts = 200000
attempts = 0
start = time.time()
found = []
for idx, cand in enumerate(candidates):
    derived_keys = generate_derived_keys(cand)
    for dk in derived_keys:
        # try raw derived bytes
        status, out = try_decrypt_with_key(dk)
        attempts += 1
        if status:
            found.append((cand, dk, status, out))
            print(f"[FOUND] candidate {cand!r} derived key {dk!r} -> {status}")
            print(out[:1000])
            break
        # also try hex/ascii form of dk
        try:
            status, out = try_decrypt_with_key(dk.hex().encode())
            attempts += 1
            if status:
                found.append((cand, dk.hex().encode(), status, out))
                print(f"[FOUND] candidate {cand!r} derived key hex {dk.hex().encode()!r} -> {status}")
                print(out[:1000])
                break
        except Exception:
            pass
        # try base64
        try:
            status, out = try_decrypt_with_key(base64.b64encode(dk))
            attempts += 1
            if status:
                found.append((cand, base64.b64encode(dk), status, out))
                print(f"[FOUND] candidate {cand!r} derived key base64 {base64.b64encode(dk)!r} -> {status}")
                print(out[:1000])
                break
        except Exception:
            pass
        if attempts >= max_total_attempts:
            break
    if found or attempts >= max_total_attempts:
        break
    if idx % 2000 == 0 and idx>0:
        elapsed = time.time() - start
        print(f"[+] processed {idx} candidates, attempts={attempts}, rate ~{attempts/elapsed:.1f}/s")
elapsed = time.time() - start
print(f"\nDone. Candidates processed: {idx+1}. Total RC4 attempts: {attempts}. Time: {elapsed:.1f}s. Found: {len(found)}")

if found:
    for cand, dk, status, out in found:
        print("\n=== SUCCESS ===")
        print("candidate repr:", cand[:200])
        print("derived key repr:", dk[:200])
        print("status:", status)
        print("output (first 2000 chars):\n", out[:2000])
else:
    print("\nNo successful decryptions found with these KDF/HMAC derivations and candidate set.")