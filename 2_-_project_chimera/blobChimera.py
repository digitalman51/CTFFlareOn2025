import ast
import base64
import zlib
import marshal
import re
from pathlib import Path

code = Path("project_chimera.py").read_text(errors="ignore")

# --- Try to find any long base64/base85 looking strings ---
for m in re.finditer(r"([A-Za-z0-9!#$%&'()*+\-;<=>?@^_`{|}~]{60,})", code):
    print(f"Found candidate block (len={len(m.group(1))}) starting:\n{m.group(1)[:80]}...\n")

# --- Parse Python literals (no execution) ---
tree = ast.parse(code)
for node in ast.walk(tree):
    if isinstance(node, ast.Assign):
        for t in node.targets:
            if isinstance(t, ast.Name):
                if t.id in ("LEAD_RESEARCHER_SIGNATURE", "ENCRYPTED_CHIMERA_FORMULA"):
                    val = ast.literal_eval(node.value)
                    print(f"{t.id}: type={type(val)}, len={len(val) if hasattr(val,'__len__') else 'N/A'}")
                    if isinstance(val, bytes):
                        preview = " ".join(f"{b:02x}" for b in val[:16])
                        print(f"  bytes preview: {preview}{'...' if len(val)>16 else ''}")