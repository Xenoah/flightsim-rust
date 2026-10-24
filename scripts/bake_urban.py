#!/usr/bin/env python3
"""Bake Natural Earth polygon cell centres to bounded FSUA row spans (stdlib only).

Input: official v5.1.2 ne_10m_urban_areas.shp, public domain, no runtime GIS.
Even/odd scanline filling retains holes. Each cell is 1/120 degree; an occupied
centre does not imply the whole cell is dry land or contains real buildings.
"""
import argparse
import hashlib
import json
import math
import struct
from pathlib import Path

SCALE = 120
SOURCE = "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/v5.1.2/10m_cultural/ne_10m_urban_areas.shp"
SHA256 = "76b8c5786af5df4fa18ae615e594347fb464525347038b15f9df15d1396cb7de"


def polygons(data):
    if len(data) < 100 or struct.unpack_from('>i', data)[0] != 9994:
        raise ValueError('not a shapefile')
    if struct.unpack_from('>i', data, 24)[0] * 2 != len(data):
        raise ValueError('truncated shapefile')
    offset = 100
    while offset < len(data):
        size = struct.unpack_from('>i', data, offset + 4)[0] * 2
        record = data[offset + 8:offset + 8 + size]
        if len(record) != size or struct.unpack_from('<i', record)[0] != 5:
            raise ValueError('expected Polygon record')
        parts, count = struct.unpack_from('<ii', record, 36)
        starts = list(struct.unpack_from(f'<{parts}i', record, 44)) + [count]
        points = list(struct.iter_unpack('<dd', record[44 + 4 * parts:]))
        if len(points) != count:
            raise ValueError('bad point count')
        yield [points[a:b] for a, b in zip(starts, starts[1:])]
        offset += 8 + size


def scan(rings):
    lo = max(0, math.ceil((min(y for r in rings for _, y in r) + 90) * SCALE - .5))
    hi = min(180 * SCALE, math.ceil((max(y for r in rings for _, y in r) + 90) * SCALE - .5))
    for row in range(lo, hi):
        y = (row + .5) / SCALE - 90
        xs = sorted(a[0] + (y - a[1]) * (b[0] - a[0]) / (b[1] - a[1])
                    for ring in rings for a, b in zip(ring, ring[1:])
                    if (a[1] <= y < b[1]) or (b[1] <= y < a[1]))
        if len(xs) % 2:
            raise ValueError('unpaired scanline')
        for left, right in zip(xs[::2], xs[1::2]):
            a = max(0, math.ceil((left + 180) * SCALE - .5))
            b = min(360 * SCALE, math.ceil((right + 180) * SCALE - .5))
            if a < b:
                yield row, a, b


def bake(data):
    rows = {}
    count = 0
    for rings in polygons(data):
        count += 1
        for row, a, b in scan(rings):
            rows.setdefault(row, []).append((a, b))
    spans = []
    for row, intervals in sorted(rows.items()):
        merged = []
        for a, b in sorted(intervals):
            if merged and a <= merged[-1][1]:
                merged[-1] = (merged[-1][0], max(b, merged[-1][1]))
            else:
                merged.append((a, b))
        spans.extend((row, a, b) for a, b in merged)
    payload = b''.join(struct.pack('<HHH', *s) for s in spans)
    checksum = 0xcbf29ce484222325
    for byte in payload:
        checksum = ((checksum ^ byte) * 0x100000001b3) & 0xffffffffffffffff
    result = struct.pack('<4sHHIQ', b'FSUA', 1, SCALE, len(spans), checksum) + payload
    return result, count, sum(b-a for _, a, b in spans)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    data = args.input.read_bytes()
    if hashlib.sha256(data).hexdigest() != SHA256:
        raise ValueError('input must match pinned official Natural Earth shapefile')
    result, polygons_count, cells = bake(data)
    args.output.write_bytes(result)
    metadata = dict(source_url=SOURCE, source_sha256=SHA256, source_release='Natural Earth vector v5.1.2',
                    dataset='10m urban areas (MODIS 2002-2003 derived)', license='Public domain',
                    terms='https://www.naturalearthdata.com/about/terms-of-use/',
                    method='even-odd polygon cell-centre raster, merged half-open row spans; 1/120 degree',
                    source_polygons=polygons_count, occupied_cells=cells, bytes=len(result),
                    output_sha256=hashlib.sha256(result).hexdigest(),
                    limits='Coarse historical urban extent only; no real building footprints, heights or roads. Runtime land/water and airport masks remain mandatory.')
    args.output.with_suffix('.provenance.json').write_text(json.dumps(metadata, indent=2) + '\n')
    print(json.dumps(metadata, indent=2))

if __name__ == '__main__':
    main()
