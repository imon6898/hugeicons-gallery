#!/usr/bin/env python3
"""Build solar/<style>.json — the Solar icon set, a family that is free in every style.

    python3 tools/solar_icons.py

Hugeicons gives away one style and sells four, so the gallery can show a
visitor only Stroke from it. Solar, by 480 Design, is CC BY 4.0 in all six of
its styles — linear, outline, broken, bold, line duotone and bold duotone — so
it gives everyone the rest of the range. This takes the set from Iconify's data
package on npm, @iconify-json/solar, and writes one file per style mapping each
icon's name to its SVG.

CC BY asks for credit: CC-BY-Solar.txt has to stay beside the files, and the
page's footer names the designers.
"""
import io
import json
import sys
import tarfile
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PACKAGE = 'https://registry.npmjs.org/@iconify-json/solar/latest'
# Longest first: "home-bold-duotone" is bold-duotone, not bold.
STYLES = ('bold-duotone', 'line-duotone', 'linear', 'outline', 'broken', 'bold')

CREDIT = '''Solar Icons Set
by 480 Design — https://www.figma.com/community/file/1166831539721848736

Licensed under Creative Commons Attribution 4.0 International (CC BY 4.0):
https://creativecommons.org/licenses/by/4.0/

The files in this folder come from Iconify's data package, @iconify-json/solar
{version}, which optimised the artwork and set its colours to currentColor.
tools/solar_icons.py split them into one file per style.
'''


def main() -> int:
    meta = json.load(urllib.request.urlopen(PACKAGE))
    if meta.get('license') != 'CC-BY-4.0':
        sys.exit(f"{meta['name']} is {meta.get('license')!r} now, not CC-BY-4.0 — check before publishing")
    print(f"{meta['name']} {meta['version']} ({meta['license']})")
    tar = tarfile.open(fileobj=io.BytesIO(urllib.request.urlopen(meta['dist']['tarball']).read()))
    data = json.load(tar.extractfile('package/icons.json'))
    width, height = data.get('width', 24), data.get('height', 24)

    sets = {style: {} for style in STYLES}
    for name, icon in data['icons'].items():
        style = next((s for s in STYLES if name.endswith('-' + s)), None)
        if style is None:
            continue
        w, h = icon.get('width', width), icon.get('height', height)
        # No fill="none" on the root, unlike a Hugeicons file: Solar's shapes
        # say for themselves what is filled, and some rely on the default.
        sets[style][name[:-len(style) - 1]] = (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
            f'viewBox="{icon.get("left", 0)} {icon.get("top", 0)} {w} {h}">{icon["body"]}</svg>\n'
        )

    out = ROOT / 'solar'
    out.mkdir(exist_ok=True)
    for style in sorted(sets, key=STYLES.index):
        if not sets[style]:
            sys.exit(f'no {style} icons found — the package layout changed')
        text = json.dumps(sets[style], ensure_ascii=False, separators=(',', ':'), sort_keys=True)
        (out / f'{style}.json').write_text(text, encoding='utf-8')
        print(f'{style:<13} {len(sets[style]):>5} icons  {len(text.encode()) / 1e6:4.1f} MB')
    (out / 'CC-BY-Solar.txt').write_text(CREDIT.format(version=meta['version']), encoding='utf-8')
    names = set().union(*sets.values())
    print(f'\n{len(names)} icons in {len(sets)} styles -> {out.name}/')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
