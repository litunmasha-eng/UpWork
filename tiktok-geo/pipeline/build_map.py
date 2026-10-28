#!/usr/bin/env python3
"""Generates compositions/map.html: the whole map drawn on one canvas from timeline time."""
import json, math, re

PROJ = '/tmp/claude-0/work/nordsee'
A = PROJ + '/assets/'
geo = json.load(open(A + 'geo.json'))
det = json.load(open(A + 'basemaps.json'))['detail']
DUR = 75.5
CY = 800
OX, OY = 24576, 12288


def P(lon, lat):
    n = 2 ** 8 * 256
    x = (lon + 180) / 360 * n
    y = (1 - math.log(math.tan(math.radians(lat)) + 1 / math.cos(math.radians(lat))) / math.pi) / 2 * n
    return [round(x - OX, 1), round(y - OY, 1)]


CAM0 = (6.0, 53.0, 0.135, 0)
CAM = [
    (0.0, 2.9, 3.0, 56.4, 0.34, 30, 'power3.inOut'),
    (2.9, 6.3, 3.0, 56.2, 0.37, 32, 'sine.inOut'),
    (9.2, 1.0, 3.2, 56.0, 0.33, 24, 'power2.inOut'),
    (11.9, 1.1, 4.0, 55.0, 0.205, 18, 'power3.inOut'),
    (13.0, 1.6, 4.0, 55.0, 0.215, 18, 'sine.inOut'),
    (14.6, 0.3, 4.6, 55.2, 0.24, 8, 'power4.out'),
    (14.9, 4.3, 4.6, 55.2, 0.25, 10, 'sine.inOut'),
    (19.25, 1.3, 5.7, 52.75, 0.92, 38, 'power3.inOut'),
    (20.55, 5.4, 5.6, 52.85, 1.0, 40, 'sine.inOut'),
    (26.0, 1.3, 10.0, 55.25, 0.62, 30, 'power3.inOut'),
    (27.3, 5.6, 10.1, 55.2, 0.7, 32, 'sine.inOut'),
    (32.95, 1.35, -4.75, 49.25, 1.02, 40, 'power3.inOut'),
    (34.3, 5.4, -4.8, 49.2, 1.12, 42, 'sine.inOut'),
    (39.75, 1.3, -2.7, 58.9, 0.86, 36, 'power3.inOut'),
    (41.05, 1.4, -2.2, 59.2, 0.8, 34, 'sine.inOut'),
    (42.45, 1.6, 1.4, 59.7, 0.38, 30, 'power2.inOut'),
    (44.05, 3.6, 1.6, 59.75, 0.41, 32, 'sine.inOut'),
    (50.75, 1.0, 1.0, 55.1, 0.205, 16, 'power3.inOut'),
    (51.75, 8.0, 1.0, 55.0, 0.22, 18, 'sine.inOut'),
    (67.3, 5.4, 6.0, 53.2, 0.135, 4, 'power2.inOut'),
    (72.7, 2.8, 6.0, 53.2, 0.13, 0, 'sine.inOut'),
]


def cam_at(t):
    s = CAM0[2]
    for c in CAM:
        if c[0] <= t:
            s = c[4]
    return s


def sub_lengths(d):
    best = 0
    for sp in re.split(r'(?=M)', d):
        nums = [float(v) for v in re.findall(r'-?\d+\.?\d*', sp)]
        pts = list(zip(nums[::2], nums[1::2]))
        L = sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(pts, pts[1:]))
        best = max(best, L)
    return round(best, 1)


def poly_d(pts):
    return 'M' + ' L'.join(f'{x},{y}' for x, y in pts)


DAM1 = [(-4.78, 48.56), (-4.95, 49.0), (-5.08, 49.5), (-5.19, 49.95)]
DAM2 = [(-3.05, 58.64), (-2.95, 58.86), (-2.75, 59.08), (-2.2, 59.35), (-1.62, 59.53), (-1.3, 59.86),
        (-0.9, 60.12), (1.0, 60.3), (3.0, 60.45), (4.95, 60.55)]
OUTS = [
    [(-5.0, 49.3), (-6.4, 49.2), (-7.8, 49.0)],
    [(-1.8, 59.45), (-2.6, 60.2), (-3.4, 60.9)],
    [(2.0, 60.38), (1.6, 61.3), (1.2, 62.2)],
]
paths = {
    'ns': geo['northsea'],
    'coast': geo['coast'],
    'dam1': poly_d([P(*p) for p in DAM1]),
    'dam2': poly_d([P(*p) for p in DAM2]),
}
for c, d in geo['countries'].items():
    paths['c' + c] = d
for r, d in geo['rivers'].items():
    paths['r' + r] = d
for i, o in enumerate(OUTS):
    paths[f'out{i}'] = poly_d([P(*p) for p in o])
lens = {k: sub_lengths(v) for k, v in paths.items() if not k.startswith('c') and k != 'coast'}

FLAGS = {'GBR': (-1.6, 52.7), 'FRA': (2.3, 47.9), 'NOR': (8.6, 60.9), 'DNK': (9.1, 56.0),
         'DEU': (10.0, 51.6), 'NLD': (5.7, 52.4), 'BEL': (4.6, 50.65)}
flags = {c: P(*ll) for c, ll in FLAGS.items()}
flag_w = round(66 / cam_at(12.4), 1)

# labels: id -> [text, x, y, rot, fontsize(world), color, spacing, counter]
LAB = [
    ('nordsee', 'NORDSEE', 2.9, 56.9, 50, 3.3, -6, '#fff', 0.3, 0),
    ('see', 'GRÖSSTER SEE DER ERDE', 2.9, 56.2, 34, 6.6, -6, '#DFFFF6', 0.14, 0),
    ('area', '', 3.0, 55.6, 60, 9.4, -6, '#fff', 0.04, 1),
    ('fr', 'FRANKREICH', -3.6, 48.25, 32, 35.0, -4, '#fff', 0.22, 0),
    ('en', 'ENGLAND', -4.2, 50.45, 32, 35.6, -4, '#fff', 0.22, 0),
    ('l161', '', -6.25, 49.25, 46, 37.2, -70, '#FF7A1A', 0.06, 1),
    ('sco', 'SCHOTTLAND', -3.9, 58.3, 26, 44.0, -4, '#fff', 0.22, 0),
    ('shet', 'SHETLAND', -2.5, 60.35, 24, 44.0, -4, '#fff', 0.22, 0),
    ('nor', 'NORWEGEN', 7.6, 61.2, 30, 44.0, -4, '#fff', 0.22, 0),
    ('l476', '', 1.6, 59.6, 52, 45.0, -3, '#FF7A1A', 0.06, 1),
    ('kiel', 'KIEL', 10.13, 54.32, 34, 28.4, 0, '#fff', 0.25, 0),
    ('rhein', 'RHEIN', 5.9, 51.55, 26, 52.0, -4, '#fff', 0.2, 0),
    ('elbe', 'ELBE', 10.4, 53.25, 26, 52.6, -4, '#fff', 0.2, 0),
    ('themse', 'THEMSE', -0.6, 51.95, 26, 53.2, -4, '#fff', 0.2, 0),
    ('atl', 'ATLANTIK', -8.6, 57.0, 30, 58.4, -6, '#CFE6FF', 0.3, 0),
]
labels = {}
for (k, text, lo, la, px, ts, rot, col, sp, ctr) in LAB:
    s = cam_at(ts + 0.6)
    x, y = P(lo, la)
    if k == 'kiel':
        y -= 48 / s
    labels[k] = dict(t=text, x=x, y=y, r=rot, fs=round(px / s, 1), c=col, sp=sp, n=ctr)

pts = {
    'kiel': P(10.13, 54.32), 'mk1': P(-4.98, 49.25), 'mk2': P(-3.0, 58.75),
    'pump0': P(-5.02, 49.3), 'pump1': P(-1.75, 59.47), 'pump2': P(2.0, 60.38),
}
cam = [[t, d] + P(lo, la) + [s, tilt, e] for (t, d, lo, la, s, tilt, e) in CAM]
cam0 = P(CAM0[0], CAM0[1]) + [CAM0[2], CAM0[3]]

data = dict(paths=paths, lens=lens, flags=flags, flagW=flag_w, labels=labels, pts=pts, cam=cam, cam0=cam0,
            det=[det['ox'] - OX, det['oy'] - OY, det['W'], det['H']], world=[17408, 16384])

JS = open('/tmp/claude-0/work/scripts/map_engine.js').read()
html = f'''<template>
  <style>
    #root {{ position: absolute; inset: 0; overflow: hidden; background: #06152A; }}
    #map-tw {{ position: absolute; left: -460px; top: -1200px; width: 2000px; height: 3200px; transform-origin: 1000px 2000px; }}
    #map-cv {{ position: absolute; left: 0; top: 0; width: 2000px; height: 3200px; }}
    .map-src {{ position: absolute; left: 0; top: 0; width: 1px; height: 1px; opacity: 0; }}
    #map-fontprobe {{ position: absolute; left: 0; top: 0; font-family: 'Oswald', sans-serif; font-weight: 700; font-size: 10px; opacity: 0; }}
  </style>
  <div id="root" data-composition-id="map" data-width="1080" data-height="1920" data-layout-allow-overflow data-layout-ignore>
    <img id="map-wide" class="map-src" src="assets/wide.jpg" alt="">
    <img id="map-detail" class="map-src" src="assets/detail.webp" alt="">
    <img id="map-flood" class="map-src" src="assets/flood.png" alt="">
    <div id="map-fontprobe">NORDSEE ÄÖÜ 0123456789 KM²</div>
    <div id="map-tw"><canvas id="map-cv" width="2000" height="3200"></canvas></div>
  </div>
  <script>
    (function () {{
      const DATA = {json.dumps(data, ensure_ascii=False)};
      const DUR = {DUR};
{JS}
    }})();
  </script>
</template>
'''
open(PROJ + '/compositions/map.html', 'w').write(html)
print('map.html', len(html) // 1024, 'KB')
