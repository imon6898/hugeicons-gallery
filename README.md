# Hugeicons gallery

A searchable gallery of Hugeicons that copies an icon the way you work — into Figma, as HTML,
React, Vue, Laravel, Flutter or React Native code, or as a file.

**→ [imon6898.github.io/hugeicons-gallery](https://imon6898.github.io/hugeicons-gallery/)**

Open it and the free **Stroke** set is there: 6,039 icons, MIT, nothing to set up. That is all a
visitor sees — no Pro tabs, and nothing to choose.

Solid, Twotone, Duotone and Bulk are Pro. They can't be redistributed, so nothing Pro is in this
repo; the page reads those from your own download instead: a
[folder on your disk](#pointing-it-at-your-folder), or a
[private online library](#a-private-online-library) opened with a key. The tabs and the buttons for
that appear once the browser has a key or a folder. On a browser that has neither yet, open the
page with `#library` on the end —
[imon6898.github.io/hugeicons-gallery/#library](https://imon6898.github.io/hugeicons-gallery/#library)
— or just drag your folder onto it.

## Copy for…

The **Copy for** menu sets what a click hands over, renames the tiles to match, and opens the
matching instructions under the title.

| Copy for | A click gives you |
|---|---|
| Figma | the SVG — press ⌘V on the canvas and it lands as an editable vector |
| SVG file | `call-ringing-01.svg`, downloaded |
| HTML / PHP | the `<svg>`, for any template |
| React / Next.js | a component, `CallRinging01Icon`, as JSX or TypeScript |
| Vue / Nuxt | a single-file component |
| Laravel Blade | a Blade component, for `<x-icon.call-ringing-01 />` |
| JavaScript / Node.js | ``export const callRinging01Icon = `<svg…>` `` |
| Flutter | `HugeIcons.callRinging01`, or `HugeIconSvg(…)` for a multi-tone style |
| React Native | a `react-native-svg` component |
| Icon name | `call-ringing-01` |

The code formats set the ink to `currentColor`, so CSS `color` paints the icon. White knockouts
stay white, and an icon drawn in two real hues is left as drawn. Figma and SVG file get the
original, untouched.

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

One folder fills every tab — its own Stroke takes the free set's place. Or add the style folders
one at a time: each fills its own tab and leaves the others alone. Chrome and Edge remember what
you gave them, so a later visit opens it again with at most one click on **Reopen** per folder;
Firefox and Safari ask each visit. A style folder can sit a level or two down, as it does in
Hugeicons' own download.

Dragging is the surer way in. Chrome's folder window reopens inside whatever you picked last, so
after picking `Stroke` it opens *inside* `Stroke`, where pressing Select just picks `Stroke` again —
go up a level first. A drop can't land one level off. (Dropping needs Chrome or Edge.)

The export carries some leftovers, which the page tidies as it reads:

- **Names are folded to kebab case.** `add circle-half-dot.svg` shows as `add-circle-half-dot`,
  `voice-iD` as `voice-id`, `c++` as `c-plus-plus`. Hovering a tile shows the original file name.
- **Non-icons are skipped.** Figma's green "New tag" badges, default-named shapes like
  `Ellipse 2021`, and the `Text-1`…`Text-24` labels (none of them on a 24×24 canvas) don't get a
  tile. The toast says how many were skipped.
- **Colours follow the theme.** The ink becomes `currentColor`, and white fills — knockouts in
  duotone and bulk — take the tile's own background, so they read right in light and dark.

## A private online library

A folder only works on the machine it sits on. To open your Pro styles anywhere, with nothing to
pick, keep them in a **private** GitHub repo and give the page a read-only key:

```bash
python3 tools/bundle_library.py --library hugeicons-svg-library --out ../hugeicons-library
```

That packs each style into one gzipped JSON file. `../hugeicons-library` is a clone of the private
repo — commit and push it there. On the page, **Use online library** takes the key: a fine-grained
GitHub token with access to that one repository and Contents on read-only (the **Make a key** link
fills in the rest). The key stays in the browser's storage and goes only to GitHub; every later
visit opens the library by itself, and **forget key** in the footer removes it.

The repo has to stay private: without the key GitHub answers "not found", which is the point. Give
the key only to people your Hugeicons licence covers. The page looks for
`imon6898/hugeicons-library` — change `LIBRARY` in `index.html` to use your own.

## Naming

Kebab-case becomes lowerCamelCase:

```
arrow-shrink-02   →   HugeIcons.arrowShrink02
sun-cloud-big-rain-01  →  HugeIcons.sunCloudBigRain01
```

React, Vue and React Native take the same name with a capital and `Icon` on the end —
`ArrowShrink02Icon` — and JavaScript the lower-case form, `arrowShrink02Icon`.

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

The free **stroke-rounded** set ships here twice: as SVG for the gallery, and as a font for
Flutter. Drop `hgi-stroke-rounded.ttf` into `assets/fonts/` and declare the family:

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

With **Copy for** on Flutter, a click copies the name to type:

| Tab | Copies |
|---|---|
| Stroke | `HugeIcons.callRinging01` — the free font's symbol, if the free font has that icon |
| Solid | `HugeIconsSolid.callRinging01` |
| Twotone / Duotone / Bulk | `HugeIconSvg('call-ringing-01', style: HugeIconStyle.duotone)` |

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
python3 tools/free_icons.py
```

`generate.py` rewrites `icons.js` and `app_icons.dart`; `categorize.py` tags `icons.js` with
categories and writes the rules to `categories.js`, which the page runs against your folder's
names. `icons.css` is the only source of truth for the font — there is no JSON metadata
endpoint, and the font's name set doesn't match the Hugeicons GitHub repo's SVG filenames.

`free_icons.py` rebuilds `free-stroke.json`, the artwork the gallery shows to everyone, from
Hugeicons' own MIT package on npm, `@hugeicons/core-free-icons`. npm spells some names differently
(`TwentyFourHoursClockIcon` for `24-hours-clock`), so each icon takes the font's name where one
matches; 6,022 of the 6,039 do, and those are the ones `HugeIcons.x` exists for.

## Licence

The free stroke-rounded icons are © Hugeicons, MIT — see [`MIT-Hugeicons.txt`](MIT-Hugeicons.txt),
which must stay with the font and with `free-stroke.json` in anything you redistribute. The Pro
styles stay under your own Hugeicons licence; they're read from your disk or your private library
and never stored here. Inter is SIL OFL 1.1. The gallery page itself is MIT.
