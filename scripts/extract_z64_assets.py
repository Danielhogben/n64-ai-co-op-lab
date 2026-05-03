#!/usr/bin/env python3
"""
Extract Zelda N64 DMA chunks (textures, audio, raw).
"""
import pathlib, struct, sys, os

ROM = pathlib.Path(sys.argv[1])
OUT = pathlib.Path("assets") / ROM.stem
OUT.mkdir(parents=True, exist_ok=True)

BASE = 0x80000000
DMA_OFF = 0x88000

with ROM.open('rb') as f:
    f.seek(DMA_OFF)
    entry_cnt = struct.unpack('>I', f.read(4))[0]
    print(f"Found DMA table with {entry_cnt} entries (offset 0x{DMA_OFF:X})")

    for i in range(entry_cnt):
        raw = f.read(20)
        if len(raw) < 20:
            break
        v_start, v_end, p_start, p_end, seg_type = struct.unpack('>5I', raw)
        size = v_end - v_start
        f.seek(v_start - BASE)
        data = f.read(size)

        if seg_type == 0x0:
            sub = "raw"
            ext = "bin"
        elif seg_type == 0x1:
            sub = "textures"
            ext = "bin"
        elif seg_type == 0x2:
            sub = "audio"
            ext = "bin"
        else:
            sub = f"unknown_{seg_type:02X}"
            ext = "bin"

        out_dir = OUT / sub
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / f"{i:04d}.{ext}"
        out_path.write_bytes(data)
        print(f"[{i:03d}] {sub:<9} 0x{v_start:08X}–0x{v_end:08X} ({size:,} bytes) → {out_path}")

    print("All done. Assets are under:", OUT)
