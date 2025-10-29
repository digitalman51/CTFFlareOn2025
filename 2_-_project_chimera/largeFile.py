#!/usr/bin/env python3
"""
large_offline_attack.py

Usage:
  python3 large_offline_attack.py --wordlist /path/to/rockyou.txt --workers 8 --mode full --out result.txt

Description:
  - Loads the encrypted blob and signature constants embedded here (from provided files).
  - Iterates the provided wordlist and generates many candidate keys & derived keys:
      * raw candidate, hex(candidate), base64(candidate)
      * HMAC-SHA1(SIG, candidate) and HMAC-SHA1(candidate, SIG)
      * SHA1(candidate + SIG), SHA1(SIG + candidate)
      * PBKDF2-HMAC-SHA1(candidate, salt=SIG) with iterations [100,1000,10000]
      * PBKDF2-HMAC-SHA256(candidate, salt=SIG) with iterations [100,1000,10000]
      * Optionally, try candidate@flare-on.com variants (if --domain flag set)
  - Uses multiprocessing to distribute attempts across workers.
  - For each derived key, runs RC4 decrypt against the encrypted blob, then tries zlib.decompress.
  - On a successful decompress (or readable ASCII), prints and stores the result to an output file and exits.
  - Works offline; designed to be run on your machine where you provide the wordlist (rockyou or other). ...

(Full script continues — pasted in full)
"""
import argparse, binascii, base64, hashlib, hmac, zlib, os, sys, multiprocessing, time
from multiprocessing import Pool, Manager

# --- Constants extracted from testing2.py ---
SIG_HEX = "6d1b40491d416f6540075a465b424c0d4e0a0c53"
ENC_HEX = "7232622d0d9ef21f70183582cffc9014f14fad235df3e2c04cd0c1650ceaecae1162a78caa21a19dc290"

SIG = binascii.unhexlify(SIG_HEX)
ENC = binascii.unhexlify(ENC_HEX)

# --- RC4 implementation ---
def rc4(key: bytes, data: bytes) -> bytes:
    S = list(range(256))
    j = 0
    if not isinstance(key, (bytes, bytearray)):
        key = key if key is not None else b''
        key = str(key).encode('utf-8', errors='ignore')
    key_bytes = key
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
        if len(dec) > 0 and all(32 <= b < 127 or b in (9,10,13) for b in dec):
            return ("printable", dec.decode('latin1'))
        return (None, None)

# --- Key derivation routines ---
def derive_candidates_from_word(word: str, domain_variants=True):
    """Yield raw candidate byte-forms for a given input word (strings)."""
    ws = set()
    w = word.strip()
    if not w:
        return []
    ws.add(w)
    ws.add(w.lower()); ws.add(w.upper()); ws.add(w.title())
    if domain_variants and "@" not in w:
        ws.add(w + "@flare-on.com")
        ws.add(w + "@flareon.com")
    # leet simple
    lw = w.replace("a","@").replace("o","0").replace("i","1").replace("e","3").replace("s","5")
    ws.add(lw)
    # numeric suffixes common
    for n in ("1","12","123","2025","42","007"):
        ws.add(f"{w}{n}"); ws.add(f"{w}_{n}"); ws.add(f"{w}-{n}")
    # add SHA1/MD5 hex forms
    try:
        ws.add(hashlib.sha1(w.encode('utf-8')).hexdigest())
        ws.add(hashlib.md5(w.encode('utf-8')).hexdigest())
    except Exception:
        pass
    # return as bytes
    return [s.encode('utf-8') for s in ws]

def generate_derived_keys(candidate_bytes):
    """Given a candidate in bytes, generate a list of derived key bytes to try."""
    res = []
    cb = candidate_bytes
    # raw
    res.append(cb)
    # ascii hex form (string)
    try:
        res.append(cb.hex().encode())
    except Exception:
        pass
    # base64 form
    res.append(base64.b64encode(cb))
    # HMAC variants
    try:
        res.append(hmac.new(SIG, cb, hashlib.sha1).digest())
        res.append(hmac.new(cb, SIG, hashlib.sha1).digest())
        # hex forms
        res.append(hmac.new(SIG, cb, hashlib.sha1).hexdigest().encode())
        res.append(hmac.new(cb, SIG, hashlib.sha1).hexdigest().encode())
    except Exception:
        pass
    # sha1 concat combos
    res.append(hashlib.sha1(cb + SIG).digest())
    res.append(hashlib.sha1(SIG + cb).digest())
    res.append(hashlib.sha1(cb + SIG).hexdigest().encode())
    res.append(hashlib.sha1(SIG + cb).hexdigest().encode())
    # PBKDF2 variants (small iterations by default, adjustable)
    for iters in (100, 1000, 10000):
        try:
            res.append(hashlib.pbkdf2_hmac('sha1', cb, SIG, iters))
            res.append(hashlib.pbkdf2_hmac('sha256', cb, SIG, iters))
        except Exception:
            pass
    # dedupe preserving order
    seen = set(); out = []
    for r in res:
        if not isinstance(r, (bytes,bytearray)):
            rr = str(r).encode('utf-8')
        else:
            rr = r
        if rr in seen: continue
        seen.add(rr); out.append(rr)
    return out

# Worker function for multiprocessing
def worker_job(args):
    """Process a chunk of words; returns a success tuple or None."""
    words_chunk, worker_id, opts = args
    attempts = 0
    for w in words_chunk:
        candidates = derive_candidates_from_word(w, domain_variants=opts['domain_variants'])
        for cand in candidates:
            derived = generate_derived_keys(cand)
            for dk in derived:
                attempts += 1
                status, out = try_decrypt_with_key(dk)
                if status:
                    return ('found', w, cand, dk, status, out, attempts, worker_id)
    return ('none', attempts, worker_id)

def chunked_iterable(iterable, n):
    """Yield successive n-sized chunks from iterable."""
    chunk = []
    for item in iterable:
        chunk.append(item)
        if len(chunk) >= n:
            yield chunk
            chunk = []
    if chunk:
        yield chunk

def main():
    parser = argparse.ArgumentParser(description="Large offline RC4+zlib attack against embedded blob")
    parser.add_argument("--wordlist", required=True, help="Path to wordlist file (one word per line)")
    parser.add_argument("--workers", type=int, default=max(1, multiprocessing.cpu_count()-1), help="Number of worker processes")
    parser.add_argument("--chunk-size", type=int, default=200, help="Number of words per chunk assigned to worker")
    parser.add_argument("--domain-variants", action="store_true", help="Try candidate@flare-on.com variants")
    parser.add_argument("--out", default="attack_result.txt", help="File to write success result to")
    parser.add_argument("--max-attempts", type=int, default=0, help="Optional cap on total RC4 attempts (0 = unlimited)")
    parser.add_argument("--mode", choices=['fast','full'], default='full', help="fast = fewer derivations, full = full derivation set")
    args = parser.parse_args()

    # load wordlist
    if not os.path.exists(args.wordlist):
        print("Wordlist not found:", args.wordlist); sys.exit(2)
    with open(args.wordlist, 'r', encoding='utf-8', errors='ignore') as f:
        words = [line.strip() for line in f if line.strip()]

    total_words = len(words)
    print(f"[+] Loaded {total_words} words from {args.wordlist}")
    workers = args.workers

    manager = Manager()
    pool = Pool(processes=workers)
    # prepare tasks: split words into chunks
    chunk_size = args.chunk_size
    tasks = []
    for chunk in chunked_iterable(words, chunk_size):
        tasks.append((chunk, 0, {'domain_variants': args.domain_variants, 'mode': args.mode}))

    print(f"[+] Dispatching {len(tasks)} tasks to {workers} workers (chunk size {chunk_size})")
    start = time.time()
    results = pool.imap_unordered(worker_job, tasks)
    total_attempts = 0
    try:
        for res in results:
            if res is None: continue
            if res[0] == 'found':
                # res = ('found', w, cand, dk, status, out, attempts, worker_id)
                _, word, cand, dk, status, out, attempts, wid = res
                elapsed = time.time() - start
                print(f"[!] SUCCESS by worker {wid} on word {word!r} (attempts this worker: {attempts})")
                print("Derived key repr (truncated):", dk[:64])
                print("Status:", status)
                print("Output (first 1000 chars):\n", out[:1000])
                # write to output file
                with open(args.out, 'w', encoding='utf-8') as fout:
                    fout.write("SUCCESS\n")
                    fout.write(f"word={word!r}\n")
                    fout.write(f"candidate_bytes={cand!r}\n")
                    fout.write(f"derived_key={dk!r}\n")
                    fout.write(f"status={status}\n")
                    fout.write("output:\n")
                    fout.write(out)
                pool.terminate()
                print(f"[+] Result written to {args.out}")
                return
            else:
                # ('none', attempts, worker_id)
                total_attempts += res[1] if isinstance(res[1], int) else 0
    except KeyboardInterrupt:
        print("Interrupted by user; terminating workers...")
        pool.terminate()
    finally:
        pool.close()
        pool.join()

    elapsed = time.time() - start
    print(f"Finished. Total attempts (approx): {total_attempts}. Time elapsed: {elapsed:.1f}s")
    print("No successful decryptions found. You can rerun with different wordlist or options.")

if __name__ == "__main__":
    main()