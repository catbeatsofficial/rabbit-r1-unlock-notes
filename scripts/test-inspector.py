"""Synthetic fixtures only; never reads a real device or partition dump."""
import importlib.util
from pathlib import Path
import struct
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('inspector', Path(__file__).with_name('inspect-seccfg.py'))
inspector = importlib.util.module_from_spec(spec)
spec.loader.exec_module(inspector)


class InspectorTests(unittest.TestCase):
    def test_named_record_and_input_unchanged(self):
        data = bytearray(0x800000)
        struct.pack_into('<7I', data, 0, 0x4d4d4d4d, 4, 60, 3, 1, 0, 0x45454545)
        name = b'avb.managed_verity_mode'
        data[0x24c:0x24c + len(name)] = name
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'synthetic.bin'
            path.write_bytes(data)
            result = inspector.inspect(path)
            self.assertTrue(result['named_verity_record_at_tested_offset'])
            self.assertEqual(result['dm_verity_state_raw'], 1)
            self.assertFalse(result['authenticated'])
            self.assertEqual(path.read_bytes(), data)

    def test_rejects_unrecognized_header(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'synthetic.bin'
            for data in (b'too short', bytes(128)):
                path.write_bytes(data)
                with self.assertRaises(ValueError):
                    inspector.inspect(path)


if __name__ == '__main__':
    unittest.main()
