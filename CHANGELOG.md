# Changelog

## 1.3.0 - 2026-08-30

- Renamed to **Quick Bubble Search (Google & YouTube)**. Same add-on, same
  install code (`458766448`), same settings - only the displayed name, the
  `Tools` entry, the window title and the right-click submenu change. The
  package folder stays `context_search`, so nothing has to be reinstalled.
- A `submenu_label` still holding the old name follows the rename by itself. A
  label you typed yourself is left alone.
- The GitHub repo moved to `Quick-Bubble-Search-Google-YouTube`; the homepage and
  support links point there now. GitHub redirects the old URL.
- Fixed: clicking empty space on a card selected a nearby word and popped the
  icons up. A word is now only picked when the pointer is really over it, so
  blank space does nothing.
- The icons appear for text you select yourself: double-click a word, or drag
  over a phrase. A double click that lands beside the text instead of on it no
  longer selects anything either.
- `popup_trigger` is replaced by **popup_select_on_click** (default `false`).
  Tick *Also select the word on a single click* in the settings, or set the key
  to `true`, for the old single-click behaviour.

## 1.2.0 - 2026-08-28

- New: a settings window instead of raw JSON. Open it from
  `Tools > Context Search (YouTube & Google Images)...` or the **Config** button
  in `Tools > Add-ons`.
- Add any website as a search: name, URL, icon, and a **Test** button that runs
  the search once so you can check the URL before saving. Searches can be
  ticked, reordered and removed from the list.
- Icons can be a built-in logo, a letter or emoji badge, or your own image file.
  Images are copied into `user_files/icons/`, which survives add-on updates.
- Google web search is now on by default, with Google's four-colour G icon,
  next to YouTube and Google Images.
- Saving the settings updates the icons on the card straight away - no need to
  leave and re-enter the review screen.

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
