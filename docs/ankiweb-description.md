<!--
Paste everything BELOW the line into the "Description" box on
https://ankiweb.net/shared/addons/ (Upload / Edit).

AnkiWeb renders this as Markdown and allows a small subset of HTML.
Images must point at a RAW file URL - a normal github.com/.../blob/... link
shows nothing. Most attributes (width, height, alt) get stripped, so keep the
img tags bare and upload screenshots that already have the size you want.

One screenshot is linked (screenshots/01-context-menu.png) and its URL already
points at this repo, so it renders as soon as the file is on the main branch.
Add more <img> lines later if you take more screenshots - but only for files
that actually exist, otherwise the page shows a broken image.
-->

---

Click a word on a card and small **YouTube** and **Google Images** icons appear right next to it. One click opens the search in your browser.

Handy when a card needs a picture or a real-world example: click the word, click the icon, done.

<img src="https://raw.githubusercontent.com/Nikhilsinha666/anki-context-search/main/screenshots/01-context-menu.png">

### How to use

1. Click any word on the card - it gets selected and the icons appear above it.
2. Click the YouTube or the Google Images icon.

Dragging across a whole phrase works too. `Esc`, scrolling, or clicking somewhere else makes the icons go away.

Prefer the old way? The same searches are also in the **right-click** menu, under **Context Search (YouTube & Google Images)**.

### Where it works

- the floating icons: while reviewing (question and answer side), in the card previewer and in the card layout screen
- the right-click menu: everywhere above, plus the note editor (**Add** and **Browse**) and the reviewer **More** menu (`m` key)

Nothing shows up until there is actually a selection, so it stays out of your way while you study. Both the icons and the menu can be switched off separately in the config.

### The selection is cleaned up first

- `{{c1::word}}` is searched as `word`
- `[sound:...]` tags are removed
- multi-line selections become a single line
- quotes, brackets and commas around the selection are trimmed

### Configuration

`Tools > Add-ons > Context Search (YouTube & Google Images) > Config`

- `popup_enabled` - turn the floating icons off and keep only the right-click menu
- `popup_trigger` - `click` shows the icons on a single click, `selection` only when you select text yourself
- `popup_icon_size` - how big the icons are
- rename the submenu, or drop the searches straight into the right-click menu
- turn the menu off per screen (reviewer / editor / More menu)
- add your own search engines with a URL template:

```json
{ "name": "Wikipedia", "url": "https://en.wikipedia.org/w/index.php?search={query}", "icon": "search", "enabled": true }
```

Google web search, Google definitions, Forvo and YouGlish are already written
in the config - just switch `"enabled"` to `true`.

### Notes

- Nothing is sent anywhere. The add-on only opens a search URL in your browser.
- Works with Anki 2.1.45 and newer (tested on 25.09).

Source code, bug reports and feature requests:
<https://github.com/Nikhilsinha666/anki-context-search>
