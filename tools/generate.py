#!/usr/bin/env python3
"""Generate icons.js (gallery) and app_icons.dart (Flutter) from Hugeicons' icons.css.

    python3 tools/generate.py icons.css

icons.css is the only source of truth — there is no JSON metadata endpoint, and the font's
name set does not match the SVG filenames in the Hugeicons GitHub repo.
"""
import json
import re
import sys
from pathlib import Path

CSS = Path(sys.argv[1] if len(sys.argv) > 1 else 'icons.css')
ROOT = Path(__file__).resolve().parent.parent

RULE = re.compile(
    r'\.hgi-stroke\.hgi-([a-z0-9-]+)::before\s*\{\s*content:\s*"\\([0-9a-fA-F]+)"\s*;\s*\}'
)

DART_KEYWORDS = {
    'assert', 'break', 'case', 'catch', 'class', 'const', 'continue', 'default', 'do', 'else',
    'enum', 'extends', 'false', 'final', 'finally', 'for', 'if', 'in', 'is', 'new', 'null',
    'rethrow', 'return', 'super', 'switch', 'this', 'throw', 'true', 'try', 'var', 'void',
    'while', 'with', 'hashCode', 'runtimeType', 'toString', 'noSuchMethod',
}


def camel(name: str) -> str:
    head, *tail = name.split('-')
    return head + ''.join(p[:1].upper() + p[1:] for p in tail)


pairs = sorted(set(RULE.findall(CSS.read_text(encoding='utf-8'))))
if not pairs:
    sys.exit(f'no icon rules matched in {CSS} — the CSS format changed')

seen: dict[str, str] = {}
rows = []
for name, cp in pairs:
    sym, note = camel(name), None

    if sym[0].isdigit():
        sym = 'icon' + sym
        note = f'{name} — Dart identifiers cannot start with a digit'

    if sym in DART_KEYWORDS:
        sym += 'Icon'
        note = name

    if sym in seen:
        base, n = sym, 1
        while sym in seen:
            n += 1
            sym = base + ('Alt' if n == 2 else f'Alt{n}')
        note = f'{name} — camelCases the same as {seen[base]}'

    seen[sym] = name
    rows.append((sym, name, cp.lower(), note))

# Gallery data: [dartSymbol, hugeiconsName, codepoint]
(ROOT / 'icons.js').write_text(
    'const ICONS=' + json.dumps([[s, n, c] for s, n, c, _ in rows], separators=(',', ':')) + ';',
    encoding='utf-8',
)

body = []
for sym, _, cp, note in rows:
    if note:
        body.append(f'  // {note}')
    body.append(f"  static const IconData {sym} = IconData(0x{cp}, fontFamily: _family);")

(ROOT / 'app_icons.dart').write_text(
    f"""import 'package:flutter/widgets.dart';

/// Hugeicons free stroke-rounded set ({len(rows)} glyphs), generated from
/// `use.hugeicons.com/font/icons.css`. A kebab name maps to lowerCamelCase:
/// `arrow-shrink-02` -> `HugeIcons.arrowShrink02`. The handful of names that
/// can't survive that transform carry a comment saying where they came from.
class HugeIcons {{
  const HugeIcons._();

  static const String _family = 'HugeiconsStrokeRounded';

"""
    + '\n'.join(body)
    + '\n}\n',
    encoding='utf-8',
)

renamed = [(s, note) for s, _, _, note in rows if note]
print(f'{len(rows)} icons -> icons.js, app_icons.dart')
print(f'{len(renamed)} renamed:')
for sym, note in renamed:
    print(f'  {sym:<28} {note}')
