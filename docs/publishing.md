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

The add-on is already listed on AnkiWeb, so this is an **update**: open
<https://ankiweb.net/shared/addons/>, click the existing
`Context Search (YouTube & Google Images)` entry, and upload the new
`dist\context_search.ankiaddon` on that same page. Do not create a second
listing - existing users only get updates through the original one.

The form is the same either way:

1. Log in to AnkiWeb, open <https://ankiweb.net/shared/addons/>.
2. Click the existing add-on (or **Upload** for a brand new one).
3. Fill in the form:
   - **Title**: `Context Search (YouTube & Google Images)`
   - **Description**: paste the text from `docs/ankiweb-description.md`
     (everything below the `---` line), with `Nikhilsinha666` replaced.
   - **Tags** / keywords: `context menu`, `youtube`, `google images`, `search`,
     `vocabulary`, `images`
   - **Support page**: `https://github.com/Nikhilsinha666/anki-context-search/issues`
   - **Branches**: one branch, `Supports: 2.1.45 to 25.09`. Both boxes must be
     filled - an empty max box is rejected with "invalid version range". Only
     use version numbers Anki has actually released. A plain max does not block
     newer Anki versions; that needs a `-` prefix (`-25.09`). `0` and `0` in
     both boxes is the form default and means "every version".
   - **File**: `dist\context_search.ankiaddon`
4. Submit. AnkiWeb gives the add-on a numeric id, and the install code users
   paste into `Tools > Add-ons > Get Add-ons` is that same id. This add-on is
   **458766448** (<https://ankiweb.net/shared/info/458766448>).
5. The id is also the folder name under `Anki2/addons21` once installed from
   AnkiWeb, which is a quick way to look it up again.

Note: AnkiWeb strips characters like `(`, `)` and `&` from the title, so the
listing shows up as `Context Search YouTube Google Images`, and that stripped
name is what Anki displays in the add-on list. The name inside the add-on
(submenu, config screen, tooltips) keeps the full form.

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

## If the upload fails

**"invalid version range".** A branch has an empty or reversed min/max box.
Fill both, e.g. `2.1.45` to `25.09`.

**"Bad Request" with no explanation.** The form posts to
`/svc/shared/upload-addon` and answers with a bare HTTP 400. Reported several
times on the Anki forums, and the cause each time was the version range in the
form, not the package - see
[this thread](https://forums.ankiweb.net/t/add-on-upload-returns-bad-request-400-even-for-a-minimal-one-file-add-on/70784)
and the [one it links to](https://forums.ankiweb.net/t/i-cant-upload-my-first-addon-my-account-is-not-new/70532).
Fix: put a real released version in the minimum field (`2.1.45`, `2.1.50`,
`25.02`...), leave the maximum empty, and do not invent numbers like `26.99`.
(Content rephrased for compliance with licensing restrictions.)

**"Account is too new".** AnkiWeb blocks add-on uploads from fresh accounts.
Nothing to fix in the package - use an older account or wait.

**"AnkiWeb will not accept the zip".** Almost always a `__pycache__` folder or
the add-on files sitting inside a `context_search/` folder in the archive.
`build.ps1` avoids both; `python tools\check_addon.py` fails loudly if a
`__pycache__` shows up.

## Notes

- Anki caches add-on code, so tell testers to restart Anki after installing.
- Users who copied the folder manually into `addons21` will not see AnkiWeb
  updates. Once the add-on is on AnkiWeb, install it with the id instead.
