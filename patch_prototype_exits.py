import struct

DGROUP_FILE_POS = 0x7D800

DGROUP = 0x0047F000
DGROUP_END = 0x004C3000



with open("GAME/tlon-orig.exe", 'rb') as f:
    data = f.read()

data = bytearray(data)


# room_offset = 0x004B2EB7 - DGROUP + DGROUP_FILE_POS
# room, = struct.unpack_from("<I", data, room_offset)
# room += 6*0x11
# struct.pack_into("<I", data, room_offset, room)


room_offset = 0x004B2EAB - DGROUP + DGROUP_FILE_POS
a,b,c,d,e,f,room = struct.unpack_from("<HHHHHHI", data, room_offset)
a,b=145,298
c,d=0x236,0x16C
e,f=0x174,0x169
room += 6*0x11
struct.pack_into("<HHHHHHI", data, room_offset, a,b,c,d,e,f,room)


poly_offset = 0x004B2EBC - DGROUP + DGROUP_FILE_POS
struct.pack_into("<8H", data, poly_offset, 75,225,   75,345,   169,311,    174,225)


with open("GAME/tlon-justexits.exe", 'wb') as f:
    f.write(data)
