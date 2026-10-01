# Hugeicons — your folder

A searchable gallery for your own Hugeicons download: point it at the folder and every style in it
— Stroke, Solid, Twotone, Duotone and Bulk — shows up with search, categories and the code for each
icon.

**→ [imon6898.github.io/hugeicons-gallery](https://imon6898.github.io/hugeicons-gallery/)**

No icons live on the page itself. The Pro styles can't be redistributed, so the page reads them
from your disk instead, in the browser — nothing is uploaded, and nothing Pro is in this repo. To
use it without the folder, keep the icons in a [private online library](#a-private-online-library)
and open that with a key.

## Pointing it at your folder

Drag the folder that holds the styles onto the page, or click **Choose folder** and pick it:

```
Hug_Icon/
  Stroke/    passport.svg …
  Solid/
  Twotone/
  Duotone/
  Bulk/
```

One folder fills every tab. Or add the style folders one at a time — each fills its own tab
and leaves the others alone. Chrome and Edge remember what you gave them, so a later visit opens it
again with at most one click on **Reopen** per folder; Firefox and Safari ask each visit. A style
folder can sit a level or two down, as it does in Hugeicons' own download.

Dragging is the surer way in. Chrome's folder window reopens inside whatever you picked last, so
after picking `Stroke` it opens *inside* `Stroke`, where pressing Select just picks `Stroke` again —
go up a level first. A drop can't land one level off. (Dropping needs Chrome or Edge.)

## A private online library

A folder only works on the machine it sits on. To open the gallery anywhere, with nothing to pick,
keep the icons in a **private** GitHub repo and give the page a read-only key:

```bash
python3 tools/bundle_library.py --library hugeicons-svg-library --out ../hugeicons-library
```

That packs each style into one gzipped JSON file. `../hugeicons-library` is a clone of the private
repo — commit and push it there. On the page, **Use online library** takes the key: a fine-grained
GitHub token with access to that one repository and Contents on read-only (the **Make a key** link
fills in the rest). The key stays in the browser's storage and goes only to GitHub; every later
visit opens the library by itself, and **forget key** in the footer removes it.

The repo has to stay private: without the key GitHub answers "not found", which is the point. The
page looks for `imon6898/hugeicons-library` — change `LIBRARY` in `index.html` to use your own.

The export carries some leftovers, which the page tidies as it reads:

- **Names are folded to kebab case.** `add circle-half-dot.svg` shows as `add-circle-half-dot`,
  `voice-iD` as `voice-id`, `c++` as `c-plus-plus`. Hovering a tile shows the original file name.
- **Non-icons are skipped.** Figma's green "New tag" badges, default-named shapes like
  `Ellipse 2021`, and the `Text-1`…`Text-24` labels (none of them on a 24×24 canvas) don't get a
  tile. The toast says how many were skipped.
- **Colours follow the theme.** The ink becomes `currentColor`, and white fills — knockouts in
  duotone and bulk — take the tile's own background, so they read right in light and dark.

Click a tile to copy:

| Tab | Copies |
|---|---|
| Stroke | `HugeIcons.callRinging01` — the free font's symbol, if the free font has that icon |
| Solid | `HugeIconsSolid.callRinging01` |
| Twotone / Duotone / Bulk | `HugeIconSvg('call-ringing-01', style: HugeIconStyle.duotone)` |

## Naming

Kebab-case becomes lowerCamelCase:

```
arrow-shrink-02   →   HugeIcons.arrowShrink02
sun-cloud-big-rain-01  →  HugeIcons.sunCloudBigRain01
```

Names that can't make that trip cleanly are marked `!` in the gallery. In the free font there are
seventeen:

- **16 collisions.** `arrow-down-01` and `arrow-down01` are different glyphs that camelCase
  identically, so the irregular one takes an `Alt` suffix — `arrowDown01` and `arrowDown01Alt`.
  Same for `book-up-2`, `circle-slash-2`, `folder-git-2`, `folder-search-2`, `music-3`,
  `navigation-2`, `rows-2/3/4` and `tally-1`…`tally-5`.
- **1 leading digit.** `24-hours-clock` → `icon24HoursClock`, because Dart identifiers can't start
  with a number.

A folder's own names follow the same rules — `3d-move` shows as `icon3dMove`.

Don't assume a `-01` suffix exists, either: the family is `call-done` and `call-done-02`, with no
`call-done-01`. The unsuffixed name *is* the first one.

## Using it in Flutter

The free **stroke-rounded** set is the one thing that does ship here, as a font. Drop
`hgi-stroke-rounded.ttf` into `assets/fonts/` and declare the family:

```yaml
flutter:
  fonts:
    - family: HugeiconsStrokeRounded
      fonts:
        - asset: assets/fonts/hgi-stroke-rounded.ttf
```

Then take `app_icons.dart` — all 6,228 glyphs as `static const IconData`, already generated — and
use it like any `IconData`:

```dart
Icon(HugeIcons.callRinging01, size: 22, color: Colors.teal);
```

Two things that will bite you:

- **Keep every `IconData` compile-time const.** `IconData(lookupByName(x))` hard-fails release
  builds — `Avoid non-constant invocations of IconData`. For API-driven icons use a
  `Map<String, IconData>` of consts.
- **Don't ship a name→IconData map of everything.** Referencing all 6,228 glyphs defeats
  `--tree-shake-icons`, which otherwise cuts the 3 MB font to about 1.4 KB for a few icons.

Twotone, duotone and bulk need two tones, and a font glyph only has one, so those stay SVG. Copy
just the ones your code uses into the app, normalised to `currentColor`:

```bash
python3 tools/sync_used_icons.py --library /path/to/Hug_Icon --app ../your-app
```

It reads `HugeIconSvg(...)` calls under `lib/`, copies those SVGs into
`assets/icons/hugeicons/<style>/`, and prunes the ones nothing references. It reads folders and
names the way the gallery does, so whatever you copied from a tile is found.

## Missing an icon?

Custom artwork goes in [`custom-icons/`](custom-icons/) — see the notes there for the constraints
it has to meet before it can be merged into the font.

## Regenerating

After a Hugeicons release, or once a custom icon is merged:

```bash
curl -sSL -o icons.css https://use.hugeicons.com/font/icons.css
curl -sSL -o hgi-stroke-rounded.ttf https://use.hugeicons.com/font/hgi-stroke-rounded.ttf
python3 tools/generate.py icons.css
python3 tools/categorize.py
```

`generate.py` rewrites `icons.js` and `app_icons.dart`; `categorize.py` tags `icons.js` with
categories and writes the rules to `categories.js`, which the page runs against your folder's
names. `icons.css` is the only source of truth for the free set — there is no JSON metadata
endpoint, and the font's name set doesn't match the Hugeicons GitHub repo's SVG filenames.

## Licence

The free stroke-rounded icons are © Hugeicons, MIT — see [`MIT-Hugeicons.txt`](MIT-Hugeicons.txt),
which must stay with the font in anything you redistribute. The Pro styles stay under your own
Hugeicons licence; they're read from your disk and never stored here. Inter is SIL OFL 1.1. The
gallery page itself is MIT.
