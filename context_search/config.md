## Context Search

Select text on a card (or in the note editor), right-click, and pick a search.

### General options

- **use_submenu** - `true` puts the searches inside a `Context search` submenu,
  `false` puts them straight into the right-click menu.
- **submenu_label** - name of that submenu.
- **enable_in_reviewer** - show the searches while reviewing / previewing cards.
- **enable_in_editor** - show the searches in the note editor (Add and Browse).
- **enable_in_more_menu** - also show them in the reviewer `More` menu (`m` key).
- **show_selection_in_label** - append the selected text to each menu entry,
  e.g. `YouTube: "photosynthesis"`.
- **max_label_length** - how much of the selection is shown in the label.
- **max_query_chars** - selections longer than this are trimmed before searching.
- **strip_cloze_markers** - `{{c1::word}}` is searched as `word`.
- **strip_sound_tags** - remove `[sound:...]` from the selection.
- **strip_surrounding_punctuation** - drop quotes, commas, brackets, etc. from
  the start and end of the selection.

### searches

A list of providers. Each entry has:

- **name** - text shown in the menu.
- **url** - the search URL, with a placeholder for the selected text.
- **enabled** - `false` hides the entry without deleting it.

Placeholders you can use in **url**:

| Placeholder     | Encoding                                    | Use for            |
| --------------- | ------------------------------------------- | ------------------ |
| `{query}`       | query-string encoding (spaces become `+`)   | `?q={query}`       |
| `{query_path}`  | path encoding (spaces become `%20`)         | `/word/{query_path}/` |
| `{query_raw}`   | no encoding                                 | special cases      |

If a URL has no placeholder, the encoded selection is appended to the end.

Example of an extra provider:

```json
{ "name": "Wikipedia", "url": "https://en.wikipedia.org/w/index.php?search={query}", "enabled": true }
```

Changes take effect immediately - no restart needed.
