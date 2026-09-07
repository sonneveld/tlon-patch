
import os
import os.path
import struct
from glob import glob

# from PIL import Image
import PIL
import PIL.Image
import PIL.ImageDraw

from roomdata import avoids_by_room, buf1_by_room, buf3_by_room, exits_by_room

# draw hotspots extracted from room data
DRAW_POLYS = True

def what_is_the_size_of_an_open_file(f):
    orig_position = f.tell()
    f.seek(0, os.SEEK_END)
    result = f.tell()
    f.seek(orig_position, os.SEEK_SET)
    return result

def do_a_gfx_header(f):
    fsize = what_is_the_size_of_an_open_file(f)
    header = f.read(10)
    # print(header)
    assert header == b'GFX v1.0->'

    while True:
        entry = f.read(9)
        i, offset, h, l = struct.unpack("<BIHH", entry)
        esize = h*10000 + l
        if offset+esize > fsize:
            break
        yield i, offset, esize


def main():
        
    with PIL.Image.open("panel.png") as panelim:  # noqa: SIM117
        with open("out/BACKS.gfx", 'rb') as f:

            entries = list(do_a_gfx_header(f))
            print(entries)

            for eid, offset, esize in entries:
                f.seek(offset)
                data = f.read(esize)

                # destination
                im = PIL.Image.new('RGB', (640,480))

                # read in the background data as BGR16 format
                bg_im = PIL.Image.frombuffer('RGB', (460, 370), data, 'raw', 'BGR;16', 0, 1)

                im.paste(panelim) # paste the border
                im.paste(bg_im, (89, 39))

                if DRAW_POLYS:
                    draw = PIL.ImageDraw.Draw(im) 
                    
                    pts = buf1_by_room.get(eid, [])
                    for i in range(len(pts)-1):
                        pt1 = pts[i]
                        pt2 = pts[i+1]
                        draw.line( (pt1.x, pt1.y, pt2.x, pt2.y), fill=0xFFFFFF)

                    pts = buf3_by_room.get(eid, [])
                    for i in range(len(pts)-1):
                        pt1 = pts[i]
                        pt2 = pts[i+1]
                        draw.line( (pt1.x, pt1.y, pt2.x, pt2.y), fill=0x00FFFF)

                    for pts in exits_by_room.get(eid, []):
                        for i in range(len(pts)-1):
                            pt1 = pts[i]
                            pt2 = pts[i+1]
                            draw.line( (pt1.x, pt1.y, pt2.x, pt2.y), fill=0xFF00FF)

                    for pts in avoids_by_room.get(eid, []):
                        for i in range(len(pts)-1):
                            pt1 = pts[i]
                            pt2 = pts[i+1]
                            draw.line( (pt1.x, pt1.y, pt2.x, pt2.y), fill=0x0000FF)

                im.save(f"out/images/backs/{eid}.png")

if __name__ == "__main__":
    main()
