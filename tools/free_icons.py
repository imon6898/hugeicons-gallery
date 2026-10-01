#!/usr/bin/env python3
"""Build free-stroke.json — the free Hugeicons set as SVG, for everyone.

    python3 tools/free_icons.py

The Pro styles can't be published, but Stroke Rounded is free: Hugeicons ships it
under MIT as the npm package @hugeicons/core-free-icons. This downloads that
package, turns each icon back into an SVG and writes them all to
free-stroke.json, which the gallery shows to a visitor who has brought nothing
of their own. MIT-Hugeicons.txt has to stay beside it.

The font and the package name their icons differently — `24-hours-clock` in
icons.css is `TwentyFourHoursClockIcon` on npm — so each icon takes the font's
name where one matches, which is what makes `HugeIcons.x` come out right in the
Flutter column. An icon the font doesn't have keeps a name spelled from npm's.
"""
import io
import json
import re
import sys
import tarfile
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PACKAGE = 'https://registry.npmjs.org/@hugeicons/core-free-icons/latest'

ELEMENT = re.compile(r'\[\s*"(\w+)"\s*,\s*\{(.*?)\}\s*\]', re.S)
ATTR = re.compile(r'(\w+)\s*:\s*(?:"((?:[^"\\]|\\.)*)"|([^,}\s]+))')
# SVG attributes that really are camelCase; every other one is hyphenated.
CAMEL = {'viewBox', 'gradientUnits', 'gradientTransform', 'clipPathUnits', 'pathLength',
         'preserveAspectRatio', 'patternUnits', 'maskUnits'}
WORDS = {'Zero': '0', 'One': '1', 'Two': '2', 'Three': '3', 'Four': '4', 'Five': '5',
         'Six': '6', 'Seven': '7', 'Eight': '8', 'Nine': '9', 'TwentyFour': '24'}


def squash(name: str) -> str:
    """Letters and digits only — what a font name and an npm name have in common."""
    return re.sub(r'[^a-z0-9]', '', name.lower())


def spelled(name: str) -> str:
    """npm's name written the font's way: CallRinging01 -> call-ringing-01."""
    s = re.sub(r'(?<=[a-z0-9])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])', '-', name)
    return re.sub(r'(?<=[a-z])(?=\d)', '-', s).lower()


def font_name(name: str, font: dict):
    """The font's name for an npm icon, or None. The font writes a number as a
    digit where npm spells it out: HtmlFive is html-5, ThreeDView is 3d-view."""
    tries = [name]
    for word, digit in WORDS.items():
        if name.endswith(word):
            tries.append(name[:-len(word)] + digit)
        if name.startswith(word):
            tries.append(digit + name[len(word):])
    for t in tries:
        if squash(t) in font:
            return font[squash(t)]
    return None


def svg(source: str) -> str:
    out = ['<svg width="24" height="24" viewBox="0 0 24 24" fill="none" '
           'xmlns="http://www.w3.org/2000/svg">']
    for tag, body in ELEMENT.findall(source):
        attrs = []
        for key, quoted, bare in ATTR.findall(body):
            if key == 'key':                    # React's, not SVG's
                continue
            if key not in CAMEL:
                key = re.sub(r'(?<=[a-z])(?=[A-Z])', '-', key).lower()
            value = (quoted or bare).replace('&', '&amp;').replace('<', '&lt;').replace('"', '&quot;')
            attrs.append(f'{key}="{value}"')
        out.append(f'<{tag} {" ".join(attrs)}/>')
    out.append('</svg>')
    return '\n'.join(out) + '\n'


def main() -> int:
    meta = json.load(urllib.request.urlopen(PACKAGE))
    if meta.get('license') != 'MIT':
        sys.exit(f"{meta['name']} is {meta.get('license')!r} now, not MIT — don't publish it")
    print(f"{meta['name']} {meta['version']} ({meta['license']})")
    tar = tarfile.open(fileobj=io.BytesIO(urllib.request.urlopen(meta['dist']['tarball']).read()))

    css = (ROOT / 'icons.css').read_text(encoding='utf-8')
    font = {squash(n): n for n in re.findall(r'\.hgi-stroke\.hgi-([a-z0-9-]+)::before', css)}

    icons, renamed, empty = {}, 0, 0
    for member in tar.getmembers():
        m = re.fullmatch(r'package/dist/esm/(\w+)Icon\.js', member.name)
        if not m:
            continue
        art = svg(tar.extractfile(member).read().decode('utf-8'))
        if art.count('\n') < 3:                 # no elements came through
            empty += 1
            continue
        name = font_name(m.group(1), font)
        if name is None:
            name, renamed = spelled(m.group(1)), renamed + 1
        icons.setdefault(name, art)

    if not icons:
        sys.exit('no icons found — the package layout changed')
    out = ROOT / 'free-stroke.json'
    out.write_text(json.dumps(icons, ensure_ascii=False, separators=(',', ':'), sort_keys=True),
                   encoding='utf-8')
    print(f'{len(icons)} icons -> {out.name}  ({out.stat().st_size / 1e6:.1f} MB)')
    print(f'{len(icons) - renamed} carry the font\'s name, {renamed} a name spelled from npm\'s'
          + (f', {empty} had no artwork' if empty else ''))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
