#!/usr/bin/env python3
"""Pack a Hugeicons download into a private online library for the gallery.

    python3 tools/bundle_library.py --library hugeicons-svg-library --out ../hugeicons-library

Writes one gzipped JSON file per style — `stroke.json.gz`, `solid.json.gz`, … —
mapping each file name to its SVG, and `index.json.gz` listing the names, so the
gallery can name every icon before it downloads any artwork.

--out must be a clone of a PRIVATE GitHub repo. The Pro styles can't be
published, so they never go on the gallery's own site; the page reads them back
through GitHub's API with a read-only key that stays in your browser.

Folders are found the way the gallery finds them — scanHandle() in index.html —
and the SVGs go in untouched: the page tidies names and skips non-icons as it
reads, exactly as it does for a folder on disk.
"""
import argparse
import gzip
import json
import sys
from pathlib import Path

from sync_used_icons import style_of

ROOT = Path(__file__).resolve().parent.parent
STYLES = ('stroke', 'solid', 'twotone', 'duotone', 'bulk')


def pack(data) -> bytes:
    """Gzipped JSON.

    GitHub's API sends a file exactly as stored — no compression on the way —
    and bulk alone is 9.5 MB of SVG, so squeeze it here. mtime=0 keeps a rerun
    byte-identical, so an unchanged library is an empty diff.
    """
    raw = json.dumps(data, ensure_ascii=False, separators=(',', ':'), sort_keys=True)
    return gzip.compress(raw.encode('utf-8'), compresslevel=9, mtime=0)


def scan(library: Path) -> dict:
    """style -> its SVG files. The first folder to claim a style keeps it."""
    found, owner = {}, {}

    def walk(folder: Path, depth: int, style):
        subs = []
        for p in sorted(folder.iterdir()):
            if p.is_dir():
                subs.append(p)
            elif style and p.suffix.lower() == '.svg':
                found.setdefault(style, []).append(p)
        for sub in subs:
            own = style_of(sub.name)
            if own:
                if owner.get(own, sub) != sub:
                    continue
                owner[own] = sub
            if (not own and not style and depth >= 2) or depth >= 6:
                continue
            walk(sub, depth + 1, own or style)

    own = style_of(library.name)
    if own:
        owner[own] = library
    walk(library, 0, own)
    return found


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--library', required=True, type=Path, help='the Hugeicons download')
    ap.add_argument('--out', required=True, type=Path, help='a clone of your private repo')
    a = ap.parse_args()

    if not a.library.is_dir():
        sys.exit(f'no such library: {a.library}')
    # The gallery repo is public, and everything in it gets committed.
    if a.out.resolve().is_relative_to(ROOT):
        sys.exit(f'{a.out} is inside the gallery repo, which is public — '
                 'point --out at a clone of your private repo')

    found = scan(a.library)
    if not found:
        sys.exit(f'no Stroke, Solid, Twotone, Duotone or Bulk folder under {a.library}')

    a.out.mkdir(parents=True, exist_ok=True)
    names = {}
    for style in STYLES:
        bundle = a.out / f'{style}.json.gz'
        art = {}
        for f in found.get(style, []):
            art.setdefault(f.stem, f.read_text(encoding='utf-8'))
        if not art:
            bundle.unlink(missing_ok=True)      # a style that has left the download
            continue
        packed = pack(art)
        bundle.write_bytes(packed)
        names[style] = sorted(art)
        print(f'{style:<8} {len(art):>5} files  {len(packed) / 1e6:4.1f} MB')

    (a.out / 'index.json.gz').write_bytes(pack({'version': 1, 'styles': names}))
    print(f'\nwrote {len(names)} styles to {a.out} — commit and push it to your PRIVATE repo')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
