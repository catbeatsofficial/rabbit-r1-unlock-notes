#!/usr/bin/env python3
"""Inspect a local backup only. No crypto authentication, repair or device IO."""
import argparse
import hashlib
import json
from pathlib import Path
import struct


def inspect(path):
    data = path.read_bytes()
    if len(data) < 60:
        raise ValueError('Too short for a V4 header')
    words = struct.unpack_from('<7I', data)
    if words[0] != 0x4d4d4d4d or words[1] != 4 or words[2] != 60 or words[6] != 0x45454545:
        raise ValueError('Unrecognized header; do not apply the documented V4 offsets')
    return {
        'size_bytes': len(data),
        'sha256': hashlib.sha256(data).hexdigest(),
        'header_version': words[1],
        'lock_state_raw': words[3],
        'dm_verity_state_raw': words[4],
        'runtime_raw': words[5],
        'named_verity_record_at_tested_offset': data[0x24c:0x24c + len(b'avb.managed_verity_mode')] == b'avb.managed_verity_mode',
        'tested_record_region_present': len(data) >= 0x2c0,
        'tested_record_region_nonzero': bool(any(data[0x240:0x2c0])),
        'matches_tested_partition_size': len(data) == 0x800000,
        'authenticated': False,
        'note': 'Raw fields only. No device IO or writes. A matching shape is not authentication or a repair recommendation.',
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('backup', type=Path)
    args = parser.parse_args()
    try:
        result = inspect(args.backup)
    except (OSError, ValueError) as error:
        parser.exit(1, f'{error}\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
