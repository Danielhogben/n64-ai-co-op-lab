#!/usr/bin/env python3
import struct, sys, pathlib, json

def parse_header(path: pathlib.Path):
    with path.open('rb') as f:
        data = f.read(0x40)
    title = data[0x20:0x34].decode('ascii', errors='ignore').strip()
    cart_id = data[0x2C:0x2E].decode('ascii')
    country = data[0x2E:0x30].decode('ascii')
    version = data[0x30]
    cic = struct.unpack('>I', data[0x34:0x38])[0]
    crc1, crc2 = struct.unpack('>II', data[0x0C:0x14])
    return {
        "file": str(path),
        "title": title,
        "cart_id": cart_id,
        "country": country,
        "version": version,
        "cic_chip": cic,
        "crc1": f"0x{crc1:08X}",
        "crc2": f"0x{crc2:08X}"
    }

if __name__ == "__main__":
    for rom_path in sys.argv[1:]:
        info = parse_header(pathlib.Path(rom_path))
        print(json.dumps(info, indent=2))
