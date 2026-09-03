import struct
from pathlib import Path

GAME_PATH=Path("./GAME")
OUT_PATH=Path("./out")

group_by_idx = {
    1: GAME_PATH / 'Data/Data00.grp',
    2: GAME_PATH / 'Data/Data01.grp',
    3: GAME_PATH / 'Sfx/Sfx00.grp',
    4: GAME_PATH / 'Music/Music00.grp',
}

def decrypt_wave(data):
    '''
    Wave files are obfuscated by being XOR'd 0x55
    '''
    result = bytearray(len(data))
    for i in range(len(data)):
        result[i] = data[i] ^ 0x55
    return result

def main():
        
    with open(GAME_PATH / "grp.fat", 'rb') as f:

        idx = 0
        while True:
            data = f.read(0x1b)
            if len(data) != 0x1b:
                break

            fname, size, group_idx, pos, _,_ = struct.unpack('<13sIBIIB', data)

            fname = fname.rstrip(b'\0').decode("ascii")
            group = group_by_idx[group_idx]

            print(idx, ':', fname, size, group, pos)

            with open(group, 'rb') as gf:
                gf.seek(pos)
                fdata = gf.read(size)
                assert len(fdata) == size
            if fname.endswith(".WAV"):
                fdata = decrypt_wave(fdata)
            with open(OUT_PATH / f'{fname}', 'wb') as gf:
                gf.write(fdata)

            idx += 1


if __name__ == "__main__":
    main()
