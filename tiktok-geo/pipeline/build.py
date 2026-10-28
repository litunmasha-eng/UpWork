#!/usr/bin/env python3
"""Generates the HyperFrames project files for the Nordsee video."""
import json, math, os, html

PROJ = '/tmp/claude-0/work/nordsee'
A = PROJ + '/assets/'
geo = json.load(open(A + 'geo.json'))
words = json.load(open('/tmp/claude-0/work/words.json'))
DUR = 75.5
W, H = 1080, 1920
CY = 800  # screen y the camera looks at

OX, OY = 24576, 12288
WORLD_W, WORLD_H = 17408, 16384


def P(lon, lat):
    n = 2 ** 8 * 256
    x = (lon + 180) / 360 * n
    y = (1 - math.log(math.tan(math.radians(lat)) + 1 / math.cos(math.radians(lat))) / math.pi) / 2 * n
    return round(x - OX, 1), round(y - OY, 1)


ORANGE = '#FF7A1A'
MINT = '#4DF0C8'
NAVY = '#06152A'

# ---------------------------------------------------------------- camera
# (time, duration, lon, lat, scale, tilt, ease)
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
    (26.0, 1.3, 10.0, 54.6, 0.62, 30, 'power3.inOut'),
    (27.3, 5.6, 10.1, 54.45, 0.7, 32, 'sine.inOut'),
    (32.95, 1.35, -4.75, 49.25, 1.02, 40, 'power3.inOut'),
    (34.3, 5.4, -4.8, 49.2, 1.12, 42, 'sine.inOut'),
    (39.75, 1.3, -2.7, 58.9, 0.86, 36, 'power3.inOut'),
    (41.05, 1.4, -2.2, 59.2, 0.8, 34, 'sine.inOut'),
    (42.45, 1.6, 1.4, 59.7, 0.38, 30, 'power2.inOut'),
    (44.05, 3.6, 1.6, 59.75, 0.41, 32, 'sine.inOut'),
    (50.75, 1.0, 2.0, 55.9, 0.255, 24, 'power3.inOut'),
    (51.75, 8.0, 2.0, 55.8, 0.275, 26, 'sine.inOut'),
    (67.3, 5.4, 6.0, 53.2, 0.135, 4, 'power2.inOut'),
    (72.7, 2.8, 6.0, 53.2, 0.13, 0, 'sine.inOut'),
]


def cam_at(t):
    """scale in effect at time t (target of the last started move)"""
    s = CAM0[2]
    for c in CAM:
        if c[0] <= t:
            s = c[4]
    return s


# ---------------------------------------------------------------- svg helpers
def path_el(id_, d, **attrs):
    a = ' '.join(f'{k.rstrip("_").replace("_", "-")}="{v}"' for k, v in attrs.items())
    return f'<path id="{id_}" d="{d}" {a}/>' if id_ else f'<path d="{d}" {a}/>'


def poly_d(pts):
    return 'M' + ' L'.join(f'{x},{y}' for x, y in pts)


def label(id_, text, lon, lat, px, t_show, rot=0, color='#fff', anchor='middle', weight=700, spacing=0.12, dy=0, counter=False):
    """map label sized for the camera scale at t_show; letters in tspans for the typewriter"""
    s = cam_at(t_show + 0.6)
    fs = px / s
    x, y = P(lon, lat)
    y += dy / s
    chars = html.escape(text) if counter else ''.join(f'<tspan class="ch">{html.escape(c)}</tspan>' for c in text)
    sw = fs * 0.16
    return ((f'<text id="{id_}" class="maplabel" opacity="0" x=' if counter else f'<text id="{id_}" class="maplabel" x=') + f'"{x}" y="{y}" font-size="{fs:.0f}" font-weight="{weight}" '
            f'letter-spacing="{fs*spacing:.1f}" text-anchor="{anchor}" fill="{color}" stroke="{NAVY}" '
            f'stroke-width="{sw:.1f}" stroke-opacity="0.85" paint-order="stroke" '
            f'transform="rotate({rot} {x} {y})">{chars}</text>')


def flag_svg(code):
    if code == 'DEU':
        return '<rect width="60" height="40" fill="#000"/><rect y="13.3" width="60" height="13.4" fill="#DD0000"/><rect y="26.7" width="60" height="13.3" fill="#FFCE00"/>'
    if code == 'NLD':
        return '<rect width="60" height="40" fill="#AE1C28"/><rect y="13.3" width="60" height="13.4" fill="#fff"/><rect y="26.7" width="60" height="13.3" fill="#21468B"/>'
    if code == 'BEL':
        return '<rect width="20" height="40" fill="#000"/><rect x="20" width="20" height="40" fill="#FDDA24"/><rect x="40" width="20" height="40" fill="#EF3340"/>'
    if code == 'FRA':
        return '<rect width="20" height="40" fill="#0055A4"/><rect x="20" width="20" height="40" fill="#fff"/><rect x="40" width="20" height="40" fill="#EF4135"/>'
    if code == 'DNK':
        return '<rect width="60" height="40" fill="#C8102E"/><rect x="18" width="7" height="40" fill="#fff"/><rect y="16.5" width="60" height="7" fill="#fff"/>'
    if code == 'NOR':
        return ('<rect width="60" height="40" fill="#BA0C2F"/><rect x="16" width="10" height="40" fill="#fff"/><rect y="15" width="60" height="10" fill="#fff"/>'
                '<rect x="18.5" width="5" height="40" fill="#00205B"/><rect y="17.5" width="60" height="5" fill="#00205B"/>')
    if code == 'GBR':
        return ('<rect width="60" height="40" fill="#012169"/>'
                '<path d="M0,0 L60,40 M60,0 L0,40" stroke="#fff" stroke-width="8"/>'
                '<path d="M0,0 L60,40 M60,0 L0,40" stroke="#C8102E" stroke-width="3"/>'
                '<path d="M30,0 V40 M0,20 H60" stroke="#fff" stroke-width="12"/>'
                '<path d="M30,0 V40 M0,20 H60" stroke="#C8102E" stroke-width="7"/>')


# ---------------------------------------------------------------- geometry
DAM1 = [(-4.78, 48.56), (-4.95, 49.0), (-5.08, 49.5), (-5.19, 49.95)]
DAM2 = [(-3.05, 58.64), (-2.95, 58.86), (-2.75, 59.08), (-2.2, 59.35), (-1.62, 59.53), (-1.3, 59.86),
        (-0.9, 60.12), (1.0, 60.3), (3.0, 60.45), (4.95, 60.55)]
d1 = [P(*p) for p in DAM1]
d2 = [P(*p) for p in DAM2]

FLAGS = {'GBR': (-1.6, 52.7), 'FRA': (2.3, 47.9), 'NOR': (8.6, 60.9), 'DNK': (9.1, 56.0),
         'DEU': (10.0, 51.6), 'NLD': (5.7, 52.4), 'BEL': (4.6, 50.65)}

svg = []
# north sea: fill + glow line
svg.append(path_el('ns-fill', geo['northsea'], fill=MINT, fill_opacity='0', fill_rule='evenodd', stroke='none'))
svg.append(path_el('ns-flood', geo['northsea'], fill='#9FFFE6', fill_opacity='0', fill_rule='evenodd', stroke='none'))
# coastline glow (used at the "lake" moment and the end)
svg.append(f'<g id="coast-glow" opacity="0">'
           + path_el('', geo['coast'], fill='none', stroke='#fff', stroke_opacity='0.18', stroke_width='14', class_='nsw', data_sw='5', stroke_linejoin='round')
           + path_el('', geo['coast'], fill='none', stroke='#fff', stroke_opacity='0.85', stroke_width='4', class_='nsw', data_sw='1.4', stroke_linejoin='round')
           + '</g>')
svg.append(path_el('ns-glow', geo['northsea'], fill='none', stroke=MINT, stroke_opacity='0.35', stroke_width='30', class_='nsw', data_sw='9', pathLength='1000', stroke_dasharray='1000 1200', stroke_dashoffset='1100', stroke_linejoin='round'))
svg.append(path_el('ns-line', geo['northsea'], fill='none', stroke='#EFFFFA', stroke_width='9', class_='nsw', data_sw='2.6', pathLength='1000', stroke_dasharray='1000 1200', stroke_dashoffset='1100', stroke_linejoin='round'))
# countries
for c, d in geo['countries'].items():
    svg.append(path_el(f'c-{c}', d, fill=ORANGE, fill_opacity='0', stroke='#FFE2CC', stroke_opacity='0', stroke_width='8', class_='nsw country', data_sw='1.6', stroke_linejoin='round'))
# rivers
for r, d in geo['rivers'].items():
    svg.append(f'<g id="riv-{r}">'
               + path_el('', d, fill='none', stroke=MINT, stroke_opacity='0.4', stroke_width='40', class_='nsw rv', data_sw='11', pathLength='1000', stroke_dasharray='1000 1200', stroke_dashoffset='1100', stroke_linecap='round', stroke_linejoin='round')
               + path_el('', d, fill='none', stroke='#E9FFF8', stroke_width='12', class_='nsw rv', data_sw='3.4', pathLength='1000', stroke_dasharray='1000 1200', stroke_dashoffset='1100', stroke_linecap='round', stroke_linejoin='round')
               + path_el(f'rflow-{r}', d, fill='none', stroke='#ffffff', stroke_opacity='0', stroke_width='14', class_='nsw', data_sw='3.8', pathLength='1000', stroke_dasharray='14 40', stroke_dashoffset='0', stroke_linecap='round')
               + '</g>')

# dams


def dam(id_, pts):
    d = poly_d(pts)
    return (f'<g id="{id_}">'
            + path_el('', d, fill='none', stroke='#000', stroke_opacity='0.45', stroke_width='60', class_='nsw dm', data_sw='15', pathLength='1000', stroke_dasharray='1000 1200', stroke_dashoffset='1100', stroke_linecap='round', stroke_linejoin='round', transform='translate(8,14)')
            + path_el('', d, fill='none', stroke='#DCE4EC', stroke_width='44', class_='nsw dm', data_sw='11', pathLength='1000', stroke_dasharray='1000 1200', stroke_dashoffset='1100', stroke_linecap='round', stroke_linejoin='round')
            + path_el('', d, fill='none', stroke='#8FA0B2', stroke_width='44', class_='nsw dm', data_sw='11', pathLength='1000', stroke_dasharray='3 9', stroke_dashoffset='0', stroke_opacity='0', stroke_linecap='butt')
            + path_el('', d, fill='none', stroke=ORANGE, stroke_width='16', class_='nsw dm', data_sw='4', pathLength='1000', stroke_dasharray='1000 1200', stroke_dashoffset='1100', stroke_linecap='round', stroke_linejoin='round', transform='translate(0,-10)')
            + '</g>')


svg.append(dam('dam1', d1))
svg.append(dam('dam2', d2))

# outflow arrows (pumps push water into the Atlantic)
OUTS = [
    [(-5.0, 49.3), (-6.4, 49.2), (-7.8, 49.0)],
    [(-1.8, 59.45), (-2.6, 60.2), (-3.4, 60.9)],
    [(2.0, 60.38), (1.6, 61.3), (1.2, 62.2)],
]
for i, o in enumerate(OUTS):
    d = poly_d([P(*p) for p in o])
    svg.append(f'<g id="out{i}" opacity="0">'
               + path_el('', d, fill='none', stroke=ORANGE, stroke_opacity='0.35', stroke_width='44', class_='nsw', data_sw='10', stroke_linecap='round')
               + path_el(f'outf{i}', d, fill='none', stroke='#FFE7D2', stroke_width='14', class_='nsw', data_sw='3.4', stroke_dasharray='30 34', stroke_dashoffset='0', stroke_linecap='round')
               + '</g>')

# ground markers (pulsing rings)


def marker(id_, lon, lat, px, t):
    s = cam_at(t + 0.6)
    x, y = P(lon, lat)
    r = px / s
    return (f'<g id="{id_}" opacity="0">'
            f'<circle class="mk-pulse" cx="{x}" cy="{y}" r="{r*2.4:.0f}" fill="none" stroke="{ORANGE}" stroke-width="{r*0.18:.0f}"/>'
            f'<circle cx="{x}" cy="{y}" r="{r*1.15:.0f}" fill="none" stroke="#fff" stroke-width="{r*0.22:.0f}"/>'
            f'<circle cx="{x}" cy="{y}" r="{r*0.55:.0f}" fill="{ORANGE}"/></g>')


svg.append(marker('mk-kiel', 10.13, 54.32, 13, 28.4))
svg.append(marker('mk-d1', -4.98, 49.25, 14, 33.0))
svg.append(marker('mk-d2', -3.0, 58.75, 13, 39.7))

# pumps


def pump(id_, lon, lat, px, t):
    s = cam_at(t)
    x, y = P(lon, lat)
    r = px / s
    blades = ''.join(f'<path d="M{x},{y} Q{x + r*0.55},{y - r*0.25} {x + r*0.62},{y - r*0.62} Q{x + r*0.15},{y - r*0.5} {x},{y}Z" fill="#fff" transform="rotate({a} {x} {y})"/>' for a in (0, 120, 240))
    return (f'<g id="{id_}" opacity="0"><circle cx="{x}" cy="{y}" r="{r:.0f}" fill="{NAVY}" stroke="{ORANGE}" stroke-width="{r*0.16:.0f}"/>'
            f'<g class="imp">{blades}</g><circle cx="{x}" cy="{y}" r="{r*0.14:.0f}" fill="{ORANGE}"/></g>')


svg.append(pump('pump0', -5.02, 49.3, 26, 56))
svg.append(pump('pump1', -1.75, 59.47, 26, 56))
svg.append(pump('pump2', 2.0, 60.38, 26, 56))

# flags
for c, (lo, la) in FLAGS.items():
    s = cam_at(12.4)
    wpx = 66 / s
    x, y = P(lo, la)
    k = wpx / 60
    svg.append(f'<g id="fl-{c}" opacity="0"><g transform="translate({x - wpx/2:.0f},{y - 20*k:.0f}) scale({k:.3f})">'
               f'<rect x="-3" y="-3" width="66" height="46" rx="5" fill="#fff"/>'
               f'<rect x="1" y="5" width="64" height="44" rx="5" fill="#000" opacity="0.25"/>'
               f'<g clip-path="url(#flagclip)">{flag_svg(c)}</g></g></g>')

# labels
svg.append(label('lb-nordsee', 'NORDSEE', 2.9, 56.9, 50, 3.3, rot=-6, spacing=0.3))
svg.append(label('lb-see', 'GRÖSSTER SEE DER ERDE', 2.9, 56.2, 26, 6.6, rot=-6, color='#DFFFF6', spacing=0.14))
svg.append(label('lb-area', '0 KM²', 3.0, 55.6, 60, 9.4, rot=-6, color='#fff', spacing=0.04, counter=True))
svg.append(label('lb-fr', 'FRANKREICH', -3.6, 48.25, 32, 35.0, rot=-4, spacing=0.22))
svg.append(label('lb-en', 'ENGLAND', -4.2, 50.45, 32, 35.6, rot=-4, spacing=0.22))
svg.append(label('lb-161', '0 KM', -6.25, 49.25, 46, 37.2, rot=-70, color=ORANGE, spacing=0.06, counter=True))
svg.append(label('lb-sco', 'SCHOTTLAND', -4.4, 57.6, 30, 41.0, rot=-4, spacing=0.22))
svg.append(label('lb-shet', 'SHETLAND', -2.4, 60.35, 22, 42.6, rot=-4, spacing=0.22))
svg.append(label('lb-nor', 'NORWEGEN', 7.6, 61.2, 26, 43.6, rot=-4, spacing=0.22))
svg.append(label('lb-476', '0 KM', 1.6, 59.6, 52, 45.0, rot=-3, color=ORANGE, spacing=0.06, counter=True))
svg.append(label('lb-kiel', 'KIEL', 10.13, 54.32, 34, 28.4, spacing=0.25, dy=-48))
svg.append(label('lb-rhein', 'RHEIN', 5.9, 51.55, 22, 52.0, rot=-4, spacing=0.2))
svg.append(label('lb-elbe', 'ELBE', 10.4, 53.25, 22, 52.6, rot=-4, spacing=0.2))
svg.append(label('lb-themse', 'THEMSE', -0.6, 51.95, 22, 53.2, rot=-4, spacing=0.2))
svg.append(label('lb-atl', 'ATLANTIK', -8.6, 57.0, 30, 58.4, rot=-6, color='#CFE6FF', spacing=0.3))

svg_markup = '\n'.join(svg)

# ---------------------------------------------------------------- map.html
cx0, cy0 = P(CAM0[0], CAM0[1])
cam_js = []
for (t, d, lo, la, s, tilt, ease) in CAM:
    x, y = P(lo, la)
    cam_js.append(f'cam({t},{d},{x},{y},{s},{tilt},"{ease}");')
cam_js = '\n      '.join(cam_js)

det = json.load(open(A + 'basemaps.json'))['detail']
dx, dy = det['ox'] - OX, det['oy'] - OY

map_html = f'''<template>
  <style>
    #root {{ position: absolute; inset: 0; overflow: hidden; background: {NAVY}; }}
    #map-stage {{ position: absolute; inset: 0; }}
    #map-tilt {{ position: absolute; inset: 0; }}
    #map-center {{ position: absolute; left: 540px; top: {CY}px; width: 0; height: 0; }}
    #map-zoom {{ position: absolute; left: 0; top: 0; width: 0; height: 0; }}
    #map-pan {{ position: absolute; left: 0; top: 0; width: {WORLD_W}px; height: {WORLD_H}px; }}
    #map-wide {{ position: absolute; left: 0; top: 0; width: {WORLD_W}px; height: {WORLD_H}px; }}
    #map-detail {{ position: absolute; left: {dx}px; top: {dy}px; width: {det['W']}px; height: {det['H']}px;
      -webkit-mask-image: linear-gradient(to right, transparent, #000 4%, #000 96%, transparent), linear-gradient(to bottom, transparent, #000 4%, #000 96%, transparent);
      -webkit-mask-composite: source-in; mask-composite: intersect; }}
    #map-flood {{ position: absolute; left: {dx}px; top: {dy}px; width: {det['W']}px; height: {det['H']}px; opacity: 0; }}
    #map-svg {{ position: absolute; left: 0; top: 0; overflow: visible; }}
    .maplabel {{ font-family: 'Oswald', sans-serif; }}
  </style>
  <div id="root" data-composition-id="map" data-width="1080" data-height="1920" data-layout-allow-overflow data-layout-ignore>
    <div id="map-stage">
      <div id="map-tilt">
        <div id="map-center">
          <div id="map-zoom">
            <div id="map-pan">
              <img id="map-wide" src="assets/wide.jpg" alt="">
              <img id="map-detail" src="assets/detail.jpg" alt="">
              <img id="map-flood" src="assets/flood.png" alt="">
              <svg id="map-svg" width="{WORLD_W}" height="{WORLD_H}" viewBox="0 0 {WORLD_W} {WORLD_H}" xmlns="http://www.w3.org/2000/svg">
                <defs><clipPath id="flagclip"><rect width="60" height="40" rx="3"/></clipPath></defs>
{svg_markup}
              </svg>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
  <script>
    (function () {{
      const tl = gsap.timeline({{ paused: true }});
      const q = (s) => document.querySelectorAll(s);
      tl.set("#map-pan", {{ x: {-cx0}, y: {-cy0} }}, 0);
      tl.set("#map-zoom", {{ scale: {CAM0[2]}, transformOrigin: "0 0" }}, 0);
      tl.set("#map-tilt", {{ rotationX: 0, transformPerspective: 1500, transformOrigin: "50% {CY/H*100:.1f}%" }}, 0);
      tl.set(".nsw", {{ attr: {{ "stroke-width": (i, el) => +el.dataset.sw / {CAM0[2]} }} }}, 0);
      function cam(t, d, x, y, s, tilt, ease) {{
        tl.to("#map-pan", {{ x: -x, y: -y, duration: d, ease }}, t);
        tl.to("#map-zoom", {{ scale: s, duration: d, ease }}, t);
        tl.to("#map-tilt", {{ rotationX: tilt, duration: d, ease }}, t);
        tl.to(".nsw", {{ attr: {{ "stroke-width": (i, el) => +el.dataset.sw / s }}, duration: d, ease }}, t);
      }}
      {cam_js}

      function draw(sel, t, d, ease) {{ tl.fromTo(sel, {{ attr: {{ "stroke-dashoffset": 1100 }} }}, {{ attr: {{ "stroke-dashoffset": 0 }}, duration: d, ease: ease || "power2.inOut" }}, t); }}
      function redraw(sel, t, d, ease) {{ tl.set(sel, {{ attr: {{ "stroke-dashoffset": 1100 }} }}, t - 0.3); tl.to(sel, {{ attr: {{ "stroke-dashoffset": 0 }}, duration: d, ease: ease || "power2.inOut" }}, t); }}
      function type(sel, t, per) {{
        tl.fromTo(sel + " .ch", {{ attr: {{ "fill-opacity": 0, "stroke-opacity": 0 }} }}, {{ attr: {{ "fill-opacity": 1, "stroke-opacity": 0.85 }}, duration: 0.01, stagger: per || 0.045 }}, t);
      }}
      function show(sel, t) {{ tl.fromTo(sel, {{ opacity: 0, scale: 0.5, transformOrigin: "50% 50%" }}, {{ opacity: 1, scale: 1, duration: 0.3, ease: "back.out(2.5)" }}, t); }}
      function hide(sel, t) {{ tl.to(sel, {{ opacity: 0, duration: 0.25 }}, t); }}
      function untype(sel, t) {{ tl.to(sel + " .ch", {{ attr: {{ "fill-opacity": 0, "stroke-opacity": 0 }}, duration: 0.2 }}, t); }}
      function counter(sel, t, d, from, to, fmt) {{
        const el = document.querySelector(sel);
        const o = {{ v: from }};
        tl.fromTo(o, {{ v: from }}, {{ v: to, duration: d, ease: "power2.out", onUpdate: () => {{ el.textContent = fmt(o.v); }} }}, t);
      }}
      const de = (v) => Math.round(v).toLocaleString("de-DE");
      // hide every label's letters at start
      tl.set(".maplabel .ch", {{ attr: {{ "fill-opacity": 0, "stroke-opacity": 0 }} }}, 0);

      // 1 hook: north sea outline + dams
      draw("#ns-glow", 3.25, 0.9); draw("#ns-line", 3.25, 0.9);
      type("#lb-nordsee", 3.35, 0.06);
            draw("#dam1 path:not(:nth-child(3))", 4.2, 0.55, "power3.out");
      draw("#dam2 path:not(:nth-child(3))", 4.4, 0.75, "power3.out");
      tl.fromTo("#dam1 path:nth-child(3), #dam2 path:nth-child(3)", {{ attr: {{ "stroke-opacity": 0 }} }}, {{ attr: {{ "stroke-opacity": 0.8 }}, duration: 0.3 }}, 5.0);

      // 2 becomes a lake
      tl.fromTo("#ns-fill", {{ attr: {{ "fill-opacity": 0 }} }}, {{ attr: {{ "fill-opacity": 0.42 }}, duration: 0.5, ease: "power2.out" }}, 6.6);
      tl.fromTo("#ns-flood", {{ attr: {{ "fill-opacity": 0 }} }}, {{ attr: {{ "fill-opacity": 0.35 }}, duration: 0.18, yoyo: true, repeat: 1 }}, 6.7);
      tl.fromTo("#coast-glow", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.6 }}, 6.6);
      untype("#lb-nordsee", 6.5);
      type("#lb-see", 6.75, 0.035);

      // 3 numbers
      untype("#lb-see", 9.2);
      show("#lb-area", 9.5);
      counter("#lb-area", 9.6, 1.4, 0, 500000, (v) => de(v) + "+ KM²");
      tl.to("#ns-fill", {{ attr: {{ "fill-opacity": 0.55 }}, duration: 0.25, yoyo: true, repeat: 1 }}, 11.0);
      hide("#lb-area", 11.9);
      tl.to("#coast-glow", {{ opacity: 0, duration: 0.4 }}, 11.9);
      const order = ["GBR", "NOR", "DNK", "DEU", "NLD", "BEL", "FRA"];
      order.forEach((c, i) => {{
        const t = 12.45 + i * 0.2;
        tl.fromTo("#c-" + c, {{ attr: {{ "fill-opacity": 0, "stroke-opacity": 0 }} }}, {{ attr: {{ "fill-opacity": 0.3, "stroke-opacity": 0.9 }}, duration: 0.25 }}, t);
        tl.fromTo("#fl-" + c, {{ opacity: 0, scale: 0.2, transformOrigin: "50% 50%" }}, {{ opacity: 1, scale: 1, duration: 0.35, ease: "back.out(2.4)" }}, t + 0.05);
      }});
      tl.to(".country", {{ attr: {{ "fill-opacity": 0, "stroke-opacity": 0 }}, duration: 0.3 }}, 14.55);
      tl.to(order.map((c) => "#fl-" + c).join(","), {{ opacity: 0, scale: 0.6, duration: 0.25, stagger: 0.03 }}, 14.5);

      // sci-fi jolt
      tl.fromTo("#map-stage", {{ x: 0 }}, {{ x: 18, duration: 0.05, yoyo: true, repeat: 5, ease: "none" }}, 14.6);

      // 5 sea level rises (Netherlands / German coast)
      tl.to("#ns-fill", {{ attr: {{ "fill-opacity": 0 }}, duration: 0.5 }}, 19.2);
      tl.to("#ns-glow, #ns-line", {{ opacity: 0, duration: 0.4 }}, 19.2);
      tl.to("#dam1, #dam2", {{ opacity: 0, duration: 0.3 }}, 19.2);
      tl.fromTo("#map-flood", {{ opacity: 0 }}, {{ opacity: 0.45, duration: 1.4, ease: "power1.inOut" }}, 20.1);
      tl.to("#map-flood", {{ opacity: 0.95, duration: 1.0, ease: "power2.out" }}, 24.5);
      tl.to("#map-flood", {{ opacity: 0, duration: 0.6 }}, 26.0);

      // 6 Kiel
      tl.fromTo("#mk-kiel", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.2 }}, 28.45);
      tl.fromTo("#mk-kiel .mk-pulse", {{ attr: {{ "stroke-opacity": 1 }}, scale: 0.4, transformOrigin: "50% 50%" }}, {{ attr: {{ "stroke-opacity": 0 }}, scale: 1.3, duration: 1.0, repeat: 3, ease: "power1.out" }}, 28.45);
      type("#lb-kiel", 29.2, 0.06);
      tl.to("#mk-kiel", {{ opacity: 0, duration: 0.3 }}, 32.9);
      untype("#lb-kiel", 32.9);

      // 7 dam 1: Channel
      tl.set("#dam1", {{ opacity: 1 }}, 32.9);
            tl.set("#dam1 path:nth-child(3)", {{ attr: {{ "stroke-opacity": 0 }} }}, 32.9);
      tl.fromTo("#mk-d1", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.2 }}, 33.4);
      tl.fromTo("#mk-d1 .mk-pulse", {{ attr: {{ "stroke-opacity": 1 }}, scale: 0.4, transformOrigin: "50% 50%" }}, {{ attr: {{ "stroke-opacity": 0 }}, scale: 1.3, duration: 0.9, repeat: 3, ease: "power1.out" }}, 33.4);
      tl.to("#c-FRA", {{ attr: {{ "fill-opacity": 0.35, "stroke-opacity": 0.9 }}, duration: 0.3 }}, 35.3);
      type("#lb-fr", 35.3, 0.03);
      tl.to("#c-GBR", {{ attr: {{ "fill-opacity": 0.35, "stroke-opacity": 0.9 }}, duration: 0.3 }}, 36.0);
      type("#lb-en", 36.0, 0.03);
      tl.to("#mk-d1", {{ opacity: 0, duration: 0.3 }}, 37.1);
      redraw("#dam1 path:not(:nth-child(3))", 37.2, 1.3, "power2.inOut");
      tl.to("#dam1 path:nth-child(3)", {{ attr: {{ "stroke-opacity": 0.8 }}, duration: 0.3 }}, 38.4);
      show("#lb-161", 37.3);
      counter("#lb-161", 37.3, 1.2, 0, 161, (v) => Math.round(v) + " KM");
      tl.to("#c-FRA, #c-GBR", {{ attr: {{ "fill-opacity": 0, "stroke-opacity": 0 }}, duration: 0.4 }}, 39.6);
      untype("#lb-fr", 39.6); untype("#lb-en", 39.6); hide("#lb-161", 39.6);

      // 8 dam 2: Scotland - Shetland - Norway
      tl.set("#dam2", {{ opacity: 1 }}, 39.7);
            tl.set("#dam2 path:nth-child(3)", {{ attr: {{ "stroke-opacity": 0 }} }}, 39.7);
      tl.fromTo("#mk-d2", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.2 }}, 40.3);
      tl.fromTo("#mk-d2 .mk-pulse", {{ attr: {{ "stroke-opacity": 1 }}, scale: 0.4, transformOrigin: "50% 50%" }}, {{ attr: {{ "stroke-opacity": 0 }}, scale: 1.3, duration: 0.9, repeat: 1, ease: "power1.out" }}, 40.3);
      type("#lb-sco", 41.5, 0.03);
      tl.to("#mk-d2", {{ opacity: 0, duration: 0.3 }}, 42.3);
      redraw("#dam2 path:not(:nth-child(3))", 42.4, 2.5, "power1.inOut");
      type("#lb-shet", 42.6, 0.04);
      type("#lb-nor", 43.9, 0.04);
      tl.to("#dam2 path:nth-child(3)", {{ attr: {{ "stroke-opacity": 0.8 }}, duration: 0.3 }}, 44.8);
      show("#lb-476", 45.35);
      counter("#lb-476", 45.35, 1.3, 0, 476, (v) => Math.round(v) + " KM");
      untype("#lb-sco", 47.5); untype("#lb-shet", 47.5); untype("#lb-nor", 47.5); hide("#lb-476", 47.5);

      // 9 problem: rivers flow in, pumps push out
      tl.set("#dam1", {{ opacity: 1 }}, 47.5);
      tl.set("#dam1 path:not(:nth-child(3))", {{ attr: {{ "stroke-dashoffset": 0 }} }}, 47.5);
      tl.set("#dam1 path:nth-child(3)", {{ attr: {{ "stroke-opacity": 0.8 }} }}, 47.5);
      tl.to("#ns-fill", {{ attr: {{ "fill-opacity": 0.3 }}, duration: 0.6 }}, 50.9);
      [["Rhein", 52.2], ["Elbe", 52.75], ["Themse", 53.4]].forEach(([r, t]) => {{
        draw("#riv-" + r + " .rv", t, 0.75, "power2.out");
        type("#lb-" + r.toLowerCase(), t + 0.05, 0.04);
        tl.fromTo("#rflow-" + r, {{ attr: {{ "stroke-opacity": 0, "stroke-dashoffset": 0 }} }}, {{ attr: {{ "stroke-opacity": 0.95, "stroke-dashoffset": -540 }}, duration: 5.2, ease: "none" }}, 54.0);
      }});
      tl.to("#ns-fill", {{ attr: {{ "fill-opacity": 0.6 }}, duration: 1.6, ease: "power1.inOut" }}, 54.0);
      tl.to("#ns-flood", {{ attr: {{ "fill-opacity": 0.28 }}, duration: 0.3, yoyo: true, repeat: 3 }}, 54.2);
      ["#pump0", "#pump1", "#pump2"].forEach((p, i) => {{
        tl.fromTo(p, {{ opacity: 0, scale: 0.2, transformOrigin: "50% 50%" }}, {{ opacity: 1, scale: 1, duration: 0.35, ease: "back.out(2.6)" }}, 56.25 + i * 0.12);
        tl.fromTo(p + " .imp", {{ rotation: 0, svgOrigin: document.querySelector(p + " circle").getAttribute("cx") + " " + document.querySelector(p + " circle").getAttribute("cy") }}, {{ rotation: 1440, duration: 4.0, ease: "none" }}, 56.3);
      }});
      tl.to("#ns-fill", {{ attr: {{ "fill-opacity": 0.32 }}, duration: 1.6 }}, 58.5);
      type("#lb-atl", 58.5, 0.04);
      [0, 1, 2].forEach((i) => {{
        tl.fromTo("#out" + i, {{ opacity: 0 }}, {{ opacity: 1, duration: 0.3 }}, 58.5 + i * 0.1);
        tl.fromTo("#outf" + i, {{ attr: {{ "stroke-dashoffset": 0 }} }}, {{ attr: {{ "stroke-dashoffset": -640 }}, duration: 2.0, ease: "none" }}, 58.5);
      }});
      tl.to("#out0, #out1, #out2", {{ opacity: 0, duration: 0.3 }}, 60.2);
      untype("#lb-atl", 60.2);
      ["Rhein", "Elbe", "Themse"].forEach((r) => {{ untype("#lb-" + r.toLowerCase(), 60.0); }});
      tl.to("#riv-Rhein, #riv-Elbe, #riv-Themse", {{ opacity: 0, duration: 0.4 }}, 60.0);
      tl.to("#pump0, #pump1, #pump2", {{ opacity: 0, duration: 0.3 }}, 60.0);

      // 11 pull back to Europe: dams fade, coast glows
      tl.to("#ns-fill", {{ attr: {{ "fill-opacity": 0.45 }}, duration: 0.6 }}, 67.4);
      tl.to("#dam1, #dam2", {{ opacity: 0, duration: 0.5 }}, 71.6);
      tl.to("#ns-fill", {{ attr: {{ "fill-opacity": 0 }}, duration: 0.6 }}, 71.6);
      tl.to("#coast-glow", {{ opacity: 0.9, duration: 0.8 }}, 71.6);
      tl.fromTo("#map-stage", {{ x: 0 }}, {{ x: 22, duration: 0.04, yoyo: true, repeat: 7, ease: "none", immediateRender: false }}, 71.45);

      window.__timelines["map"] = tl;
    }})();
  </script>
</template>
'''
os.makedirs(PROJ + '/compositions', exist_ok=True)
pass  # map.html is generated by build_map.py

# ---------------------------------------------------------------- captions


def clean(t):
    return t.rstrip('.,:;')


groups = []
cur = []
for i, wd in enumerate(words):
    cur.append(i)
    end_sentence = wd['text'][-1] in '.,:;?!'
    gap = (words[i + 1]['start'] - wd['end']) if i + 1 < len(words) else 9
    nchars = sum(len(words[k]['text']) for k in cur)
    if end_sentence or gap >= 0.15 or len(cur) >= 3 or nchars > 16 or (i + 1 < len(words) and nchars + len(words[i + 1]['text']) > 20):
        groups.append(cur)
        cur = []
if cur:
    groups.append(cur)

cap_html = []
cap_js = []
for gi, g in enumerate(groups):
    st = max(0.1, words[g[0]]['start'] - 0.08)
    nxt = words[groups[gi + 1][0]]['start'] - 0.08 if gi + 1 < len(groups) else DUR - 1.2
    en = min(nxt, words[g[-1]]['end'] + 0.6)
    en = max(en, words[g[-1]]['start'] + 0.3)
    en = min(en, nxt)
    spans = ' '.join(f'<span id="cw{k}" class="cw">{html.escape(clean(words[k]["text"]))}</span>' for k in g)
    cap_html.append(f'<div id="cg{gi}" class="cg">{spans}</div>')
    cap_js.append(f'grp("#cg{gi}", {st:.2f}, {en:.2f});')
    for k in g:
        ws = words[k]['start']
        we = max(words[k]['end'], ws + 0.12)
        cap_js.append(f'word("#cw{k}", {ws:.2f}, {min(we, en):.2f});')

captions_html = f'''<template>
  <style>
    #root {{ position: absolute; inset: 0; }}
    .cg {{ position: absolute; left: 0; width: 1080px; top: 1150px; text-align: center; padding: 0 90px;
      font-family: 'Montserrat', sans-serif; font-weight: 800; font-size: 66px; line-height: 1.12; color: #fff;
      opacity: 0; visibility: hidden; overflow: visible; }}
    .cw {{ display: inline-block; margin: 0 6px;
      text-shadow: 0 0 2px #061226, 0 3px 0 #061226, 0 -2px 0 #061226, 3px 0 0 #061226, -3px 0 0 #061226, 0 6px 22px rgba(0,0,0,.55); }}
  </style>
  <div id="root" data-composition-id="captions" data-width="1080" data-height="1920" data-layout-allow-caption-zone>
    {''.join(cap_html)}
  </div>
  <script>
    (function () {{
      const tl = gsap.timeline({{ paused: true }});
      function grp(sel, s, e) {{
        tl.set(sel, {{ visibility: "visible" }}, s);
        tl.fromTo(sel, {{ opacity: 0, scale: 0.86, y: 14 }}, {{ opacity: 1, scale: 1, y: 0, duration: 0.14, ease: "back.out(2)" }}, s);
        tl.to(sel, {{ opacity: 0, duration: 0.08, ease: "power2.in" }}, e - 0.08);
        tl.set(sel, {{ opacity: 0, visibility: "hidden" }}, e);
      }}
      function word(sel, s, e) {{
        tl.fromTo(sel, {{ color: "#ffffff", scale: 1 }}, {{ color: "#FF8A33", scale: 1.09, duration: 0.08, ease: "power2.out" }}, s);
        tl.to(sel, {{ color: "#ffffff", scale: 1, duration: 0.1 }}, e);
      }}
      {chr(10).join('      ' + j for j in cap_js)}
      window.__timelines["captions"] = tl;
    }})();
  </script>
</template>
'''
open(PROJ + '/compositions/captions.html', 'w').write(captions_html)
print('groups', len(groups))

# ---------------------------------------------------------------- index.html
PEAK = {'whoosh': 0.16, 'whoosh-short': 0.16, 'whoosh-cinematic': 2.5, 'pop': 0.12, 'click-soft': 0.07,
        'glitch-1': 0.2, 'impact-bass-1': 0.07, 'impact-bass-2': 0.02, 'riser': 3.47, 'sparkle': 0.03,
        'ping': 0.32, 'typing': 0.45, 'key-press': 0.07}
SFX = [  # (hit time, file, volume, max duration)
    (0.9, 'whoosh-cinematic', 0.55, 3.2),
    (3.3, 'sparkle', 0.35, 1.6),
    (4.3, 'pop', 0.55, 0.5), (4.55, 'pop', 0.5, 0.5),
    (6.7, 'sparkle', 0.4, 1.6),
    (9.6, 'typing', 0.3, 1.3),
    (12.5, 'pop', 0.4, 0.5), (12.9, 'pop', 0.38, 0.5), (13.3, 'pop', 0.36, 0.5), (13.7, 'pop', 0.34, 0.5),
    (14.62, 'glitch-1', 0.5, 2.0),
    (16.55, 'whoosh-short', 0.45, 0.5),
    (18.23, 'impact-bass-1', 0.5, 1.6),
    (19.5, 'whoosh', 0.45, 0.5),
    (22.1, 'typing', 0.28, 1.1),
    (24.55, 'pop', 0.5, 0.5),
    (26.4, 'whoosh', 0.45, 0.5),
    (27.0, 'whoosh-short', 0.35, 0.5), (27.2, 'whoosh-short', 0.3, 0.5),
    (28.5, 'ping', 0.4, 1.0),
    (30.7, 'impact-bass-1', 0.35, 1.4),
    (31.75, 'sparkle', 0.4, 1.6),
    (33.4, 'whoosh-cinematic', 0.5, 3.0),
    (37.3, 'typing', 0.25, 1.2),
    (38.5, 'pop', 0.45, 0.5),
    (40.2, 'whoosh', 0.45, 0.5),
    (42.6, 'whoosh-short', 0.35, 0.5),
    (45.4, 'typing', 0.25, 1.2), (46.65, 'pop', 0.45, 0.5),
    (47.75, 'whoosh', 0.5, 0.5),
    (48.1, 'impact-bass-1', 0.35, 1.4),
    (49.25, 'ping', 0.35, 1.0),
    (50.8, 'whoosh', 0.45, 0.5),
    (51.65, 'impact-bass-1', 0.5, 1.6),
    (52.25, 'click-soft', 0.45, 0.3), (52.8, 'click-soft', 0.45, 0.3), (53.45, 'click-soft', 0.45, 0.3),
    (56.35, 'pop', 0.4, 0.5), (56.5, 'pop', 0.36, 0.5), (56.65, 'pop', 0.34, 0.5),
    (57.95, 'whoosh-short', 0.35, 0.5),
    (58.6, 'whoosh', 0.35, 0.5),
    (60.0, 'whoosh-short', 0.4, 0.5),
    (62.6, 'impact-bass-1', 0.45, 1.4),
    (66.3, 'impact-bass-1', 0.4, 1.4),
    (67.15, 'whoosh', 0.4, 0.5),
    (69.45, 'whoosh-short', 0.4, 0.5),
    (70.0, 'pop', 0.4, 0.5), (70.14, 'pop', 0.4, 0.5),
    (71.45, 'riser', 0.4, 3.5),
    (71.45, 'impact-bass-1', 0.7, 2.0),
    (72.7, 'whoosh', 0.4, 0.5),
    (74.0, 'click-soft', 0.6, 0.3),
]
aud = []
for i, (hit, f, vol, mx) in enumerate(SFX):
    st = round(hit - PEAK[f], 3)
    mstart = 0
    if st < 0:
        mstart = -st
        st = 0
    if f == 'riser':
        st = round(hit - PEAK[f], 3)
    aud.append(f'<audio id="sfx{i}" class="clip" src="assets/sfx/{f}.mp3" data-start="{st}" data-duration="{mx}"'
               + (f' data-media-start="{mstart:.3f}"' if mstart else '')
               + f' data-track-index="{20 + i % 6}" data-volume="{vol}"></audio>')

index = f'''<!doctype html>
<html lang="de" data-resolution="portrait">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <script src="assets/gsap.min.js"></script>
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ margin: 0; width: 1080px; height: 1920px; overflow: hidden; background: {NAVY}; }}
      #root {{ position: relative; width: 1080px; height: 1920px; overflow: hidden; }}
      #map {{ z-index: 1; }} #ovl {{ z-index: 2; }} #caps {{ z-index: 3; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{DUR}" data-width="1080" data-height="1920">
      <div id="map" data-composition-id="map" data-composition-src="compositions/map.html" data-start="0" data-duration="{DUR}" data-track-index="1" data-track-kind="graphics" data-width="1080" data-height="1920"></div>
      <div id="ovl" data-composition-id="overlays" data-composition-src="compositions/overlays.html" data-start="0" data-duration="{DUR}" data-track-index="2" data-track-kind="graphics" data-width="1080" data-height="1920"></div>
      <div id="caps" data-composition-id="captions" data-composition-src="compositions/captions.html" data-start="0" data-duration="{DUR}" data-track-index="3" data-track-kind="captions" data-width="1080" data-height="1920"></div>
      <audio id="vo" class="clip" src="assets/voice.mp3" data-start="0" data-track-index="10" data-volume="1"></audio>
      <audio id="bgm" class="clip" src="assets/music.wav" data-start="0" data-duration="{DUR}" data-track-index="11" data-volume="0.2" data-fade-out="2"></audio>
      {chr(10).join('      ' + a for a in aud)}
    </div>
    <script>
      window.__timelines["main"] = gsap.timeline({{ paused: true }});
    </script>
  </body>
</html>
'''
open(PROJ + '/index.html', 'w').write(index)
print('index written', len(SFX), 'sfx')
