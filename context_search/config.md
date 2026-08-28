## Context Search (YouTube & Google Images)

Click or select a word on a card and small search icons appear next to it.
The same searches are also in the right-click menu.

**The easy way to change all of this is the settings window:**
`Tools > Context Search (YouTube & Google Images)...`, or the **Config** button
next to the add-on in `Tools > Add-ons`. It lets you tick searches, reorder
them, and add any website with its own icon.

This file documents the underlying keys, in case you prefer editing
`config.json` by hand.

### Floating icons

- **popup_enabled** - `false` turns the floating icons off and leaves only the
  right-click menu.
- **popup_trigger** - `"click"` shows the icons as soon as you click a word
  (the word gets selected for you). `"selection"` only shows them when you
  select text yourself, by double-click or dragging.
- **popup_icon_size** - icon button size in pixels (18-64).

The icons appear on the review screen, the previewer and the card layout
screen. Press `Esc`, scroll, or click elsewhere to dismiss them.

### Right-click menu

- **use_submenu** - `true` puts the searches inside a
  `Context Search (YouTube & Google Images)` submenu, `false` puts them straight
  into the right-click menu.
- **submenu_label** - name of that submenu. It defaults to the add-on's full
  name; shorten it here if you want a smaller right-click menu.
- **enable_in_reviewer** - show the searches while reviewing / previewing cards.
  Set this to `false` if you only want the floating icons there.
- **enable_in_editor** - show the searches in the note editor (Add and Browse).
  The floating icons do not appear in the editor, so keep this on if you look
  words up while writing notes.
- **enable_in_more_menu** - also show them in the reviewer `More` menu (`m` key).
- **show_selection_in_label** - append the selected text to each menu entry,
  e.g. `YouTube: "photosynthesis"`.
- **max_label_length** - how much of the selection is shown in the label.

### Shared options

- **max_query_chars** - selections longer than this are trimmed before searching.
- **strip_cloze_markers** - `{{c1::word}}` is searched as `word`.
- **strip_sound_tags** - remove `[sound:...]` from the selection.
- **strip_surrounding_punctuation** - drop quotes, commas, brackets, etc. from
  the start and end of the selection.

### searches

A list of providers. Each entry has:

- **name** - text shown in the menu, and the icon's tooltip.
- **url** - the search URL, with a placeholder for the selected text.
- **enabled** - `false` hides the entry without deleting it.
- **icon** - one of:

| Value             | Result                                                     |
| ----------------- | ---------------------------------------------------------- |
| `youtube`         | YouTube logo                                               |
| `google`          | Google-coloured magnifying glass                           |
| `google-images`   | Google Images picture icon                                 |
| `search`          | plain magnifying glass                                     |
| `text:W`, `text:📖` | badge with that letter or emoji (1-2 characters)          |
| `file:logo.png`   | image from `user_files/icons/` (the settings window puts it there for you) |
| `""`              | badge with the first letter of the name                    |

Placeholders you can use in **url**:

| Placeholder     | Encoding                                    | Use for            |
| --------------- | ------------------------------------------- | ------------------ |
| `{query}`       | query-string encoding (spaces become `+`)   | `?q={query}`       |
| `{query_path}`  | path encoding (spaces become `%20`)         | `/word/{query_path}/` |
| `{query_raw}`   | no encoding                                 | special cases      |

If a URL has no placeholder, the encoded selection is appended to the end.

Example of an extra provider:

```json
{ "name": "Wikipedia", "url": "https://en.wikipedia.org/w/index.php?search={query}", "icon": "search", "enabled": true }
```

Saving from the settings window applies everything straight away, including the
floating icons. If you edit `config.json` by hand instead, leave and re-enter
the review screen for the icons to pick up the change.

Images you add stay in `user_files/icons/`, which survives add-on updates.
