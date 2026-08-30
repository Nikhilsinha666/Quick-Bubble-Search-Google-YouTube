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

Double-click a word on a card and a small bubble with **Google**, **Google Images** and **YouTube** icons appears right next to it. One click opens the search in your browser.

Handy when a card needs a picture or a real-world example: double-click the word, click the icon, done. Any other website can be added in the settings, with its own icon.

<img src="https://raw.githubusercontent.com/Nikhilsinha666/Quick-Bubble-Search-Google-YouTube/main/screenshots/01-context-menu.png">

### How to use

1. Double-click any word on the card - it gets selected and the icons appear above it.
2. Click the icon you want.

Dragging across a whole phrase works too. A single click on empty space selects nothing, so the icons never appear by accident. `Esc`, scrolling, or clicking somewhere else makes them go away.

Prefer the old way? The same searches are also in the **right-click** menu, under **Quick Bubble Search (Google & YouTube)**.

### Where it works

- the floating icons: while reviewing (question and answer side), in the card previewer and in the card layout screen
- the right-click menu: everywhere above, plus the note editor (**Add** and **Browse**) and the reviewer **More** menu (`m` key)

Nothing shows up until there is actually a selection, so it stays out of your way while you study. Both the icons and the menu can be switched off separately in the config.

### The selection is cleaned up first

- `{{c1::word}}` is searched as `word`
- `[sound:...]` tags are removed
- multi-line selections become a single line
- quotes, brackets and commas around the selection are trimmed

### Settings

`Tools > Quick Bubble Search (Google & YouTube)...`, or the **Config** button next to the add-on in `Tools > Add-ons`.

**Add any website you like.** Give it a name, paste the search URL with `{query}` where the word belongs, pick an icon, and hit **Test** to try it once before saving:

```
https://en.wikipedia.org/w/index.php?search={query}
```

For icons you can use a built-in logo (YouTube, Google, Google Images, magnifying glass), a letter or emoji badge, or your own image file. Searches can be ticked, reordered and removed from the list.

You can also turn the floating icons off, let a single click select a word as well (off by default, so only a double-click or a drag selects), change the icon size, control the right-click menu per screen, and adjust how the selected text is cleaned up.

Google definitions, Forvo and YouGlish are already written in - just tick them.

### Notes

- Nothing is sent anywhere. The add-on only opens a search URL in your browser.
- Works with Anki 2.1.45 and newer (tested on 25.09).

Source code, bug reports and feature requests:
<https://github.com/Nikhilsinha666/Quick-Bubble-Search-Google-YouTube>
