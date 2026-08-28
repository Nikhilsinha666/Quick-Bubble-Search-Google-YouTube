"""Sanity checks for the add-on package.

Runs without Anki installed (no `aqt` import), so it works in CI:

* every .py file parses
* config.json and manifest.json are valid JSON
* config.json is identical to DEFAULT_CONFIG inside __init__.py
* every enabled search has a usable URL template
* no __pycache__ folders are lying around (AnkiWeb rejects those)

Usage:  python tools/check_addon.py
"""

from __future__ import annotations

import ast
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ADDON = ROOT / "context_search"

problems: list[str] = []


def fail(msg: str) -> None:
    problems.append(msg)
    print(f"[FAIL] {msg}")


def ok(msg: str) -> None:
    print(f"[ok]   {msg}")


def module_constant(name: str):
    """Read a top-level literal from __init__.py without importing aqt."""
    source = (ADDON / "__init__.py").read_text(encoding="utf-8")
    tree = ast.parse(source, "__init__.py")
    for node in tree.body:
        if not isinstance(node, (ast.Assign, ast.AnnAssign)):
            continue
        targets = node.targets if isinstance(node, ast.Assign) else [node.target]
        for target in targets:
            if isinstance(target, ast.Name) and target.id == name:
                if node.value is None:
                    return None
                return ast.literal_eval(node.value)
    return None


def load_default_config() -> dict | None:
    return module_constant("DEFAULT_CONFIG")


def main() -> int:
    if not ADDON.is_dir():
        fail(f"add-on folder not found: {ADDON}")
        return 1

    for path in sorted(ADDON.rglob("*.py")):
        try:
            ast.parse(path.read_text(encoding="utf-8"), str(path))
        except SyntaxError as exc:
            fail(f"syntax error in {path.name}: {exc}")
        else:
            ok(f"{path.relative_to(ROOT)} parses")

    caches = [p for p in ADDON.rglob("__pycache__") if p.is_dir()]
    if caches:
        fail("__pycache__ folder(s) present, AnkiWeb rejects them: " + ", ".join(str(p) for p in caches))
    else:
        ok("no __pycache__ folders")

    config: dict | None = None
    manifest: dict | None = None
    for name in ("config.json", "manifest.json"):
        path = ADDON / name
        if not path.is_file():
            fail(f"missing {name}")
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            fail(f"{name} is not valid JSON: {exc}")
            continue
        ok(f"{name} is valid JSON")
        if name == "config.json":
            config = data
        else:
            manifest = data
            for key in ("package", "name"):
                if not data.get(key):
                    fail(f"manifest.json is missing '{key}'")
            if data.get("package") != ADDON.name:
                fail(f"manifest package '{data.get('package')}' != folder '{ADDON.name}'")

    if not (ADDON / "config.md").is_file():
        fail("missing config.md (shown in Anki's config screen)")
    else:
        ok("config.md present")

    # the add-on should call itself the same thing everywhere the user can see
    addon_name = module_constant("ADDON_NAME")
    if not addon_name:
        fail("could not find ADDON_NAME in __init__.py")
    else:
        manifest_name = (manifest or {}).get("name")
        if manifest_name != addon_name:
            fail(f"manifest name {manifest_name!r} != ADDON_NAME {addon_name!r}")
        else:
            ok(f"name consistent: {addon_name!r}")

        submenu = (config or {}).get("submenu_label")
        if submenu != addon_name:
            fail(f"config.json submenu_label {submenu!r} != ADDON_NAME {addon_name!r}")
        else:
            ok("config.json submenu_label matches the add-on name")

        js = ADDON / "web" / "ctxsearch.js"
        if js.is_file() and addon_name not in js.read_text(encoding="utf-8"):
            fail(f"{js.name} does not mention the add-on name")
        elif js.is_file():
            ok("ctxsearch.js mentions the add-on name")

        heading = (ADDON / "config.md").read_text(encoding="utf-8").splitlines()[0]
        if addon_name not in heading:
            fail(f"config.md heading {heading!r} does not use the add-on name")
        else:
            ok("config.md heading uses the add-on name")

    defaults = load_default_config()
    if defaults is None:
        fail("could not find DEFAULT_CONFIG in __init__.py")
    elif config is not None:
        if config == defaults:
            ok("config.json matches DEFAULT_CONFIG")
        else:
            only_json = sorted(set(config) - set(defaults))
            only_code = sorted(set(defaults) - set(config))
            detail = []
            if only_json:
                detail.append(f"only in config.json: {only_json}")
            if only_code:
                detail.append(f"only in DEFAULT_CONFIG: {only_code}")
            differing = sorted(
                k for k in set(config) & set(defaults) if config[k] != defaults[k]
            )
            if differing:
                detail.append(f"different values: {differing}")
            fail("config.json and DEFAULT_CONFIG are out of sync (" + "; ".join(detail) + ")")

    if isinstance(config, dict):
        searches = config.get("searches")
        if not isinstance(searches, list) or not searches:
            fail("config.json has no searches")
        else:
            enabled = 0
            for i, entry in enumerate(searches):
                if not isinstance(entry, dict):
                    fail(f"searches[{i}] is not an object")
                    continue
                url = str(entry.get("url") or "")
                if not url.startswith("https://"):
                    fail(f"searches[{i}] url should start with https:// ({url!r})")
                if entry.get("enabled"):
                    enabled += 1
            if enabled == 0:
                fail("no search is enabled by default")
            else:
                ok(f"{enabled} search(es) enabled by default")

    print()
    if problems:
        print(f"{len(problems)} problem(s) found")
        return 1
    print("all checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
