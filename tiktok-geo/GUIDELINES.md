# TikTok Geo-Videos (DE) — rules from the owner's feedback

Read this before writing a script or editing a video for this channel. Every rule below comes from a correction the owner made; do not repeat the mistake.

## Format
- Language of the video: **German**. Talk to the owner in **Ukrainian**.
- 9:16, 1080×1920, 30 fps, ~60–75 s. Built with HyperFrames (`npx hyperframes`).
- The owner records the voiceover from the script and sends an MP3; editing starts only after that.
- Reference competitor: GEOallday (animated map explainer). Take the structure, **never copy the look**.

## Script
- When asked for the narrator text: **plain text only** — no timeline, no tables, no notes inside it.
- **All numbers are written out in words** (e.g. "fünfhundertfünfzig Milliarden", "zweitausendzwanzig", "dreihundert Meter"). Never digits in the narrator text. (Digits made TTS/ASR ambiguous: 550 was heard as 515, 25 as 35.)
- On-screen captions and number graphics may still show digits.
- Structure (same as competitor): hook "Die meisten wissen nicht…" → big visual promise → numbers → "klingt wie Science-Fiction" amplifier → context/why → who had the idea → mechanism 1 / 2 / 3 → result in numbers → twist ending → CTA "Folg für mehr Geo-Fakten".
- Flag every fact/number the owner should verify before publishing.
- Topics: the owner wants trend-driven, high-view topics, not only "forgotten mega-projects". Research what is trending right now (news, TikTok/Shorts formats) before proposing; the "Was wäre, wenn …?" (what-if) format is a priority direction. Prefer what-ifs we can show with real data (elevation, rivers, borders).

## Sound (owner complaint: effects far too loud, voice too quiet)
- The **voice is the loudest element**, always. Normalise voice to about −16 LUFS before mixing.
- SFX **very quiet**: per-clip volume × 0.12 of the HyperFrames defaults; loudest SFX moment must sit ≥ 12 dB under voice peaks. Fewer effects rather than more.
- Music bed ~17 dB under the voice, ducked a further ~4 dB while speech plays.
- Final mix −14…−15 LUFS, true peak ≤ −1.5 dBFS. Measure with `ebur128` and report that it was measured, not heard.
- `pipeline/remix.py` does this mix outside the renderer (re-mux with `-c:v copy`, no re-render needed).

## Captions
- 2–3 words per group, Montserrat 800, white with dark outline, **active word orange (#FF8A33)**.
- **Groups must never overlap in time** (group end ≤ next group start) — this bug shipped once.
- Correct the ASR transcript against the script (names, numbers) before building captions.

## Look (our own, not the competitor's)
- Map: own shaded-relief + bathymetry basemap (dark navy sea, muted land), not satellite imagery.
- Palette: orange #FF7A1A (accents, dams, numbers), mint #4DF0C8 (water, rivers), white labels.
- Fonts: Oswald 700 uppercase for map labels/numbers, Montserrat for captions, Space Mono for glitch/blueprint.
- Camera always moving, tilted 3D map, typewriter labels, count-up numbers, flags, own illustrated inserts.
- Hook headline visible on frame 0. CTA end card. Data credit (Natural Earth, Terrain Tiles) on the end card.
- **Show the owner the map style (stills) before the final render.**

## Technical lessons
- Do **not** build the map as giant DOM/SVG layers (17k px) — Chrome drops other layers (captions vanished). Draw the map on one `<canvas>` in an `hf-seek` listener (`pipeline/map_engine.js`), tilt via CSS on a wrapper div.
- In this environment Esri/Carto tiles, HuggingFace and music libraries are blocked; AWS terrarium tiles, raw.githubusercontent (Natural Earth), PyPI, npm and GitHub release assets work.
- Transcription: sherpa-onnx Parakeet TDT v3 (GitHub release) gives word timestamps; Whisper turbo as second opinion.
- Keep the owner posted with an ETA during renders (~11 min per render) and send the file when done. Never commit rendered videos to git.

## Pipeline (`pipeline/`)
`fetch_tiles.py` → `render_base.py` (basemaps) → `geo.py` (Natural Earth overlays) → `asr.py`/`words.py` (word timings) → `music.py` (generated bed) → `build.py` (captions, index, SFX list) + `build_map.py`/`map_engine.js` (canvas map) → `npx hyperframes render` → `remix.py` (final audio mix).
Paths inside the scripts point to `/tmp/claude-0/work/…`; adjust for the new project.
