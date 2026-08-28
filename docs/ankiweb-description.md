<!--
Paste everything BELOW the line into the "Description" box on
https://ankiweb.net/shared/addons/ (Upload / Edit).

AnkiWeb renders this as Markdown and allows a small subset of HTML.
Images must point at a RAW file URL - a normal github.com/.../blob/... link
shows nothing. Most attributes (width, height, alt) get stripped, so keep the
img tags bare and upload screenshots that already have the size you want.

The image URLs already point at this repo, so they start working as soon as
the screenshots are pushed to the main branch.
-->

---

Select a word on a card, right-click it, and search it on **YouTube** or **Google Images** without leaving Anki.

Handy when a card needs a picture or a real-world example: select the word, right-click, done.

<img src="https://raw.githubusercontent.com/Nikhilsinha666/anki-context-search/main/screenshots/01-context-menu.png">

### How to use

1. Select any word or phrase on the card you are reviewing.
2. Right-click the selection.
3. Pick **Context search â†’ YouTube** or **Context search â†’ Google Images**.

The search opens in your normal web browser.

### Where it works

- while reviewing (question and answer side) and in the card previewer
- in the note editor, both in the **Add** window and in **Browse**
- in the reviewer **More** menu (`m` key), when text is selected

The entries only show up when something is actually selected, so your usual
right-click menu stays exactly as it was.

<img src="https://raw.githubusercontent.com/Nikhilsinha666/anki-context-search/main/screenshots/02-editor-menu.png">

### The selection is cleaned up first

- `{{c1::word}}` is searched as `word`
- `[sound:...]` tags are removed
- multi-line selections become a single line
- quotes, brackets and commas around the selection are trimmed

### Configuration

`Tools â†’ Add-ons â†’ Context Search (YouTube & Google Images) â†’ Config`

<img src="https://raw.githubusercontent.com/Nikhilsinha666/anki-context-search/main/screenshots/03-config.png">

- rename the submenu, or drop the searches straight into the right-click menu
- turn it off per screen (reviewer / editor / More menu)
- add your own search engines with a URL template:

```json
{ "name": "Wikipedia", "url": "https://en.wikipedia.org/w/index.php?search={query}", "enabled": true }
```

Google web search, Google definitions, Forvo and YouGlish are already written
in the config - just switch `"enabled"` to `true`.

### Notes

- Nothing is sent anywhere. The add-on only opens a search URL in your browser.
- Works with Anki 2.1.45 and newer (tested on 25.09).

Source code, bug reports and feature requests:
<https://github.com/Nikhilsinha666/anki-context-search>
