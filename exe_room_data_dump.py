import struct
from dataclasses import dataclass

'''
Dumb script to dump room information from the tlon executable. It will print out a
bunch of definitions that you can copy/paste into roomdata.py. That way other
scripts can just refer to that instead of extracting all over again.
'''

DGROUP_FILE_POS = 0x7D800

DGROUP = 0x0047F000
DGROUP_END = 0x004C3000

ROOM_DEFNS = 0x004AF6FC
ROOM_DEFNS_END = 0x004AFD3A

GOTO_ROOMS = 0x004B5229
GOTO_ROOMS_END = 0x004B574D

DATA_SWAPS = 0x004B6408
DATA_SWAPS_END = 0x004B6610

with open("GAME/Tlon-orig.exe", 'rb') as f:

    f.seek(DGROUP_FILE_POS)
    dgroup_data = f.read(DGROUP_END-DGROUP)
    assert len(dgroup_data) == DGROUP_END-DGROUP


@dataclass
class RoomDefn:
    eid : int
    f1: int
    f2: int
    f3: int
    off4: int
    off5: int
    off6: int
    f7: int


@dataclass
class Point:
    x: int
    y: int



def read_points(buf):
    # print('        ','---')
    result = []
    offset = 0
    while offset < len(buf):
        # print('        ',buf[offset:])
        if buf[offset:offset+2] == b'\x00\x00':
            break
        if buf[offset:offset+2] == b'\x01\x00':
            print('   !!!NON ZERO!!!')
            break
        # if buf[offset:offset+2] == b'\x03\x00':
        #     break
        x,y = struct.unpack_from("<HH", buf, offset)
        offset += 4
        p = Point(x,y)
        # print('        ',p)
        result.append(p)
    return result


def parsebuf3(buf):
    print("PARSING", buf)

    offset = 0
    num_entries, = struct.unpack_from('<B', buf, offset)
    offset += 1

    exits = []
    avoids = []

    for _ in range(num_entries):

        entry_size,entry_type,entry_extra = struct.unpack_from('<HHB', buf, offset)
        print(f"  (E) {entry_size}: {entry_type} - {entry_extra}")
        next_entry_offset = offset + entry_size

        if entry_type == 0:
            offset += 5

            points = read_points(buf[offset:next_entry_offset])
            avoids.append(points)
            print('   avoid:', points)

        else:
            offset += 2
            a,b,c,d,e,f,room,g = struct.unpack_from('<6HIB', buf, offset)
            offset += 17
            points = read_points(buf[offset:next_entry_offset])
            exits.append(points)
            print("    exit:")
            print("        ", a,b,'  ',c,d,'  ', e,f,'  ', room,'  ',g)
            print('        ', points)

        offset = next_entry_offset

    if next_entry_offset < len(buf):
        print("MORE DATA")

    return avoids, exits




roomdefns = []

spotsets = set()

offset = ROOM_DEFNS
while offset < ROOM_DEFNS_END:

    values = struct.unpack_from('<BBBBIIIB', dgroup_data, offset-DGROUP)
    offset += 17
    roomdefn = RoomDefn(*values)
    # print(hex(off1), hex(off2), hex(off3))
    spotsets.add(roomdefn.off4)
    spotsets.add(roomdefn.off5)
    spotsets.add(roomdefn.off6)

    roomdefns.append(roomdefn)


spot_data = {}

spotsets.add(GOTO_ROOMS)
spotsets_ordered = list(sorted(spotsets))  # noqa: C413
for i, off in enumerate(spotsets_ordered[:-1]):

    s = spotsets_ordered[i]
    e = spotsets_ordered[i+1]

    d = dgroup_data[s-DGROUP:e-DGROUP]
    # print(s, d)

    spot_data[s] = d


# for roomdefn in roomdefns:
#     # print(roomdefn)
#     # print(len(spot_data[roomdefn.off6]))
#     print(spot_data[roomdefn.off5][0])

buf1_by_room = {}
buf3_by_room = {}

avoids_by_room = {}
exits_by_room = {}




for roomdefn in roomdefns:
    print(roomdefn.eid)
    # print(roomdefn.eid, 'buf1', read_points(spot_data[roomdefn.off4]))
    # print(roomdefn.eid, 'buf3', read_points(spot_data[roomdefn.off6]))

    print("-2")
    avoids, exits = parsebuf3(spot_data[roomdefn.off5])
    avoids_by_room[roomdefn.eid] = avoids
    exits_by_room[roomdefn.eid] = exits
    print("-1")
    buf1_by_room[roomdefn.eid] = read_points(spot_data[roomdefn.off4])
    print("-3")
    buf3_by_room[roomdefn.eid] = read_points(spot_data[roomdefn.off6])


if True:
    print()
    print('buf1_by_room = ', repr(buf1_by_room))
    print()
    print('buf3_by_room = ', repr(buf3_by_room))
    print()
    print('avoids_by_room = ', repr(avoids_by_room))
    print()
    print('exits_by_room = ', repr(exits_by_room))

