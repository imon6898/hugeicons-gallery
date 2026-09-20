# Hugeicons — stroke rounded

A searchable gallery of the **6,228 free Hugeicons stroke-rounded glyphs**, rendered from the same
`.ttf` that ships inside the app, with the Dart symbol for each one.

**→ [imon6898.github.io/hugeicons-gallery](https://imon6898.github.io/hugeicons-gallery/)**

Search matches both the Hugeicons name and the Dart name — `call-ringing`, `callRinging` and
`call ringing` all find the same glyph. Click a tile to copy `HugeIcons.callRinging01`.

## Naming

Kebab-case becomes lowerCamelCase:

```
arrow-shrink-02   →   HugeIcons.arrowShrink02
sun-cloud-big-rain-01  →  HugeIcons.sunCloudBigRain01
```

Seventeen names can't make that trip cleanly and are marked `!` in the gallery:

- **16 collisions.** `arrow-down-01` and `arrow-down01` are different glyphs that camelCase
  identically, so the irregular one takes an `Alt` suffix — `arrowDown01` and `arrowDown01Alt`.
  Same for `book-up-2`, `circle-slash-2`, `folder-git-2`, `folder-search-2`, `music-3`,
  `navigation-2`, `rows-2/3/4` and `tally-1`…`tally-5`.
- **1 leading digit.** `24-hours-clock` → `icon24HoursClock`, because Dart identifiers can't start
  with a number.

Don't assume a `-01` suffix exists, either: the family is `call-done` and `call-done-02`, with no
`call-done-01`. The unsuffixed name *is* the first one.

## What isn't here

The free tier is **stroke rounded only** — one style, one weight, outlines. Solid, Bulk, Duotone,
Twotone and the Sharp/Standard corner variants are 8 of Hugeicons' 10 styles and all Pro. If you
need a filled icon for an active nav state, pair this with Material or build the active state from
colour and weight instead of fill.

## Using it in Flutter

Drop `hgi-stroke-rounded.ttf` into `assets/fonts/` and declare the family:

```yaml
flutter:
  fonts:
    - family: HugeiconsStrokeRounded
      fonts:
        - asset: assets/fonts/hgi-stroke-rounded.ttf
```

Then generate the Dart class and use it like any `IconData`:

```dart
Icon(HugeIcons.callRinging01, size: 22, color: Colors.teal);
```

Two things that will bite you:

- **Keep every `IconData` compile-time const.** `IconData(lookupByName(x))` hard-fails release
  builds — `Avoid non-constant invocations of IconData`. For API-driven icons use a
  `Map<String, IconData>` of consts.
- **Don't ship a name→IconData map of everything.** Referencing all 6,228 glyphs defeats
  `--tree-shake-icons`, which otherwise cuts the 3 MB font to about 1.4 KB for a few icons.

## Missing an icon?

[**Open an icon request →**](https://github.com/imon6898/hugeicons-gallery/issues/new?template=icon-request.yml)

The gallery's empty state links straight to that form with the name you searched already filled in.

Custom artwork goes in [`custom-icons/`](custom-icons/) — see the notes there for the constraints
it has to meet before it can be merged into the font.

## Regenerating

After a Hugeicons release, or once a custom icon is merged:

```bash
curl -sSL -o icons.css https://use.hugeicons.com/font/icons.css
curl -sSL -o hgi-stroke-rounded.ttf https://use.hugeicons.com/font/hgi-stroke-rounded.ttf
python3 tools/generate.py icons.css
```

That rewrites `icons.js` for this page and `app_icons.dart` for the Flutter side. `icons.css` is the
only source of truth — there is no JSON metadata endpoint, and the font's name set doesn't match the
Hugeicons GitHub repo's SVG filenames.

## Licence

Icons © Hugeicons, MIT — see [`MIT-Hugeicons.txt`](MIT-Hugeicons.txt), which must stay with the font
in anything you redistribute. Inter is SIL OFL 1.1. The gallery page itself is MIT.
