"""Independent scanline holes/boundaries and pinned output integrity."""
import hashlib
import importlib.util
import json
from pathlib import Path
import struct
import unittest

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location('bake_urban', ROOT / 'scripts/bake_urban.py')
bake = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(bake)

class UrbanBakeTests(unittest.TestCase):
    def test_hole_remains_empty(self):
        scale = bake.SCALE
        def ring(a, b):
            return [(x / scale - 180, y / scale - 90) for x, y in [(a,a),(b,a),(b,b),(a,b),(a,a)]]
        cells = {(r,c) for r,a,b in bake.scan([ring(0,6),ring(2,4)]) for c in range(a,b)}
        self.assertEqual(len(cells), 32)
        self.assertFalse(any((r,c) in cells for r in [2,3] for c in [2,3]))

    def test_pinned_payload_and_row_intervals(self):
        path = ROOT / 'crates/flightsim-world/data/natural-earth-urban.fsua'
        data = path.read_bytes()
        meta = json.loads(path.with_suffix('.provenance.json').read_text())
        self.assertEqual(hashlib.sha256(data).hexdigest(), meta['output_sha256'])
        magic,version,scale,count,_ = struct.unpack_from('<4sHHIQ',data)
        self.assertEqual((magic,version,scale),(b'FSUA',1,120))
        self.assertEqual(len(data),20+count*6)
        spans=list(struct.iter_unpack('<HHH',data[20:]))
        self.assertEqual(sum(b-a for _,a,b in spans),meta['occupied_cells'])
        self.assertTrue(all(0<=r<21600 and 0<=a<b<=43200 for r,a,b in spans))
        self.assertTrue(all(a[0]<b[0] or (a[0]==b[0] and a[2]<b[1]) for a,b in zip(spans,spans[1:])))
