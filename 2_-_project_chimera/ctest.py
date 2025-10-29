import ctypes
import multiprocessing as mp
from ctypes import c_char_p, c_int, c_void_p, create_string_buffer

# Load shared library (adjust name/path as needed)
lib = ctypes.CDLL('./libtarget.so')  # or 'target.dll' on Windows
# declare signature: int func(char *s1, char *s2, int len);
lib.func.argtypes = [c_char_p, c_char_p, c_int]
lib.func.restype = c_int

a1 = b"\xaf\xaa\xad\xeb\xae\xaa\xec\xa4\xba\xaf\xae" \
     b"\xaa\x8a\xc0\xa7\xb0\xbc\x9a\xba\xa5\xa5\xba" \
     b"\xaf\xb8\x9d\xb8\xf9\xae\x9d\xab\xb4\xbc\xb6" \
     b"\xb3\x90\x9a\xa8"

def test_candidate(args):
    """Test a single byte candidate for position i, return candidate if it changes idx."""
    i, candidate_byte, current_inp_bytes, expected_idx = args
    inp = bytearray(current_inp_bytes)
    inp[i] = candidate_byte
    buf = create_string_buffer(bytes(inp))
    n = lib.func(a1, buf, 0x25)
    idx = (n & 0xff00) >> 8
    if idx != expected_idx:
        return candidate_byte, idx
    return None

def brute_force():
    current = bytearray(37)  # initialized to zeros
    expected_idx = 0x25
    result = bytearray(37)

    for i in range(37):
        print(f"Testing position {i} ...", flush=True)
        # create tasks for all 256 candidates
        tasks = [(i, b, bytes(current), expected_idx) for b in range(256)]
        # parallel test using pool
        with mp.Pool(processes=mp.cpu_count()) as pool:
            for res in pool.imap_unordered(test_candidate, tasks):
                if res is not None:
                    candidate_byte, new_idx = res
                    result[i] = candidate_byte
                    current[i] = candidate_byte
                    expected_idx = new_idx
                    print(f" Found byte {candidate_byte:02x} at pos {i} -> new idx {new_idx}")
                    pool.terminate()  # stop other workers for this position
                    break
    print("Final hex:", " ".join(f"{b:02x}" for b in result))
    # show ascii fallback
    ascii_out = "".join(chr(b) if 0x20 <= b <= 0x7e else "\\x%02x" % b for b in result)
    print("Final ascii:", ascii_out)

if __name__ == "__main__":
    brute_force()