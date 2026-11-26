import importlib.util
import struct
import unittest
from pathlib import Path

import numpy as np

spec = importlib.util.spec_from_file_location("pp_function", Path(__file__).with_name("main.py"))
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class PCDTests(unittest.TestCase):
    def pcd(self, rgb_type="U"):
        header = f"FIELDS x y z rgb\nSIZE 4 4 4 4\nTYPE F F F {rgb_type}\nCOUNT 1 1 1 1\nPOINTS 2\nDATA binary\n".encode()
        return header + struct.pack("<fffIfffI", 1, -2, 3, 0x282828, 4, 5, 6, 0xFFFFFF)

    def test_binary_coordinates_and_inverse_intensity(self):
        points = module.parse_pcd(self.pcd())
        np.testing.assert_array_equal(points[:, :3], [[1, -2, 3], [4, 5, 6]])
        np.testing.assert_allclose(points[:, 3], [0, 50], atol=1e-5)

    def test_float_rgb_bit_layout(self):
        np.testing.assert_array_equal(module.parse_pcd(self.pcd("F")), module.parse_pcd(self.pcd()))

    def test_truncated_payload_rejected(self):
        with self.assertRaisesRegex(ValueError, "payload length"):
            module.parse_pcd(self.pcd()[:-1])


if __name__ == "__main__":
    unittest.main()
