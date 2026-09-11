'''
First workings of a patch. Just implemented the original nocd patch.
'''


# nocd
set(buffer, 0x6f1ae,  b'\x03')
set(buffer, 0x6f20d,  b'\x90\x90')

fill(buffer, 0x80F51, 0x13, b'\x00')
setbuf(buffer, 0x80F51, b'.\\data\\data00.grp')

fill(buffer, 0x80F6B, 0x13, b'\x00')
setbuf(buffer, 0x80F6B, b'.\\data\\data00.grp')


# change release date
now = datetime.datetime.now()
now_s = now.strftime("%a %b %d %Y")
now_b = now_s.encode('ascii')
assert len(now_b) <= 0xF
fill(buffer, 0x7D9F4, 0xF, b' ')
setbuf(buffer, 0x7D9F4, now_b)



def fill(buffer, offset, len, b):
    while len > 0:
        buffer[offset] = b
        offset += 1
        len -= 1

def setbuf(buffer, offset, b_ins):
    buffer[offset:offset+len(b_ins)] = b_ins




