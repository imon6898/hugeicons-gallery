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

COLOR = re.compile(r'\b(fill|stroke)\s*=\s*"([^"]*)"')
OPACITY = re.compile(r'(fill|stroke)-opacity\s*=\s*"([0-9.]+)"')

# Figma writes `fill="black"` as readily as `fill="#141B34"`. Matching only hex
# left those untouched, so the icon stayed black and vanished on a dark theme.
NAMED = {
    'black': '#000000', 'white': '#ffffff', 'red': '#ff0000', 'lime': '#00ff00',
    'blue': '#0000ff', 'yellow': '#ffff00', 'cyan': '#00ffff', 'aqua': '#00ffff',
    'magenta': '#ff00ff', 'fuchsia': '#ff00ff', 'silver': '#c0c0c0',
    'gray': '#808080', 'grey': '#808080', 'maroon': '#800000',
    'olive': '#808000', 'green': '#008000', 'purple': '#800080',
    'teal': '#008080', 'navy': '#000080', 'orange': '#ffa500',
}
SKIP = {'none', 'currentcolor', 'transparent', 'inherit', ''}


def norm(value: str):
    """Canonical #rrggbb, or None when the value paints nothing."""
    v = value.strip().lower()
    if v in SKIP:
        return None
    if v in NAMED:
        return NAMED[v]
    if v.startswith('#'):
        h = v[1:]
        if len(h) in (3, 4):
            h = ''.join(c * 2 for c in h[:3])
        return '#' + h[:6]
    m = re.match(r'rgba?\(([^)]*)\)', v)
    if m:
        parts = [p.strip() for p in m.group(1).replace('/', ',').split(',')][:3]
        try:
            return '#' + ''.join(f'{int(float(x)):02x}' for x in parts)
        except ValueError:
            pass
    return v


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
        hues = {h for h in (norm(m.group(2)) for m in COLOR.finditer(src)) if h}

        # Two distinct hues means real colour, not two opacities of one colour.
        if len(hues) > 1:
            multihue.append((f, sorted(hues)))
            skipped += 1
            continue

        out = COLOR.sub(
            lambda m: f'{m.group(1)}="currentColor"' if norm(m.group(2))
            else m.group(0), src)
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
