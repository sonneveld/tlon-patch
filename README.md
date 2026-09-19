# Tlön: A Misty Story Patch

Patch to Tlon's game data to allow finishing without savegame hacks.

Visit [https://sonneveld.dev/tlon/](https://sonneveld.dev/tlon/) for more details.

## Scripts

- `dumbpatch.py` - patches Tlon.exe

- `grp_extract.py` - extract resource data from grp files
- `text_dat_dump.py` - dump english text from data files
- `exe_room_data_dump.py` - dump room hotspots from tlon.exe
- `roomdata.py` - extracted room information from exe
- `gfx_backgrounds_extract.py` - extract backgrounds with optional hotspots to png
- `dumbpe.py` - pe exe file parser for relocation data
- `dump_bindiff.py` - random helper script
- `dump_byte_array_repr.py` - random helper script
- `filemeta_dump.py` - dump file dates and hashes
- `patch_prototype_exits.py` - early prototype exits patch
- `patch_prototype_nocd.py` - early prototype nocd patch

## Assumptions

Scripts assumes original game data in `./GAME/` directory. A lot of other tools will
read or write resources to `./out/`
