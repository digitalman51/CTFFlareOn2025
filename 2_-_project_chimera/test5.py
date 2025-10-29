import zlib
import lzma
import bz2
import gzip
import lz4.frame
import brotli

data = b'r2b-\r\x9e\xf2\x1fp\x185\x82\xcf\xfc\x90\x14\xf1O\xad#]\xf3\xe2\xc0L\xd0\xc1e\x0c\xea\xec\xae\x11b\xa7\x8c\xaa!\xa1\x9d\xc2\x90'

methods = {
    "zlib": zlib.decompress,
    "lzma": lzma.decompress,
    "bz2": bz2.decompress,
    "gzip": lambda d: gzip.decompress(d),
    "lz4": lambda d: lz4.frame.decompress(d),
    "brotli": brotli.decompress
}

def is_printable_text(b):
    try:
        text = b.decode('utf-8')
        # If at least half of characters are printable, consider it text
        printable_ratio = sum(c.isprintable() for c in text) / max(1, len(text))
        return printable_ratio > 0.5
    except:
        return False

for method_name, decompress_func in methods.items():
    print(f"Trying method: {method_name}")
    found = False
    for offset in range(len(data)):
        try:
            result = decompress_func(data[offset:])
            found = True
            kind = "Text" if is_printable_text(result) else "Binary"
            print(f"\nSuccess with {method_name} at offset {offset} ({kind}):")
            print(f"Decompressed size: {len(result)} bytes")
            if kind == "Text":
                print(f"Content:\n{result.decode('utf-8')}\n")
            else:
                print(f"Hex preview (first 64 bytes):\n{result[:64].hex()}\n")
            break  # stop at first successful decompression for this method
        except Exception:
            continue
    if not found:
        print(f"No valid {method_name} compressed data found.\n")