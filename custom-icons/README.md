# Custom icons

SVGs that aren't in the free Hugeicons set. Drop one here in a PR, or attach it to an
[icon request](../../../issues/new?template=icon-request.yml).

Adding a file here does **not** put the glyph in the font — the `.ttf` has to be rebuilt before
`HugeIcons.yourIcon` exists. That's a deliberate step, not an oversight: every rebuild changes the
font bytes and has to be re-tested against tree-shaking.

## What an SVG has to look like

Match the set or it will read as foreign the moment it sits next to a real one:

| | |
|---|---|
| Canvas | 24 × 24 |
| Stroke | 1.5, round cap, round join |
| Fill | none — strokes only |
| Colour | single colour; no gradients, no multi-colour |
| Paths | expand text and boolean ops first; no `<use>`, no embedded images |

Name the file in kebab-case the way Hugeicons would: `fingerprint-scan.svg`, not
`FingerprintScan.svg`.

Multi-colour artwork can't become a font glyph at all — a glyph is a single silhouette. If you need
colour, it stays an SVG asset and gets rendered with `flutter_svg` instead.

## Rebuilding the font

Merging custom glyphs means generating a new TTF from the Hugeicons SVGs plus these, then
regenerating the codepoint map. [`fantasticon`](https://github.com/tancredi/fantasticon) does it:

```bash
fantasticon custom-icons --output dist --font-types ttf --name hgi-custom
```

Keep custom glyphs in their own font family rather than splicing them into the Hugeicons TTF.
Flutter handles several icon families fine, the licence stays unambiguous, and the next Hugeicons
update won't clobber your work.
