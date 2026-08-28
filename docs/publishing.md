# Publishing to AnkiWeb

## 1. Build the package

```powershell
.\build.ps1
```

That produces `dist\context_search.ankiaddon`. The script already does the two
things AnkiWeb is picky about: the add-on files sit at the root of the archive
(no `context_search/` folder inside), and no `__pycache__` is included.

Verify anytime with:

```powershell
python tools\check_addon.py
```

## 2. Upload

1. Log in to AnkiWeb, open <https://ankiweb.net/shared/addons/>.
2. Click **Upload**.
3. Fill in the form:
   - **Title**: `Context Search (YouTube & Google Images)`
   - **Description**: paste the text from `docs/ankiweb-description.md`
     (everything below the `---` line), with `Nikhilsinha666` replaced.
   - **Tags** / keywords: `context menu`, `youtube`, `google images`, `search`,
     `vocabulary`, `images`
   - **Supported Anki versions**: 2.1.45 and up.
   - **File**: `dist\context_search.ankiaddon`
4. Submit. AnkiWeb gives the add-on a numeric id, and the install code users
   paste into `Tools > Add-ons > Get Add-ons` is that same id.
5. Put the id in `README.md` where it says `<ANKIWEB-ID>`.

## 3. Images on the add-on page

AnkiWeb has no image hosting and no image upload. Screenshots live in this
repo, and the description links to their **raw** URLs:

```html
<img src="https://raw.githubusercontent.com/Nikhilsinha666/anki-context-search/main/screenshots/01-context-menu.png">
```

- A `https://github.com/USER/REPO/blob/main/file.png` link renders nothing -
  it has to be `raw.githubusercontent.com`.
- Attributes such as `width`, `height` and `alt` are stripped, so size the
  images before committing them.
- Pushing a new screenshot with the same filename updates the AnkiWeb page too,
  since the page just links to the file. Browsers may cache it for a while.

See `screenshots/README.md` for what to capture.

## 4. Shipping an update

1. Make the change.
2. Bump `human_version` in `context_search/manifest.json` and add a
   `CHANGELOG.md` entry.
3. `python tools\check_addon.py` then `.\build.ps1`.
4. On <https://ankiweb.net/shared/addons/>, open your add-on and upload the new
   `.ankiaddon`. Keep the same page - do not create a second listing, otherwise
   existing users will not get the update.
5. Tag the release so GitHub attaches the built file automatically:

```powershell
git tag v1.0.1
git push origin v1.0.1
```

The `build` workflow validates the package on every push and, for `v*` tags,
creates a GitHub release with the `.ankiaddon` attached.

## Notes

- Anki caches add-on code, so tell testers to restart Anki after installing.
- Users who copied the folder manually into `addons21` will not see AnkiWeb
  updates. Once the add-on is on AnkiWeb, install it with the id instead.
