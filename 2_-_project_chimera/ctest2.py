import base64
import zlib
import marshal
import importlib.util
import sys
import struct
import time
import types # Added 'types' for the execution part, as the code object might be a function

# --- Original Blobs ---
# ------------------------------
blob1 = b"\xe3\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x05\x00\x00\x00\x00\x00\x00\x00\xf3\x02\x01\x00\x00\x97\x00d\x00d\x01l\x00Z\x00d\x00d\x01l\x01Z\x01d\x00d\x01l\x02Z\x02d\x00d\x01l\x03Z\x03d\x02Z\x04\x02\x00e\x05d\x03\xab\x01\x00\x00\x00\x00\x00\x00\x01\x00\x02\x00e\x05d\x04\xab\x01\x00\x00\x00\x00\x00\x00\x01\x00\x02\x00e\x00j\x0c\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00e\x04\xab\x01\x00\x00\x00\x00\x00\x00Z\x07\x02\x00e\x01j\x10\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00e\x07\xab\x01\x00\x00\x00\x00\x00\x00Z\t\x02\x00e\x02j\x14\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00e\t\xab\x01\x00\x00\x00\x00\x00\x00Z\x0b\x02\x00e\x05d\x05\xab\x01\x00\x00\x00\x00\x00\x00\x01\x00\x02\x00e\x03j\x18\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00e\x0b\x02\x00e\r\xab\x00\x00\x00\x00\x00\x00\x00\xab\x02\x00\x00\x00\x00\x00\x00Z\x0e\x02\x00e\x0e\xab\x00\x00\x00\x00\x00\x00\x00\x01\x00y\x01)\x06\xe9\x00\x00\x00\x00Ns\xac\x08\x00\x00"
blob2 = b"c$|e+O>7&-6`m!Rzak~llE|2<;!(^*VQn#qEH||xE2b$*W=zw8NW~2mgIMj3sFjzy%<NJQ84^$vqeTG&mC+yhlE677j-8)F4nD>~?<GqL64olvBs$bZ4{qE;{|=p@M4Abeb^*>CzIprJ_rCXLX1@k)54$HHULnIe5P-l)Ahj!*6w{D~l%XMwDPu#jDYhX^DN{q5Q|5-Wq%1@lBx}}|vN1p~UI8h)0U&nS13Dg}x8K^E-(q$p0}4!ly-%m{0Hd>^+3*<O{*s0K-lk|}BLHWKJweQrNz5{%F-;@E_{d+ImTl7-o7&}O{%uba)w1RL*UARX*79t+0<^B?zmlODX9|2bzp_ztwjy_TdKb)1%eP4d-Xti0Ygjk_%w!^%1xuMNv4Z8&(*Ue7_^Fby1n3;+G<VDAfqi^h1>0@=Eki5!M~rms%afx`+uxa0*;FzudpqNln5M<@!OqndZ)R<vh4u&gpmmnaMewbT0RJby?(fa7XW#r>ZQ4UE&u|~lZsEY~-lpfWMf0_+pV-H`PXInpwmyo~mZ`tfUK?($KHa%mvNlovZ;Y)D+e6uw+mY6LNB2Y9&akbWpZ@lh=Si<!J@t|CG86E`)jp!l4xEY(h7@$llA4}B9dpL*j)eL{vVcbyMx5_{b13)N@wa~epS8Zfo&V_Y#fM*g9;@6%j=%i%WB0=QS3ewj@0~B!iibu<MqrrJIH{m&FoAGB3#0Nf;x!~dvQ|9#3c})IL6kEvhByJvA{B9%UqX0Tg*-+Ak~NW&RJbB?a6weENW&rzRi2ZB!647HWlA^rG4gvj3Yteo30&*};59;7nJF7eh7vjEXwwxPWWzD*3<IvZS#lIL(l*?u$;EGifKfLDpVb*rXLyw!AP~ZT^-S=4X{31tqe<O1kwG$gBZnu8eva3~6;4CxrcH1{Qg{M;GT5@Bdqt%s{xkT;DyaBk)v>cTr#=XM@cQ-VZZJ1azh{1Df~fwf(mdYk_cEC``#zrevUuf1-I7DHKqx9c7Me?*iNur9a3~o)A1AmHbK!6#k<d+QmXjoUlrAc=R-8EfEvn$TP%?Zb2%`-;wF2Z7c~Qh!QUp%@F7d(Q;It@nl31iwc^NCTTrj*OW)bEH>BYlQ$YmihSV2QDxrCsKNToEmsNif~;-ILG+l$@~sMDcnEHYIbjb?L-swo%>NNY60QJ5`2LX(&$CFf*W(cl7t80939@QH+>;!kK4jMTiOQA}zM@dS+wmk4?RtsqIs(NtuZr(Ewj<zxXaVots!6<}UP5>nNp1gfkes4T*zd{)6h-GF4>NSQO}R*91{c`k!=D-D}baN$1fuVNrUDvGiYVXWYBI456{mCG`ukuZfpN)A<xyb=s}byE(DvZfmpRkvo4CMg+F*3C%f6#?m{g@T4u-G<~mB~wGXg;NVMFDj&f5<)qG1#7xlYdFEQ_jHRu*e&FUmQ1J<Gp}4$xq@yalC(x)S-FIEgQe+IxARLJPRm@DXx&t+<h5L0ORJ<E<cw}6ln6?exLHy}9_dE4pz17oL(~E`{a`E-no7?`5)pDEpNY(-6VaJ?C^<J9(GN!A;n`PTPDZBE;WN>5k=ams`uyy<xmZYd@Og|04{1U(*1PGLR>h3WX?aZWQf~69?j-FsmL^GvInrgidoM2}r1u&}XB+q}oGg-NR#n^X*4uqBy?1qY$4<jzMBhXA);zPfx3*xU!VW$#fFa&MCOfRHVn0%6k8aaRw9dY?)7!uP!nGHEb#k+JxY|2h>kX{N{%!`IfvPX|S@e!nA3Iy~#cKVr)%cFx{mYSGj9h1H_Q6edkhuGk)3Z9gWp`~mJzG74m7(!J^o(!2de`mO?3IDzcV;$RQ`@foiYHlj%{3;+>#iT|K>v-`YH)PTx#fRu(|@AsKT#P^)cna!|9sUyU-MtAxP}M>w|Cc1s4_KI9hlp2y|UAEJ$C2$4Oh6~@uj-!Y-5tEyI$Y%KECN4u6l<*?fcwR_fD^|+djDIJ5u!>A&1N9itm{<3o-un;-)89^#pIPd{VwyzH_1WOyqZ$H)k$XXD-xcUafgjb=N#i!+Onn-Tj-cEob+(!(BOWa>FtC;21DH{%^IHo=c%;r;jstN15qS_U^F=Ab$c5Oh5W?fY!%^vdXfE>5Yf!rHF^<aF`B*be*L=(CF(%-E<?)%b0$BJ)|f2ZjG%ISw+Z8XcC`j+)bpk<79YXWEkdaV7mwG_kiObaNYym&C&ix(EpA7N#?}|aRxAsRm;!2e%e)a4AvZnHUPvwCa?b&OiHooz%"
blob3 = b"--- Calibrating Genetic Sequencer ---z\x1fDecoding catalyst DNA strand...z\x1eSynthesizing Catalyst Serum...)\x0f\xda\x06base64\xda\x04zlib\xda\x07marshal\xda\x05types\xda\x17encoded_catalyst_strand\xda\x05print\xda\tb85decode\xda\x13compressed_catalyst\xda\ndecompress\xda\x17marshalled_genetic_code\xda\x05loads\xda\x14catalyst_code_object\xda\x0cFunctionType\xda\x07globals\xda\x1bcatalyst_injection_function\xa9\x00\xf3\x00\x00\x00\x00\xfa\x13<genetic_sequencer>\xda\x08<module>r\x15\x00\x00\x00\x01\x00\x00\x00s\x8f\x00\x00\x00\xf0\x03\x01\x01\x01\xe3\x00\r\xdb\x00\x0b\xdb\x00\x0e\xdb\x00\x0c\xf0\x06\x00\x1bJ#\xd0\x00\x17\xe1\x00\x05\xd0\x06-\xd4\x00.\xd9\x00\x05\xd0\x06'\xd4\x00(\xd8\x16&\x90f\xd7\x16&\xd1\x16&\xd0'>\xd3\x16?\xd0\x00\x13\xd8\x1a)\x98$\x9f/\x99/\xd0*=\xd3\x1a>\xd0\x00\x17\xd8\x17$\x90w\x97}\x91}\xd0%<\xd3\x17=\xd0\x00\x14\xe1\x00\x05\xd0\x06&\xd4\x00'\xf0\x06\x00\x1f1\x98e\xd7\x1e0\xd1\x1e0\xd01E\xc1w\xc3y\xd3\x1eQ\xd0\x00\x1b\xf1\x06\x00\x01\x1c\xd5\x00\x1dr\x13\x00\x00\x00"


print("Starting genetic sequencing and payload decryption...")

# 1. Decode and Decompress the Core Payload (Blob 2)
decoded = base64.b85decode(blob2)
decompressed = zlib.decompress(decoded)
print("✅ Blob 2 successfully decoded (Base85) and decompressed (zlib).")

# 2. Extract the Python Code Object
# This is the correct step to get the executable code
try:
    code_object = marshal.loads(decompressed)
    print("✅ Python code object successfully loaded (marshal).")
    print(code_object)
    # 3. Execution (The core fix)
    # The code object might be a module-level code block or a function.
    # We'll execute it in a new, empty module environment.

    # Create a simple function from the code object for cleaner execution
    # If the code object is a function definition, this is needed.
    # If it's a module, exec() is better. We'll try a safe exec.
    
    # Define an environment for the code to run in
    module_globals = {
        '__builtins__': __builtins__,
        '__name__': '__chimera_payload__',
        '__file__': '<marshalled_code>',
        'sys': sys,
        'types': types,
        'base64': base64,
        'zlib': zlib,
        'marshal': marshal,
        'importlib': importlib.util,
        'struct': struct,
        'time': time
    }
    
    print("\n--- Executing Payload ---")
    exec(code_object, module_globals)
    print("--- Payload Execution Complete ---\n")

    # 4. Optional: Write the .pyc file (as you intended)
    pyc_filename = "chimera_payload_fixed.pyc"
    magic = importlib.util.MAGIC_NUMBER
    timestamp = struct.pack("I", int(time.time()))
    # Padding is for hash-based pyc (Python 3.3+), used as filler here
    padding = b'\x00\x00\x00\x00'  

    with open(pyc_filename, "wb") as f:
        f.write(magic)
        f.write(timestamp)
        f.write(padding)
        f.write(marshal.dumps(code_object))

    print(f"✅ Successfully wrote the extracted code object to {pyc_filename}")

except Exception as e:
    print(f"❌ An error occurred during payload processing/execution: {e}")


# --- Decrypting the Message ---
print("\n--- Checking Blobs for Decrypted Message ---")

# Check blob3 for visible text
blob3_str = blob3.decode('utf-8', errors='ignore')
print(f"**Content of blob3 (visible text):**\n{blob3_str}")