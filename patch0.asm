;first patch


org     0x400000

BITS 32
CPU 586





; max 9 bytes
section .jmpcheck start=0x0042EB14

jmp  coolcheck

nop
nop
nop
nop
nop
nop
nop
nop
nop
nop
nop
nop






section .logoskip start=0x0044FCFC

call    s_video_play_46E2A0



section .cdfind start=0x0046FD60

s_cd_find_drive_46FD60:
mov eax, 0x00005C2E    ; '.\'
mov dword [a_path_game_cd_4C5FE0], eax
ret





section .newcheck start=0x047D340

coolcheck:

mov  al, byte [b_room_id__4A581D]
cmp al, 32h
jz  short doneso
cmp al, 54h
jz  short doneso

loopagain:
jmp   l_loop_head_42EADA

doneso:
jmp  l_done_42EB1D







absolute 0x0042EADA 
l_loop_head_42EADA:

absolute 0x0042EB1D 
l_done_42EB1D:

absolute 0x0046E2A0
s_video_play_46E2A0:

absolute 0x004A581D
b_room_id__4A581D db ?




absolute 0x004C5FE0

a_path_game_cd_4C5FE0 dd ?
