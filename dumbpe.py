
import struct
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Self


@dataclass
class PeHeader:
    mMagic : int
    mMachine : int
    mNumberOfSections : int
    mTimeDateStamp : int
    mPointerToSymbolTable : int
    mNumberOfSymbols : int
    mSizeOfOptionalHeader : int
    mCharacteristics : int

    @classmethod
    def from_buffer(cls, buffer, offset) -> Self:
        values = struct.unpack_from("<IHHIIIHH", buffer, offset)
        result = cls(*values)
        assert result.mMagic == 0x4550   # PE
        return result

    @classmethod
    def size(cls) -> int:
        return struct.calcsize("<IHHIIIHH")



PE32OPTDIR_STRUCT = struct.Struct("<II")

@dataclass
class Pe32ImageDataDirectory:
    VirtualAddress : int
    Size : int

    @classmethod
    def from_buffer(cls, buffer, offset) -> Self:
        values = PE32OPTDIR_STRUCT.unpack_from(buffer, offset)
        return cls(*values)

    @classmethod
    def size(cls) -> int:
        return PE32OPTDIR_STRUCT.size


PE32OPTHEAD_STRUCT = struct.Struct("<HBBIIIIIIIIIHHHHHHIIIIHHIIIIII")

@dataclass
class Pe32OptionalHeader:
    mMagic : int
    mMajorLinkerVersion : int
    mMinorLinkerVersion : int
    mSizeOfCode : int
    mSizeOfInitializedData : int
    mSizeOfUninitializedData : int
    mAddressOfEntryPoint : int
    mBaseOfCode : int
    mBaseOfData : int
    mImageBase : int
    mSectionAlignment : int
    mFileAlignment : int
    mMajorOperatingSystemVersion : int
    mMinorOperatingSystemVersion : int
    mMajorImageVersion : int
    mMinorImageVersion : int
    mMajorSubsystemVersion : int
    mMinorSubsystemVersion : int
    mWin32VersionValue : int
    mSizeOfImage : int
    mSizeOfHeaders : int
    mCheckSum : int
    mSubsystem : int
    mDllCharacteristics : int
    mSizeOfStackReserve : int
    mSizeOfStackCommit : int
    mSizeOfHeapReserve : int
    mSizeOfHeapCommit : int
    mLoaderFlags : int
    mNumberOfRvaAndSizes : int
    dirValues : list = field(default_factory=list)

    @classmethod
    def from_buffer(cls, buffer, offset) -> Self:
        values = PE32OPTHEAD_STRUCT.unpack_from(buffer, offset)
        result = cls(*values)
        assert result.mMagic == 0x010b    # PE32
        assert result.mImageBase == 0x400000
        offset += PE32OPTHEAD_STRUCT.size
        for _ in range(16):
            dirvalue = Pe32ImageDataDirectory.from_buffer(buffer, offset)
            offset += Pe32ImageDataDirectory.size()
            result.dirValues.append(dirvalue)
        return result



SECTHEAD_STRUCT = struct.Struct("<8sIIIIIIHHI")

@dataclass
class SectionHeader:
    mName : str
    mVirtualSize : int
    mVirtualAddress : int
    mSizeOfRawData : int
    mPointerToRawData : int
    mPointerToRelocations : int
    mPointerToLinenumbers : int
    mNumberOfRelocations : int
    mNumberOfLinenumbers : int
    mCharacteristics : int

    @classmethod
    def from_buffer(cls, buffer, offset) -> Self:
        values = SECTHEAD_STRUCT.unpack_from(buffer, offset)
        return cls(*values)

    @classmethod
    def size(cls) -> int:
        return SECTHEAD_STRUCT.size


def parse_relocations(buffer, offset):

    while True:
        # print("-")
        VirtualAddress, SizeOfBlock = struct.unpack_from("<II", buffer, offset)
        # print(hex(VirtualAddress), hex(SizeOfBlock))
        nextblock_offset = offset+SizeOfBlock
        offset += 8

        if VirtualAddress == 0:
            break

        SizeOfBlock -= 8
        while SizeOfBlock:
            entry_b, = struct.unpack_from("<H", buffer, offset)
            offset += 2
            SizeOfBlock -= 2
            entry_type = (entry_b >> 12) & 0xF
            entry_offset = entry_b & 0xFFF
            # if entry_type == 0:
                # print(entry_offset)
            if entry_type != 0:
                assert entry_type == 3
                yield VirtualAddress + entry_offset
                # print('et', entry_type)
            # print(' ', hex(entry_offset), '->', hex(VirtualAddress + entry_offset), entry_type)

        assert offset == nextblock_offset
        offset = nextblock_offset
        


def encode_relocations(relocations):

    result = bytearray()

    pages = defaultdict(list)

    for address in relocations:
        page_idx, page_offset = divmod(address, 0x1000)
        page_address = page_idx*0x1000
        pages[page_address].append(page_offset)


    for page_address in sorted(pages.keys()):

        assert len(result) % 4 == 0

        offsets = pages[page_address]
        block_sz = 4 + 4 + 2*len(offsets)
        padding_sz = 0
        _,remaining = divmod(block_sz, 4)
        if remaining != 0:
            padding_sz += 4-remaining

        result.extend( struct.pack("<II",page_address, block_sz+padding_sz) )
        for offset in offsets:
            value = (3 << 12) | offset
            result.extend( struct.pack("<H", value))
        result.extend(b'\x00'*padding_sz)

    # result.extend(b'\x00' * (wanted_size-len(result)))
    # assert len(result) == wanted_size

    return result 

IMAGE_DIRECTORY_ENTRY_BASERELOC = 5

@dataclass
class PeFile:

    exedata: bytearray
    pe_header: PeHeader
    pe32_opt_header_offset: int
    pe32_opt_header: Pe32OptionalHeader
    sections: list[SectionHeader]
    reloc_s: SectionHeader
    relocations: list[int]


    @classmethod
    def fromfile(cls, f) -> Self:
        f.seek(0)
        data = f.read()
        exedata = bytearray(data)

        # DOS stub
        mz_magic,  = struct.unpack_from('<H', exedata, 0)
        assert mz_magic == 0x5A4D # MZ
        e_lfanew,  = struct.unpack_from('<I', exedata, 0x3C)
        # print(hex(e_lfanew))

        offset = e_lfanew

        pe_header = PeHeader.from_buffer(exedata, offset)
        # print(pe_header)
        offset += PeHeader.size()

        pe32_opt_header_offset = offset
        pe32_opt_header = Pe32OptionalHeader.from_buffer(exedata, offset)
        # print(pe32_opt_header)
        offset += pe_header.mSizeOfOptionalHeader

        reloc_s = None
        sections = []
        for i in range(pe_header.mNumberOfSections):
            s = SectionHeader.from_buffer(exedata, offset)
            offset += SectionHeader.size()
            if s.mName == b'.reloc\x00\x00':
                reloc_s = s
            sections.append(s)
        assert reloc_s is not None

        relocations = list(parse_relocations(exedata, reloc_s.mPointerToRawData))

        return cls(exedata, pe_header, pe32_opt_header_offset, pe32_opt_header, sections, reloc_s, relocations)

    def tofile(self, f):
        self.update_reloc()
        f.write(self.exedata)


    def update_reloc(self):
        new_relocations_b = encode_relocations(self.relocations)
        assert len(new_relocations_b) <= self.reloc_s.mSizeOfRawData

        # clear it first
        self.exedata[self.reloc_s.mPointerToRawData:self.reloc_s.mPointerToRawData+self.reloc_s.mSizeOfRawData] = b'\x00'*self.reloc_s.mSizeOfRawData

        self.exedata[self.reloc_s.mPointerToRawData:self.reloc_s.mPointerToRawData+len(new_relocations_b)] = new_relocations_b

        reloc_dir_size_offset = self.pe32_opt_header_offset + PE32OPTHEAD_STRUCT.size + PE32OPTDIR_STRUCT.size*IMAGE_DIRECTORY_ENTRY_BASERELOC

        struct.pack_into("<I", self.exedata, reloc_dir_size_offset+4, len(new_relocations_b))


    def clear_relocs(self, start_offset, end_offset):

        assert start_offset >= self.pe32_opt_header.mImageBase
        assert end_offset >= self.pe32_opt_header.mImageBase
        start_offset -= self.pe32_opt_header.mImageBase
        end_offset -= self.pe32_opt_header.mImageBase

        to_remove = range(start_offset, end_offset)
        l = len(self.relocations)
        self.relocations = [x for x in self.relocations if x not in to_remove]
        l2 = len(self.relocations)

        print(f'removed {l-l2} relocations')


    def add_reloc(self, offset):
        assert offset >= self.pe32_opt_header.mImageBase
        offset -= self.pe32_opt_header.mImageBase

        l = len(self.relocations)

        if offset not in self.relocations:
            self.relocations.append(offset)
        else:
            print(f"offset {offset} already in .reloc")
        l2 = len(self.relocations)

        print(f'added {l2-l} relocations')








if __name__ == "__main__":

    with open("GAME/Tlon-orig.exe", 'rb') as f:
        pefile = PeFile.fromfile(f)

    with open("testout.exe", "wb") as f:
        pefile.tofile(f)

    # mz_magic,  = struct.unpack_from('<H', exedata, 0)
    # assert mz_magic == 0x5A4D # MZ

    # e_lfanew,  = struct.unpack_from('<I', exedata, 0x3C)
    # print(hex(e_lfanew))


    # offset = e_lfanew

    # # pe_magic, = struct.unpack_from("<I", exedata, e_lfanew)
    # # assert pe_magic == 0x4550   # PE

    # pe_header = PeHeader.from_buffer(exedata, offset)
    # # pe_header = struct.unpack_from("<IHHIIIHH", exedata, e_lfanew)
    # print(pe_header)


    # offset += PeHeader.size()

    # pe32_opt_header = Pe32OptionalHeader.from_buffer(exedata, offset)
    # print(pe32_opt_header)

    # offset += pe_header.mSizeOfOptionalHeader

    # # print(exedata[offset:offset+10])
    # print()


    # reloc_s : SectionHeader|None = None

    # for i in range(pe_header.mNumberOfSections):

    #     s = SectionHeader.from_buffer(exedata, offset)
    #     offset += SectionHeader.size()

    #     print(s)
    #     if s.mName == b'.reloc\x00\x00':
    #         reloc_s = s

    # assert reloc_s is not None
    # print()
    # print(reloc_s)


    # relocations = list(parse_relocations(exedata, reloc_s.mPointerToRawData))

    # orig_relocation_bin = exedata[reloc_s.mPointerToRawData:reloc_s.mPointerToRawData+reloc_s.mSizeOfRawData]

    # # print(relocations[:100])
    # # print(len(set(relocations)))
    # # reloc_bin = exedata[reloc_s.mPointerToRawData: reloc_s.mPointerToRawData+reloc_s.mSizeOfRawData]
    # # print(reloc_bin[:100])

    # new_relocations_bin = encode_relocations(relocations, reloc_s.mSizeOfRawData)


    # print(len(orig_relocation_bin))
    # print(len(new_relocations_bin))

    # relocations2 = list(parse_relocations(new_relocations_bin, 0))


    # print(relocations == relocations2)


    # # print(orig_relocation_bin[:-100])

    # with open('reloc-orig.bin', 'wb') as f:
    #     f.write(orig_relocation_bin)
    # with open('reloc-new.bin', 'wb') as f:
    #     f.write(new_relocations_bin)



    # # for o in relocations:
    # #     if o not in relocations2:
    # #         print(hex(o))


    # # so we need to try to fit in within the reloc siz.e. but also update the reloc directry entry


