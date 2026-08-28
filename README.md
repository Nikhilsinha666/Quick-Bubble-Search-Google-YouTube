# Context Search for Anki

Select a word or phrase on a flashcard, right-click it, and search it on
**YouTube** or **Google Images** without leaving Anki.

![Context search submenu in the reviewer](screenshots/01-context-menu.png)

Works in:

- the reviewer (question and answer side) and the card previewer
- the note editor, in the **Add** window and in **Browse**
- the reviewer **More** menu (`m` key), when text is selected

The entries only appear when something is actually selected, so the normal
right-click menu stays clean.

## Install

**From AnkiWeb** (recommended once published)

`Tools > Add-ons > Get Add-ons...` and paste the code `<ANKIWEB-ID>`.

**From a release file**

Download `context_search.ankiaddon` from the
[releases page](https://github.com/Nikhilsinha666/anki-context-search/releases),
then double-click it, or use `Tools > Add-ons > Install from file...`.

**From source**

1. `Tools > Add-ons > View Files` - this opens `.../Anki2/addons21`.
2. Copy the `context_search` folder into it.
3. Restart Anki.

## Usage

1. Select any word or phrase on the card.
2. Right-click the selection.
3. Choose `Context search > YouTube: "..."` or `Context search > Google Images: "..."`.

The search opens in your normal web browser.

The selection is tidied up before searching: `{{c1::word}}` is searched as
`word`, `[sound:...]` tags are dropped, line breaks collapse into spaces, and
surrounding quotes, brackets and commas are trimmed.

## Configuration

`Tools > Add-ons > Context Search (YouTube & Google Images) > Config`

- rename the submenu, or put the searches straight into the right-click menu
- switch it off per screen (reviewer / editor / More menu)
- add your own providers with a URL template:

```json
{ "name": "Wikipedia", "url": "https://en.wikipedia.org/w/index.php?search={query}", "enabled": true }
```

| Placeholder    | Encoding                              | Example                  |
| -------------- | ------------------------------------- | ------------------------ |
| `{query}`      | query string, spaces become `+`       | `?q={query}`             |
| `{query_path}` | path segment, spaces become `%20`     | `/word/{query_path}/`    |
| `{query_raw}`  | no encoding                           | special cases            |

Google web search, Google definitions, Forvo and YouGlish ship pre-written but
disabled - flip `"enabled": true` to use them. Every option is documented in
[`context_search/config.md`](context_search/config.md), which is also what Anki
shows next to the config editor.

## Development

```
context_search/       the add-on itself
  __init__.py         hooks + search logic
  config.json         default settings
  config.md           config help shown inside Anki
  manifest.json       package id, name, version
tools/check_addon.py  package sanity checks (no Anki needed)
build.ps1             builds dist/context_search.ankiaddon
docs/                 AnkiWeb description + publishing steps
screenshots/          images linked from the AnkiWeb page
```

```powershell
python tools\check_addon.py   # validate the package
.\build.ps1                   # build dist\context_search.ankiaddon
```

The add-on hooks `webview_will_show_context_menu`,
`editor_will_show_context_menu` and `reviewer_will_show_context_menu`, reads the
selection with `selectedText()`, and opens the resulting URL with
`aqt.utils.openLink`. Nothing is sent anywhere else.

Publishing steps live in [`docs/publishing.md`](docs/publishing.md).

## License

MIT - see [LICENSE](LICENSE).
