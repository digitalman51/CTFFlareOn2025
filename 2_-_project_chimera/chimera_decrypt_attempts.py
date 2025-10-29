#!/usr/bin/env python3
# chimera_decrypt_attempts.py
# Reconstruct-and-try decryption heuristics for Project Chimera payload.
# Usage: python chimera_decrypt_attempts.py
#
# This script tries multiple key-derivation strategies inferred from the
# static analysis of project_chimera.py's inner code object (ARC4-based).
#
# IMPORTANT: run locally (I will not execute this for you).

import zlib, marshal, sys, getpass, binascii
from hashlib import sha256, md5
import base64

# Paste the two blobs exactly as bytes (from the code object constants).
# Replace these with the exact bytes you extracted from project_chimera.py
# (the script below uses the values discovered during static analysis).
LEAD_RESEARCHER_SIGNATURE = b"\x6d\x1b\x40\x49\x1d\x41\x6f\x65\x40\x07\x5a\x46\x5b\x42\x4c\x0d\x4e\x0a\x0c\x53"
ENC_HEX = "7232622d0d9ef21f70183582cffc9014f14fad235df3e2c04cd0c1650ceaecae1162a78caa21a19dc290"


ENC = binascii.unhexlify(ENC_HEX)
ENCRYPTED_CHIMERA_FORMULA = ENC

# ---------- RC4 (ARC4) implementation ----------
def rc4(key: bytes, data: bytes, drop=0) -> bytes:
    S = list(range(256))
    j = 0
    key = key if isinstance(key, (bytes, bytearray)) else key.encode('utf-8')
    for i in range(256):
        j = (j + S[i] + key[i % len(key)]) & 0xff
        S[i], S[j] = S[j], S[i]
    i = j = 0
    # drop keystream bytes if requested
    for _ in range(drop):
        i = (i + 1) & 0xff
        j = (j + S[i]) & 0xff
        S[i], S[j] = S[j], S[i]
        _ = S[(S[i] + S[j]) & 0xff]
    out = bytearray()
    for ch in data:
        i = (i + 1) & 0xff
        j = (j + S[i]) & 0xff
        S[i], S[j] = S[j], S[i]
        K = S[(S[i] + S[j]) & 0xff]
        out.append(ch ^ K)
    return bytes(out)

# ---------- Key derivation candidates ----------
def xor_derive(sig: bytes, usr: bytes) -> bytes:
    out = bytearray(len(sig))
    for i, b in enumerate(sig):
        out[i] = b ^ usr[i % len(usr)]
    return bytes(out)

def concat(sig: bytes, usr: bytes) -> bytes:
    return sig + usr

def concat_rev(sig: bytes, usr: bytes) -> bytes:
    return usr + sig

def sha256_derive(sig: bytes, usr: bytes) -> bytes:
    return sha256(sig + usr).digest()

def md5_derive(sig: bytes, usr: bytes) -> bytes:
    return md5(sig + usr).digest()

def hex_derive(sig: bytes, usr: bytes) -> bytes:
    return (sig.hex() + usr.decode('latin1', errors='ignore')).encode('latin1', errors='ignore')

def b64_derive(sig: bytes, usr: bytes) -> bytes:
    return base64.b64encode(sig) + usr

# pack strategies in list (name, fn)
strategies = [
    ("sig-as-key", lambda s,u: s),
    ("xor(sig,usr)", xor_derive),
    ("sig+usr", concat),
    ("usr+sig", concat_rev),
    ("sha256(sig+usr)", sha256_derive),
    ("md5(sig+usr)", md5_derive),
    ("hex(sig)+usr", hex_derive),
    ("b64(sig)+usr", b64_derive),
]

# common drop values (ARC4 keystream-drop)
drop_values = [0, 16, 32, 64, 128, 256]

# candidate usernames to try if os.getlogin is not available or you want to brute force a small list.
# Add names you think the original author might have used (e.g., 'alistair', 'khem', 'lead', 'sandbox').
candidate_usernames = [
    None,  # None means "try current OS login"
    "alistair", "alistairkhem", "khem", "drkhem", "lead_researcher",
    "lead", "sandbox", "root", "user", "ubuntu", "admin","password","123456","123456789","12345678","12345","qwerty","abc123","football","monkey","letmein",
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

def try_all(user_hint=None):
    # prepare username bytes
    if user_hint is None:
        try:
            uname = getpass.getuser()
        except Exception:
            uname = None
    else:
        uname = user_hint
    if not uname:
        print("No username available; try specifying one from the candidate list.")
        return
    usr_bytes = uname.encode('utf-8')
    print(f"Trying username: {uname!r}")

    found = []
    for name, fn in strategies:
        key = fn(LEAD_RESEARCHER_SIGNATURE, usr_bytes)
        for drop in drop_values:
            try:
                out = rc4(key, ENCRYPTED_CHIMERA_FORMULA, drop=drop)
            except Exception:
                continue

            # try sensible decodings
            # 1) raw printable text
            try:
                txt = out.decode('utf-8')
                if any(marker in txt for marker in ("I am alive", "secret", "Catalyst", "AUTHENTICATION", "Finalizing")):
                    found.append((name, drop, "utf-8", txt))
            except Exception:
                pass

            # 2) zlib decompress -> maybe marshal / text
            try:
                z = zlib.decompress(out)
                # try as text
                try:
                    txt = z.decode('utf-8', errors='replace')
                    if len(txt) > 1 and any(w in txt for w in ("I am alive","secret","AUTHENTICATION")):
                        found.append((name, drop, "zlib->utf8", txt))
                except Exception:
                    pass
                # try marshal.loads if it is a marshalled code object or tuple
                try:
                    obj = marshal.loads(z)
                    found.append((name, drop, "zlib->marshal", repr(obj)))
                except Exception:
                    pass
            except Exception:
                pass

            # 3) fallback heuristic: many printable bytes
            printable_ratio = sum(1 for b in out if 32 <= b < 127 or b in (9,10,13)) / max(1,len(out))
            if printable_ratio > 0.9:
                try:
                    found.append((name, drop, "likely-plaintext", out.decode('latin1',errors='replace')))
                except Exception:
                    found.append((name, drop, "likely-plaintext", repr(out[:200])))

    return found

def main():
    results = []
    for candidate in candidate_usernames:
        if candidate is None:
            # try OS login
            try:
                uname = getpass.getuser()
            except Exception:
                uname = None
        else:
            uname = candidate
        if not uname:
            continue
        res = try_all(user_hint=uname)
        if res:
            print(f"\n=== Results for username {uname!r} ===")
            for r in res:
                name, drop, tag, preview = r
                print(f"strategy={name}, drop={drop}, kind={tag}\n  preview:\n{preview}\n")
            results.extend(res)
    if not results:
        print("No clear plaintext found with the tried heuristics. You can:")
        print(" - provide the exact biometric/passphrase used to derive the key, or")
        print(" - add more username candidates to `candidate_usernames` above, or")
        print(" - ask me to try different derivation rules (I can expand heuristics).")
    else:
        print("Done — some candidates returned. Check the previews above.")

if __name__ == '__main__':
    main()
