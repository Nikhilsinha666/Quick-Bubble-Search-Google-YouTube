# Changelog

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
