#!/usr/bin/env python3
"""Make exported SVGs themeable without flattening their tones.

    python3 tools/svg_currentcolor.py <dir> [--dry-run]

Figma and most icon exporters bake a literal colour into every path
(`fill="#141B34"`). Painting over that in Flutter means
`ColorFilter.mode(c, srcIn)`, which repaints *every* path one colour — fine for
stroke and solid, fatal for twotone/duotone/bulk, where the second tone is the
whole point.

This rewrites the colour to `currentColor` and leaves opacity alone, so
`SvgPicture.asset(..., theme: SvgTheme(currentColor: c))` tints the icon while
its own `fill-opacity` / `stroke-opacity` keep the tones apart.

Multi-*hue* artwork (two genuinely different colours, not two opacities) can't
survive this — those files are reported and skipped.
"""
import re
import sys
from collections import Counter
from pathlib import Path

HEX = re.compile(r'(fill|stroke)\s*=\s*"(#[0-9a-fA-F]{3,8})"')
OPACITY = re.compile(r'(fill|stroke)-opacity\s*=\s*"([0-9.]+)"')


def norm(hexcode: str) -> str:
    """#abc -> #aabbcc, drop alpha, lowercase — so shades compare honestly."""
    h = hexcode.lstrip('#').lower()
    if len(h) in (3, 4):
        h = ''.join(c * 2 for c in h[:3])
    return '#' + h[:6]


def main() -> int:
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    root = Path(sys.argv[1])
    dry = '--dry-run' in sys.argv
    files = sorted(root.rglob('*.svg'))
    if not files:
        sys.exit(f'no .svg files under {root}')

    changed = skipped = 0
    multihue = []

    for f in files:
        src = f.read_text(encoding='utf-8')
        hues = {norm(m.group(2)) for m in HEX.finditer(src) if m.group(2).lower() != 'none'}

        # Two distinct hues means real colour, not two opacities of one colour.
        if len(hues) > 1:
            multihue.append((f, sorted(hues)))
            skipped += 1
            continue

        out = HEX.sub(lambda m: f'{m.group(1)}="currentColor"', src)
        if out == src:
            skipped += 1
            continue
        changed += 1
        if not dry:
            f.write_text(out, encoding='utf-8')

    tones = Counter()
    for f in files:
        tones[len(set(OPACITY.findall(f.read_text(encoding='utf-8'))))] += 1

    print(f'{len(files)} svg  |  rewritten {changed}  |  untouched {skipped}'
          + ('   (dry run)' if dry else ''))
    if multihue:
        print(f'\n{len(multihue)} file(s) use more than one hue — left alone, they '
              'need explicit colours rather than currentColor:')
        for f, hues in multihue[:10]:
            print(f'  {f.name:<34} {", ".join(hues)}')
        if len(multihue) > 10:
            print(f'  … and {len(multihue) - 10} more')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
