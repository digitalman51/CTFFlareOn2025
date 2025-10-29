#!/usr/bin/env python3
# dump_pyc_consts.py
# Usage: python3.13 dump_pyc_consts.py chimera_payload3.pyc output_dir

import sys, os, marshal, types, argparse, binascii

def walk_code_consts(co, found):
    # co is a code object
    for c in co.co_consts:
        if isinstance(c, types.CodeType):
            walk_code_consts(c, found)
        else:
            found.append(c)

def dump_pyc_consts(pyc_path, outdir):
    with open(pyc_path, "rb") as f:
        data = f.read()
    header = data[:16]
    payload = data[16:]
    try:
        code = marshal.loads(payload)
    except Exception as e:
        print("Error: failed to marshal.loads payload:", e)
        return 1

    consts = []
    walk_code_consts(code, consts)

    os.makedirs(outdir, exist_ok=True)
    summary = []
    bytes_count = 0
    for i, c in enumerate(consts):
        typ = type(c).__name__
        summary.append((i, typ, None if c is None else (len(c) if hasattr(c,'__len__') else None)))
        if isinstance(c, (bytes, bytearray)):
            bytes_count += 1
            raw_name = os.path.join(outdir, f"const_{i}.bin")
            hex_name = os.path.join(outdir, f"const_{i}.hex")
            with open(raw_name, "wb") as rw:
                rw.write(bytes(c))
            with open(hex_name, "w") as hx:
                hx.write(binascii.hexlify(bytes(c)).decode())
            print(f"Wrote bytes const #{i}: {raw_name} ({len(c)} bytes)")
        elif isinstance(c, str):
            # save strings too for convenience
            txt_name = os.path.join(outdir, f"const_{i}.txt")
            with open(txt_name, "w", encoding="utf-8", errors="ignore") as t:
                t.write(c)
    # summary file
    with open(os.path.join(outdir, "constants_summary.txt"), "w", encoding="utf-8") as s:
        s.write("index,type,length\n")
        for idx, typ, ln in summary:
            s.write(f"{idx},{typ},{ln if ln is not None else ''}\n")
    print(f"\nDone. Found {len(consts)} constants, of which {bytes_count} were bytes objects.")
    print(f"Constants and dumps in: {outdir}")
    return 0

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("pyc", help="path to .pyc file")
    p.add_argument("outdir", help="directory to write extracted constants")
    args = p.parse_args()
    sys.exit(dump_pyc_consts(args.pyc, args.outdir))
