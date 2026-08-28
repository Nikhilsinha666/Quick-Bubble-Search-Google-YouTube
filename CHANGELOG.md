# Changelog

## 1.1.0 - 2026-08-28

- New: floating search icons. Click (or select) a word on a card and a small
  bubble with a YouTube and a Google Images icon appears next to it - one click
  runs the search, no right-click needed.
- The bubble lives in a shadow root, so note styling cannot break it, and it
  follows Anki's light/dark theme.
- New config: `popup_enabled`, `popup_trigger` (`click` or `selection`),
  `popup_icon_size`, and a per-provider `icon` (`youtube`, `google-images`,
  `google`, `search`, or empty for a letter badge).
- The right-click menu is unchanged and still works everywhere, including the
  note editor. Set `enable_in_reviewer` to `false` if you only want the icons
  while reviewing.
- The right-click submenu is now labelled with the add-on's full name,
  `Context Search (YouTube & Google Images)`, so the naming matches AnkiWeb,
  the add-on list and the config screen. `submenu_label` still overrides it.

## 1.0.0 - 2026-08-28

First release.

- Right-click a selection on a card to search it on YouTube or Google Images.
- Works in the reviewer, the card previewer, the note editor (Add and Browse)
  and the reviewer `More` menu.
- Menu entries only appear when text is actually selected.
- Selection is cleaned before searching: cloze markers (`{{c1::word}}`),
  `[sound:...]` tags, line breaks and surrounding punctuation are removed.
- Configurable: submenu on/off and its label, per-screen toggles, label
  preview length, and your own search providers via URL templates
  (`{query}`, `{query_path}`, `{query_raw}`).
