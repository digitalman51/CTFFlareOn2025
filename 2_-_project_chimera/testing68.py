import ast, base64, zlib, marshal, types, asyncio, json, os, sys, binascii
from collections import deque

OUT_JSON = "instrumented_output.json"
OUT_TXT  = "instrumented_output.txt"

# --- Safety: helper mocks to minimize side-effects ---
class ARC4Mock:
    instances = []
    @classmethod
    def reset(cls):
        cls.instances.clear()
    def __init__(self, key=None):
        self.key = key
        ARC4Mock.instances.append({"call":"init", "key":repr(key)})
    def decrypt(self, data):
        ARC4Mock.instances.append({"call":"decrypt", "key":repr(self.key), "data_hex":binascii.hexlify(data).decode()})
        # return empty bytes (we're only recording calls)
        return b''
    @staticmethod
    def decrypt_static(key, data):
        ARC4Mock.instances.append({"call":"decrypt_static", "key":repr(key), "data_hex":binascii.hexlify(data).decode()})
        return b''

class SafeOS:
    def __init__(self, login):
        self._login = login
    def getlogin(self):
        return self._login
    def getenv(self, k, d=None):
        return d
    # block other dangerous calls by not providing them

class SafeGetpass:
    def __init__(self, user):
        self._user = user
    def getuser(self):
        return self._user

# Minimal safe builtin set (intentionally small)
SAFE_BUILTINS = {
    "None": None, "True": True, "False": False,
    "str": str, "bytes": bytes, "int": int, "float": float,
    "bool": bool, "len": len, "range": range, "enumerate": enumerate,
    "list": list, "tuple": tuple, "dict": dict, "set": set,
    "chr": chr, "ord": ord, "min": min, "max": max, "sum": sum,
    # Print will collect printed output
}

def load_blob2_from_source(path="testing2.py"):
    src = open(path, "r", encoding="utf-8", errors="ignore").read()
    # try AST extract of blob2 literal
    tree = ast.parse(src, filename=path)
    blob2_text = None
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "blob2":
                    val = node.value
                    # Common case: a Constant string
                    if isinstance(val, ast.Constant):
                        blob2_text = val.value if isinstance(val.value, str) else None
                    # fallback: regex search
    if blob2_text is None:
        import re
        m = re.search(r"blob2\s*=\s*(b?)(?P<quote>['\"]{1,3})(?P<body>.*?)(?P=quote)", src, re.S)
        if m:
            body = m.group("body")
            # If literal contains b'...' with escapes we need raw bytes; here assume plain ascii
            blob2_text = body
    if blob2_text is None:
        raise RuntimeError("Tidak menemukan literal blob2 dalam testing2.py")
    return blob2_text.encode("latin1")

def safe_globals_for(login_value):
    printed = []
    # copy builtins but override print
    safe_builtins = SAFE_BUILTINS.copy()
    safe_builtins["print"] = lambda *a, **kw: printed.append(" ".join(map(str,a)))
    g = {"__builtins__": safe_builtins}
    # mocks
    g["os"] = SafeOS(login_value)
    g["getpass"] = SafeGetpass(login_value)
    g["ARC4"] = ARC4Mock
    g["arc4"] = ARC4Mock
    # common harmless mocks
    g["asyncio"] = __import__("asyncio")
    g["random"] = types.SimpleNamespace(choice=lambda seq: seq[0])
    g["pyjokes"] = types.SimpleNamespace(get_joke=lambda: "jk")
    g["art"] = types.SimpleNamespace(tprint=lambda *a, **k: None)
    g["cowsay"] = types.SimpleNamespace(cow=lambda s: s)
    # sys.exit replaced
    g["sys"] = types.SimpleNamespace(exit=lambda *a, **k: (_ for _ in ()).throw(SystemExit("exit called")))
    return g, printed

def find_codeobj(root, name):
    q = [root]
    seen = set()
    while q:
        co = q.pop()
        if id(co) in seen: continue
        seen.add(id(co))
        if co.co_name == name:
            return co
        for c in co.co_consts:
            if isinstance(c, types.CodeType):
                q.append(c)
    return None

def main():
    print("Loading blob2 from testing2.py ...")
    blob2_bytes = load_blob2_from_source("testing2.py")
    try:
        decoded = base64.b85decode(blob2_bytes.replace(b"\n",b"").replace(b"\r",b""))
    except Exception as e:
        print("Gagal decode base85:", e); return
    try:
        decompressed = zlib.decompress(decoded)
    except Exception as e:
        print("Gagal zlib.decompress:", e); return

    # write decompressed for inspection
    with open("decompressed.bin", "wb") as f:
        f.write(decompressed)
    print("Wrote decompressed.bin (marshal bytes). Attempting marshal.loads ...")
    try:
        code_obj = marshal.loads(decompressed)
    except Exception as e:
        print("marshal.loads gagal:", e); return

    act_co = find_codeobj(code_obj, "activate_catalyst")
    if act_co is None:
        print("Tidak menemukan activate_catalyst di bytecode.")
        return

    print("Ditemukan code object activate_catalyst. Membuat function dan menjalankan dengan mocks.")
    results = []
    # candidates: kamu bisa tambahkan nama/email di sini sebelum menjalankan
    candidates = [
        "alistair", "alistair.khem", "alistair_khem", "dr.alistair",
        "alistair@flare-on.com", "alistair.khem@flare-on.com", "lead.researcher@flare-on.com",
        "teddy", "teddy.zugana"
    ]

    for cand in candidates:
        print(f"\n-- Running candidate login: {cand}")
      
        try:
            ARC4Mock.reset()
            g, printed = safe_globals_for(cand)
            # Build function object bound to our safe globals
            func = types.FunctionType(act_co, g)
            entry = {"candidate": cand, "status": None, "printed": [], "arc4_calls": []}
            # act_co is often async; if so, run with asyncio.run
            res = None
            if asyncio.iscoroutinefunction(func):
                # run via asyncio.run (safe local process)
                asyncio.run(func())   # if it triggers SystemExit, will propagate
            else:
                # sync function
                func()
            entry["status"] = "ran_ok"
        except SystemExit as se:
            entry["status"] = "system_exit"
            printed.append(f"SystemExit: {se}")
        except Exception as e:
            entry["status"] = "error"
            printed.append(f"Exception: {type(e).__name__}: {e}")
        entry["printed"] = printed[:]
        # record ARC4Mock instances
        entry["arc4_calls"] = list(ARC4Mock.instances)
        results.append(entry)

    # save results
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    with open(OUT_TXT, "w", encoding="utf-8") as f:
        for r in results:
            f.write(f"Candidate: {r['candidate']} | status: {r['status']}\n")
            f.write("Printed:\n")
            for p in r["printed"]:
                f.write("  " + p + "\n")
            f.write("ARC4 records:\n")
            for a in r["arc4_calls"]:
                f.write("  " + repr(a) + "\n")
            f.write("\n---\n\n")
    print("\nDone. Results written to", OUT_JSON, "and", OUT_TXT)
    print("Silakan periksa file tersebut. Jika kamu ingin kandidat lain tambahkan di list 'candidates' di file ini dan jalankan ulang.")

if __name__ == "__main__":
    main()