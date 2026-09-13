
import datetime
import os
import os.path
import struct
import subprocess
import sys

from blake3 import blake3

import dumbpe

NASM_PATH='c:/apps/nasm/nasm-2.16.03/nasm.exe'


CODE_FILE_POS = 0x400
CODE = 0x00401000
CODE_END = 0x0047D400

DGROUP_FILE_POS = 0x7D800
DGROUP = 0x0047F000
DGROUP_END = 0x004C3000

EXE_PATH="GAME/Tlon-orig.exe"

# DON'T CALL IT PATCHED. WINDOWS WANTS TO RUN IT AS ADMIN
# OUT_PATH="GAME/Tlon2.exe"
OUT_PATCHED_PATH="GAME/Tlon-fixed.exe"
OUT_NOCD_OLD_PATH="GAME/Tlon-fixed-nocd-old.exe"
OUT_NOCD_NEW_PATH="GAME/Tlon-fixed-nocd.exe"

# NOCD_PATCH=True


def hashit(fpath):
    hasher = blake3()
    with open(fpath, 'rb') as f:
        d = f.read()
    hasher.update(d)
    return hasher.hexdigest()

def fill(buffer:bytearray, offset:int, fillen:int, b:bytes):
    assert len(b) == 1
    while fillen > 0:
        buffer[offset] = b[0]
        offset += 1
        fillen -= 1

def setbuf(buffer:bytearray, offset:int, b_ins:bytes):
    buffer[offset:offset+len(b_ins)] = b_ins


def nasm(asmfile):
    basename, _ = os.path.splitext(asmfile)
    binpath = basename + ".bin"
    subprocess.run([NASM_PATH, asmfile, '-o', binpath], check=True)
    with open(binpath, 'rb') as f:
        asmbin = f.read()
    return asmbin

def code_lfa(offset):
    code_fo = offset - CODE
    assert code_fo >= 0
    return CODE_FILE_POS + code_fo

def dgroup_lfa(offset):
    dgroup_fo = offset - DGROUP
    assert dgroup_fo >= 0
    return DGROUP_FILE_POS + dgroup_fo



def set_code(pefile, coffset, cbuf, relocs=None):
    if relocs is None:
        relocs = []

    exedata = pefile.exedata

    # clear with nops, remove relocs
    fill(exedata, code_lfa(coffset), len(cbuf), b'\x90')
    pefile.clear_relocs(coffset, coffset+len(cbuf))

    setbuf(exedata, code_lfa(coffset), cbuf)

    for r in relocs:
        pefile.add_reloc(coffset + r)


    
def patchit(OUT_PATH, FIX_TYPE):

    print()
    print(f"Patching {EXE_PATH}...")

    # we use current date in a couple of places
    now = datetime.datetime.now()

    # sanity check that we're patching the write file.
    assert hashit(EXE_PATH) == "fdba14f9bdaec3aedb3f16d0fd5b95a53cf8b1b21c4c40d18ca1024af8e080c2"

    with open(EXE_PATH, 'rb') as f:
        pefile = dumbpe.PeFile.fromfile(f)
        
    exedata = pefile.exedata

    # load assembled code
    patch0bin = nasm('patch0.asm')


    # nocd
    if FIX_TYPE == "nocd-old":
        assert code_lfa(0x0046FDAC+2) == 0x6f1ae
        setbuf(exedata, code_lfa(0x0046FDAC), b'\x83\xF8\x03')  # "cmp eax, 3" - Changed to 3 for fixed drive instead of CD
        assert code_lfa(0x0046FE0D) == 0x6f20d
        setbuf(exedata, code_lfa(0x0046FE0D), b'\x90\x90')   # "nop;nop" so we don't check space.

        # used by cd check
        assert dgroup_lfa(0x00482751) == 0x80F51
        fill(exedata, dgroup_lfa(0x00482751), 0x13, b'\x00')
        setbuf(exedata, dgroup_lfa(0x00482751), b'.\\data\\data00.grp')

        # used by cd find 
        assert dgroup_lfa(0x0048276B) == 0x80F6B
        fill(exedata,  dgroup_lfa(0x0048276B), 0x13, b'\x00')
        setbuf(exedata,  dgroup_lfa(0x0048276B), b'.\\data\\data00.grp')


    if FIX_TYPE == "nocd":
        # replace cd_check with "return 1;"
        cdcheck_code_offset = 0x46FCF0
        cbuf = b'\x31\xC0' + b'\x40' + b'\xC3' # xor eax,eax; inc eax; retn
        set_code(pefile, cdcheck_code_offset, cbuf)

        # replace cd_find with "a_path_game_cd_4C5FE0='.\'; return nonzero"
        cdfind_code_offset = 0x0046FD60
        cbuf = patch0bin[0x6FD60:0x6FD60+0xB]
        set_code(pefile, cdfind_code_offset, cbuf, [6,])









    # ----------------------------------------------------------------------------------
    # new exit for room 47

    # Need to add extra exit.
    # and the relocations for the data
    # and replace the bit in the array of stuff to replace.

    # that "5".  I don't knwo what it means.. it could be 2,3,4,5 ?  direction?

    room_47_exit = b'\x03' + \
        b'\x25\x00' + b'\xd3\x01\xea\x01\x44\x00\x42\x01\x60\x00\x42\x01\xd7\xf9\x4a\x00' + b'\x05' + b'\x1a\x01\x74\x01\x19\x01\xa3\x01\x3b\x02\xa4\x01\x36\x02\x74\x01\x00\x00' + \
        b'\x25\x00' + b'\x91\x00\x2a\x01\x36\x02\x6c\x01\x74\x01\x69\x01\x3d\xfa\x4a\x00' + b'\x05' + b'\x4b\x00\xe1\x00\x4b\x00\x59\x01\xa9\x00\x37\x01\xae\x00\xe1\x00\x00\x00' + \
        b'\x17\x00' + b'\x00\x00\x00' + b'\x3e\x00\xf0\x00\x3c\x00\x4f\x01\x4d\x01\x4a\x01\x4c\x01\xf0\x00\x00\x00'



    room_data_offset = 0x004C2050
    setbuf(exedata, dgroup_lfa(room_data_offset), room_47_exit)
    pefile.add_reloc(room_data_offset + room_47_exit.index(b'\xd7\xf9\x4a\x00'))
    pefile.add_reloc(room_data_offset + room_47_exit.index(b'\x3d\xfa\x4a\x00'))


    ptr_to_new_buf = 0x004B64D0
    setbuf(exedata, dgroup_lfa(ptr_to_new_buf), struct.pack("<I", room_data_offset))
    pefile.add_reloc(ptr_to_new_buf)


    # ----------------------------------------------------------------------------------

    # try to fix the fight loop
    jmp_reset_b = patch0bin[0x2Eb14:0x2Eb14+9]

    # jump to the new code
    pefile.clear_relocs(0x0042EB14, 0x0042EB14+9)
    setbuf(exedata, code_lfa(0x0042EB14), jmp_reset_b)

    # the new code, shoved at the end of the code segment
    new_checks_b = patch0bin[0x7D340: 0x7D340+0x20]
    setbuf(exedata, code_lfa(0x0047D340), new_checks_b)
    pefile.add_reloc(0x0047D340 + 2)



    # ----------------------------------------------------------------------------------

    # allow skipping LOGO
    call_play_video_b = patch0bin[0x4FCFC:0x4FCFC+5]
    setbuf(exedata, code_lfa(0x0044FCFC), call_play_video_b)


    # ----------------------------------------------------------------------------------

    # update version display

    # x is usually screenwidth-0x23 but we need more room.
    # change to middle of screen by dividing by 2
    setbuf(exedata, code_lfa(0x406203), b"\xD1\xE8\x90")

    # update pointer to version.
    setbuf(exedata, code_lfa(0x00406207 + 1), b'\xC0\x20\x4C\x00')
    # reloc already here

    # add str
    vnow_s = now.strftime("%Y%m%d")

    vstr = f'Fixed ({vnow_s}) v1.02'
    if FIX_TYPE == "nocd":
        vstr = f'Fixed NoCD ({vnow_s}) v1.02'
    elif FIX_TYPE == "nocd-old":
        vstr = f'Fixed NoCD Old ({vnow_s}) v1.02'
    vstr = vstr.rjust(82)
    vstr_b = vstr.encode('ascii') + b'\x00'

    version_str_offset = 0x004C20C0
    setbuf(exedata, dgroup_lfa(version_str_offset), vstr_b)



    # ----------------------------------------------------------------------------------

    # change release date
    now_s = now.strftime("%a %b %d %Y")
    now_b = now_s.encode('ascii') # no \x00 because we're patching middle of string
    assert len(now_b) <= 0xF
    fill(exedata, 0x7D9F4, 0xF, b' ')
    setbuf(exedata, 0x7D9F4, now_b)


    with open(OUT_PATH, 'wb')  as f:
        pefile.tofile(f)
        # f.write(exedata)
    
    print(f"Wrote {OUT_PATH}")





if __name__ == "__main__":
    patchit(OUT_PATCHED_PATH, None)
    patchit(OUT_NOCD_OLD_PATH, 'nocd-old')
    patchit(OUT_NOCD_NEW_PATH, 'nocd')
