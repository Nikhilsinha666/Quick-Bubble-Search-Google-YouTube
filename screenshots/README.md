# Screenshots

These files are linked from the AnkiWeb description, so keep the names as they
are - if you rename one, update `docs/ankiweb-description.md` too.

| File                  | What to capture                                                      |
| --------------------- | -------------------------------------------------------------------- |
| `01-context-menu.png` | Reviewer, a word selected on the card, `Context search` submenu open |
| `02-editor-menu.png`  | Add or Browse editor, a word selected, same submenu open             |
| `03-config.png`       | `Tools > Add-ons > Context Search > Config` window                   |

`01-context-menu.png` currently holds a placeholder: the real menu widgets
rendered outside Anki, so the page is not imageless on day one. Replace it with
a proper capture that shows the card behind the menu. `02` and `03` are not in
the repo yet - until you add them, those two `<img>` tags in the AnkiWeb
description show nothing, so either take the shots or delete those two lines.

## Taking them on Windows

`Win + Shift + S` starts a region snip, then paste it into Paint and save as
PNG. Snipping Tool also has a 3 second delay option, which is the easy way to
capture an open menu.

Tips:

- Crop tight around the card and the menu, no full desktop.
- AnkiWeb strips `width` / `height` from `<img>` tags, so the image is shown at
  its real size. Around 900-1100 px wide looks right on the add-on page.
- Keep files under ~1 MB.
- Use a card without personal content.

## How they end up on the AnkiWeb page

AnkiWeb has no image upload. The description points at the raw files in this
repo, e.g.

```
https://raw.githubusercontent.com/Nikhilsinha666/anki-context-search/main/screenshots/01-context-menu.png
```

So: commit the screenshots, push, and the AnkiWeb page picks them up. A normal
`github.com/.../blob/...` link renders nothing - it has to be the raw URL.
