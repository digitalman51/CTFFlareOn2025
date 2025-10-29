import marshal, dis
with open("chimera_payload_fixed_off0.pyc", "rb") as f:
    f.read(16)          # skip .pyc header
    code = marshal.load(f)
dis.dis(code)