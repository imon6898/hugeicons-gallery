#!/usr/bin/env python3
"""Ship only the multi-tone icons your code actually uses.

    python3 tools/sync_used_icons.py --library ~/hugeicons-pro --app ../calldone

Keep the whole Pro download wherever you like — it never enters the app. This
scans `lib/` for `HugeIconSvg(...)` calls, copies just those SVGs into
`assets/icons/hugeicons/<style>/`, normalises them to `currentColor`, and
deletes assets nothing references any more.

Why not simply bundle everything: SVG assets are not tree-shaken, so all three
multi-tone styles at the full set is ~19.8 MB and 18,684 files in the APK. Fonts
are different — stroke and solid are single-colour, belong in a .ttf, and shrink
to a couple of KB. Use `generate.py` for those.

--library may be laid out either way:
    <library>/bulk/moon-02.svg          style from the folder
    <library>/moon-02.svg               single-style download
"""
import argparse
import re
import shutil
import sys
from pathlib import Path

STYLES = ('twotone', 'duotone', 'bulk')
DEFAULT_STYLE = 'duotone'          # must match HugeIconSvg's default

CALL = re.compile(r'HugeIconSvg\s*\(')
NAME = re.compile(r"""['"]([a-z0-9][a-z0-9-]*)['"]""")
STYLE = re.compile(r'HugeIconStyle\.(\w+)')
HEX = re.compile(r'(fill|stroke)\s*=\s*"(#[0-9a-fA-F]{3,8})"')


def arg_list(src: str, open_paren: int) -> str:
    """The text between this call's own parens.

    A fixed-size window is wrong: it runs past the closing paren and picks up
    the *next* call's `style:`, so an argument-less call silently inherits its
    neighbour's style. Track depth instead, ignoring parens inside strings.
    """
    depth, i, n = 1, open_paren, len(src)
    quote = None
    while i < n and depth:
        i += 1
        if i >= n:
            break
        c = src[i]
        if quote:
            if c == '\\':
                i += 1
            elif c == quote:
                quote = None
        elif c in '\'"':
            quote = c
        elif c == '(':
            depth += 1
        elif c == ')':
            depth -= 1
    return src[open_paren + 1:i]


def used_icons(lib: Path) -> set:
    """Every (style, name) the Dart source asks for."""
    found = set()
    for f in lib.rglob('*.dart'):
        src = f.read_text(encoding='utf-8', errors='ignore')
        for m in CALL.finditer(src):
            args = arg_list(src, m.end() - 1)
            name = NAME.search(args)
            if not name:
                continue
            style = STYLE.search(args)
            found.add(((style.group(1) if style else DEFAULT_STYLE), name.group(1)))
    return found


def index(library: Path) -> dict:
    """(style, name) -> source file, for every SVG in the download."""
    out = {}
    for f in library.rglob('*.svg'):
        parts = {p.lower() for p in f.relative_to(library).parts[:-1]}
        styles = [s for s in STYLES if s in parts] or list(STYLES)
        for s in styles:
            out.setdefault((s, f.stem), f)
    return out


def to_current_color(text: str) -> str:
    hues = {m.group(2).lower() for m in HEX.finditer(text) if m.group(2) != 'none'}
    if len({h[:7] for h in hues}) > 1:
        return text                     # real multi-hue art — leave it alone
    return HEX.sub(lambda m: f'{m.group(1)}="currentColor"', text)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--library', required=True, type=Path, help='the full Pro download')
    ap.add_argument('--app', required=True, type=Path, help='the Flutter project root')
    ap.add_argument('--dry-run', action='store_true')
    a = ap.parse_args()

    lib_dir = a.app / 'lib'
    dest_root = a.app / 'assets' / 'icons' / 'hugeicons'
    if not lib_dir.is_dir():
        sys.exit(f'no lib/ under {a.app}')
    if not a.library.is_dir():
        sys.exit(f'no such library: {a.library}')

    wanted = used_icons(lib_dir)
    have = index(a.library)

    copied, missing = [], []
    for style, name in sorted(wanted):
        src = have.get((style, name))
        if src is None:
            missing.append((style, name))
            continue
        dest = dest_root / style / f'{name}.svg'
        if not a.dry_run:
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(to_current_color(src.read_text(encoding='utf-8')),
                            encoding='utf-8')
        copied.append(dest.relative_to(a.app))

    pruned = []
    for style in STYLES:
        d = dest_root / style
        if not d.is_dir():
            continue
        for f in d.glob('*.svg'):
            if (style, f.stem) not in wanted:
                pruned.append(f.relative_to(a.app))
                if not a.dry_run:
                    f.unlink()

    tag = '  (dry run)' if a.dry_run else ''
    print(f'referenced {len(wanted)}  |  copied {len(copied)}  |  '
          f'pruned {len(pruned)}  |  missing {len(missing)}{tag}')
    for p in copied:
        print(f'  + {p}')
    for p in pruned:
        print(f'  - {p}')
    if missing:
        print('\nnot in the library — check the name, or the style really has no such icon:')
        for style, name in missing:
            print(f'  ? {style}/{name}.svg')
    if not wanted:
        print('\nNo HugeIconSvg(...) calls found. Stroke and solid belong on the '
              'font — Icon(HugeIcons.moon02) — not here.')
    return 1 if missing else 0


if __name__ == '__main__':
    raise SystemExit(main())
