
import struct
from pathlib import Path

GAME_DATA_PATH=Path("./GAME/Data")

fnames = [
    'ANSW.DAT',
    'DLGS.DAT',
    'LOOKAT.DAT',
]

def main():

    '''
    Majority of text data files have a lookup table at the start. I don't think
    there's a way to determine how many though, so we use heuristics like checking
    the index makes sense.
    '''
        
    for fname in fnames:

        with open(GAME_DATA_PATH / fname, 'rb') as f:
            data = f.read()

        offsets = []
        read_offset = 0
        while True:
            # if we start reading into the text data, we're done.
            if offsets and read_offset >= min(offsets):
                break

            o, = struct.unpack_from("<I", data, read_offset)

            # GUESS: I _think_ offset is actually off by 1. Maybe 0 is special case.
            # I'm assuming this because the index table never refers to the first
            # obfuscated character.
            assert o >= 1
            o -= 1

            # stop if we get an invalid offset too.
            if o >= len(data):
                break
            # we assume offsets are in order
            if offsets and o <= offsets[-1]:
                break
            offsets.append(o)
            read_offset += 4

        # Don't want to trust the format so we use start/end ranges to extract str
        # however it looks like the format is always
        #   "\raaaaaaaa\rbbbbbbbbbbb\rccccccccc\n"

        offsets.append(len(data))

        for i in range(len(offsets)-1):

            s_b = data[offsets[i]:offsets[i+1]]
            s_b = bytearray(s_b)
            
            for chi,chb in enumerate(s_b):
                s_b[chi] = chb ^ 0x33

            s = s_b.decode('ascii')
            print(fname, hex(i), repr(s))


    '''
    TLONTXT.DAT doesn't have a lookup table, it's just 
    one long string separated by \\r characters.
    '''

    fname = 'TLONTXT.DAT'
    with open(f"GAME/Data/{fname}", 'rb') as f:
        data = f.read()

    # The last two bytes are 0x29 0x1A which are each other when XOR'd. Probably
    # used to represent the end?
    end_offset = data.index(b"\x29\x1a")
    data = bytearray(data[:end_offset])

    for chi,chb in enumerate(data):
        data[chi] = chb ^ 0x33
    data_ascii = data.decode('ascii')
    strs = data_ascii.split("\r")
    for i, s in enumerate(strs):
        print(fname, hex(i), repr(s))



if __name__ == "__main__":
    main()
