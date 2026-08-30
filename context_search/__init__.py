"""Quick Bubble Search (Google & YouTube) - Anki add-on.

Double-click a word on a card and a small bubble with one icon per search
provider appears next to it - click an icon to search that word on Google,
Google Images or YouTube. The same searches are also available from the
right-click menu, including inside the note editor. Providers are configurable.

Hooks used:
    gui_hooks.webview_will_set_content          -> inject the popup JS/config
    gui_hooks.webview_did_receive_js_message    -> handle icon clicks from JS
    gui_hooks.webview_will_show_context_menu    -> reviewer / previewer / editor
    gui_hooks.editor_will_show_context_menu     -> Add + Browse note editor
    gui_hooks.reviewer_will_show_context_menu   -> reviewer "More" menu ("m" key)
"""

from __future__ import annotations

import copy
import json
import os
import re
from typing import Any, Callable

from urllib.parse import quote, quote_plus

from aqt import gui_hooks, mw
from aqt.qt import QMenu

try:
    from aqt.qt import qconnect
except ImportError:  # pragma: no cover - very old Anki builds

    def qconnect(signal: Any, func: Callable) -> None:  # type: ignore[misc]
        signal.connect(func)


try:
    from aqt.utils import openLink, tooltip
except ImportError:  # pragma: no cover - very old Anki builds
    import webbrowser

    def openLink(url: str) -> None:  # type: ignore[misc]
        webbrowser.open(url)

    def tooltip(msg: str, period: int = 3000) -> None:  # type: ignore[misc]
        print(msg)


# the add-on's name, used for the submenu, tooltips and the popup's aria-label.
# Keep it identical to "name" in manifest.json.
# The package folder stays "context_search": Anki keys add-ons by folder name,
# so renaming it would look like a different add-on and orphan saved configs.
ADDON_NAME = "Quick Bubble Search (Google & YouTube)"

# names used before the add-on was renamed. `submenu_label` is a saved setting,
# so a profile from an older version still holds the old name; it is replaced
# with the current one unless the user picked a label of their own.
LEGACY_NAMES = ("Context Search (YouTube & Google Images)",)

# ---------------------------------------------------------------------------
# defaults (kept in sync with config.json, used as a fallback + validator)
#
# Plain literals only: tools/check_addon.py reads this dict with
# ast.literal_eval to prove it matches config.json.
# ---------------------------------------------------------------------------

DEFAULT_CONFIG: dict[str, Any] = {
    "popup_enabled": True,
    "popup_select_on_click": False,
    "popup_icon_size": 30,
    "use_submenu": True,
    "submenu_label": "Quick Bubble Search (Google & YouTube)",
    "enable_in_reviewer": True,
    "enable_in_editor": True,
    "enable_in_more_menu": True,
    "show_selection_in_label": True,
    "max_label_length": 32,
    "max_query_chars": 200,
    "strip_cloze_markers": True,
    "strip_sound_tags": True,
    "strip_surrounding_punctuation": True,
    "searches": [
        {
            "name": "YouTube",
            "url": "https://www.youtube.com/results?search_query={query}",
            "icon": "youtube",
            "enabled": True,
        },
        {
            "name": "Google Images",
            "url": "https://www.google.com/search?tbm=isch&q={query}",
            "icon": "google-images",
            "enabled": True,
        },
        {
            "name": "Google",
            "url": "https://www.google.com/search?q={query}",
            "icon": "google",
            "enabled": True,
        },
        {
            "name": "Google Definition",
            "url": "https://www.google.com/search?q=define+{query}",
            "icon": "search",
            "enabled": False,
        },
        {
            "name": "Forvo (pronunciation)",
            "url": "https://forvo.com/word/{query_path}/",
            "icon": "",
            "enabled": False,
        },
        {
            "name": "YouGlish (word in real videos)",
            "url": "https://youglish.com/pronounce/{query_path}/english",
            "icon": "",
            "enabled": False,
        },
    ],
}

_CLOZE_RE = re.compile(r"\{\{c\d+::(.*?)(?:::.*?)?\}\}", re.DOTALL)
_SOUND_RE = re.compile(r"\[sound:[^\]]*\]")
_WHITESPACE_RE = re.compile(r"\s+")
_TRIM_CHARS = " \t\r\n\"'`*_~^\u2026,;:.!?\u00bf\u00a1()[]{}<>\u00ab\u00bb\u201e\u201c\u201d\u2018\u2019-\u2013\u2014/\\|"

# marker so the same QMenu never gets our items twice
_MENU_MARK = "_context_search_added"


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------


def _as_int(value: Any, fallback: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return fallback


def normalize_search(raw: Any) -> dict[str, Any] | None:
    """Clean up one entry of the searches list, or None if it is unusable."""
    if not isinstance(raw, dict):
        return None
    url = str(raw.get("url") or "").strip()
    if not url:
        return None
    return {
        "name": str(raw.get("name") or "").strip() or "Search",
        "url": url,
        # not lowercased: an icon may be a file name or an emoji
        "icon": str(raw.get("icon") or "").strip(),
        "enabled": bool(raw.get("enabled", True)),
    }


def get_raw_config() -> dict[str, Any]:
    """User config merged onto the defaults, including disabled searches.

    This is what the settings dialog edits.
    """
    cfg = copy.deepcopy(DEFAULT_CONFIG)

    user: Any = None
    if mw is not None:
        try:
            user = mw.addonManager.getConfig(__name__)
        except Exception:
            user = None

    if isinstance(user, dict):
        for key, value in user.items():
            if key in cfg:
                cfg[key] = value

    if str(cfg.get("submenu_label") or "").strip() in LEGACY_NAMES:
        cfg["submenu_label"] = ADDON_NAME

    searches: list[dict[str, Any]] = []
    raw_searches = cfg.get("searches")
    if isinstance(raw_searches, list):
        for raw in raw_searches:
            entry = normalize_search(raw)
            if entry is not None:
                searches.append(entry)
    cfg["searches"] = searches

    return cfg


def get_config() -> dict[str, Any]:
    """Runtime config: `searches` holds only the enabled ones, in order."""
    cfg = get_raw_config()
    cfg["searches"] = [
        {"name": entry["name"], "url": entry["url"], "icon": entry["icon"]}
        for entry in cfg["searches"]
        if entry["enabled"]
    ]
    return cfg


def save_config(cfg: dict[str, Any]) -> None:
    if mw is None:
        return
    try:
        mw.addonManager.writeConfig(__name__, cfg)
    except Exception:
        pass


def refresh_webviews() -> None:
    """Tell any open card webview to re-read the config and rebuild the icons."""
    if mw is None:
        return
    js = "if (window.__ctxSearch && window.__ctxSearch.refresh) { window.__ctxSearch.refresh(); }"
    seen: list[Any] = []
    for web in (getattr(mw, "web", None), getattr(getattr(mw, "reviewer", None), "web", None)):
        if web is None or any(web is other for other in seen):
            continue
        seen.append(web)
        try:
            web.eval(js)
        except Exception:
            pass


def clean_selection(text: str, cfg: dict[str, Any]) -> str:
    """Turn a raw webview selection into a usable search query."""
    if not text:
        return ""

    text = text.replace("\u00a0", " ").replace("\u200b", "")

    if cfg.get("strip_cloze_markers", True):
        text = _CLOZE_RE.sub(r"\1", text)
    if cfg.get("strip_sound_tags", True):
        text = _SOUND_RE.sub(" ", text)

    text = _WHITESPACE_RE.sub(" ", text).strip()

    if cfg.get("strip_surrounding_punctuation", True):
        text = text.strip(_TRIM_CHARS)

    limit = _as_int(cfg.get("max_query_chars"), 200)
    if limit > 0 and len(text) > limit:
        text = text[:limit].rstrip()

    return text


def selected_text(webview: Any) -> str:
    """Read the current selection from an AnkiWebView (or its page)."""
    candidates: list[Any] = [webview]
    try:
        page = webview.page()
        if page is not None:
            candidates.append(page)
    except Exception:
        pass

    for obj in candidates:
        try:
            text = obj.selectedText()
        except Exception:
            continue
        if text:
            return str(text)
    return ""


def build_url(template: str, query: str) -> str:
    """Fill a URL template with the query.

    Supported placeholders:
        {query}      / {}   url-encoded for a query string (spaces -> '+')
        {query_path}        percent-encoded for a path segment (spaces -> %20)
        {query_raw}         inserted as-is, no encoding

    A template without any placeholder simply gets the encoded query appended.
    """
    plus = quote_plus(query)
    if "{query" in template or "{}" in template:
        return (
            template.replace("{query_raw}", query)
            .replace("{query_path}", quote(query, safe=""))
            .replace("{query_plus}", plus)
            .replace("{query}", plus)
            .replace("{}", plus)
        )
    return template + plus


def run_search(name: str, template: str, query: str) -> None:
    url = build_url(template, query)
    try:
        openLink(url)
    except Exception as exc:  # pragma: no cover - depends on desktop env
        tooltip(f"{ADDON_NAME}: could not open {name} ({exc})")


def _escape_amp(text: str) -> str:
    """'&' in a Qt menu label means 'mnemonic', so double it up."""
    return text.replace("&", "&&")


def _action_label(name: str, query: str, cfg: dict[str, Any]) -> str:
    if not cfg.get("show_selection_in_label", True):
        return name

    limit = _as_int(cfg.get("max_label_length"), 32)
    preview = query
    if limit > 0 and len(preview) > limit:
        preview = preview[: max(1, limit - 1)].rstrip() + "\u2026"
    return f'{name}: "{preview}"'


def _is_editor_webview(webview: Any) -> bool:
    for cls in type(webview).__mro__:
        if "EditorWebView" in cls.__name__:
            return True
    return False


def add_menu_items(menu: QMenu, query: str, cfg: dict[str, Any]) -> None:
    searches = cfg.get("searches") or []
    if not searches:
        return

    target: Any = menu
    if cfg.get("use_submenu", True):
        label = str(cfg.get("submenu_label") or ADDON_NAME)
        submenu = menu.addMenu(_escape_amp(label))
        if submenu is None:
            return
        target = submenu
    elif menu.actions():
        menu.addSeparator()

    for entry in searches:
        name = entry["name"]
        template = entry["url"]
        action = target.addAction(_escape_amp(_action_label(name, query, cfg)))
        if action is None:
            continue
        qconnect(
            action.triggered,
            lambda _checked=False, n=name, t=template, q=query: run_search(n, t, q),
        )


def _decorate_menu(menu: QMenu, webview: Any, config_key: str) -> None:
    if menu is None or webview is None:
        return

    cfg = get_config()
    if not cfg.get(config_key, True):
        return

    if getattr(menu, _MENU_MARK, False):
        return

    query = clean_selection(selected_text(webview), cfg)
    if not query:
        return

    try:
        setattr(menu, _MENU_MARK, True)
    except Exception:
        pass

    add_menu_items(menu, query, cfg)


# ---------------------------------------------------------------------------
# floating icon popup (injected into the card webview)
# ---------------------------------------------------------------------------

# webviews that show a card, and therefore get the popup
_POPUP_CONTEXTS = {
    "Reviewer",
    "Previewer",
    "MultiCardPreviewer",
    "SingleCardPreviewer",
    "BrowserPreviewer",
    "CardLayout",
}
_JS_PREFIX = "ctxsearch:"


_ICON_SUFFIXES = "png|jpg|jpeg|gif|webp|svg"


def _register_web_exports() -> None:
    if mw is None:
        return
    try:
        mw.addonManager.setWebExports(
            __name__, rf"(web|user_files)/.*\.(css|js|{_ICON_SUFFIXES})"
        )
    except Exception:
        pass


def user_icons_dir() -> str:
    """Folder for icons the user adds. user_files survives add-on updates."""
    return os.path.join(os.path.dirname(__file__), "user_files", "icons")


def _addon_url() -> str:
    """URL Anki serves this add-on's folder from.

    The package is the add-on folder name: "context_search" when installed from
    source, a numeric id when installed from AnkiWeb. addonFromModule() is the
    official way to get it; __name__ is the same value and works as a fallback.
    """
    package = __name__.split(".")[0]
    if mw is not None:
        try:
            package = mw.addonManager.addonFromModule(__name__) or package
        except Exception:
            pass
    return f"/_addons/{package}"


def _web_folder_url() -> str:
    return f"{_addon_url()}/web"


def _user_icons_url() -> str:
    return f"{_addon_url()}/user_files/icons"


def _is_popup_context(context: Any) -> bool:
    try:
        names = {cls.__name__ for cls in type(context).__mro__}
    except Exception:
        return False
    return bool(names & _POPUP_CONTEXTS)


def _popup_payload(cfg: dict[str, Any]) -> dict[str, Any]:
    return {
        # off by default: only a double click or a drag selects a word, so a
        # click on blank space cannot pop the icons up
        "select_on_click": bool(cfg.get("popup_select_on_click", False)),
        "icon_size": _as_int(cfg.get("popup_icon_size"), 30),
        "max_query_chars": _as_int(cfg.get("max_query_chars"), 200),
        "icon_base": _user_icons_url(),
        "searches": [
            {"name": entry["name"], "icon": entry.get("icon", "")}
            for entry in cfg.get("searches") or []
        ],
    }


def on_webview_will_set_content(web_content: Any, context: Any) -> None:
    cfg = get_config()
    if not cfg.get("popup_enabled", True):
        return
    if not cfg.get("searches"):
        return
    if not _is_popup_context(context):
        return

    base = _web_folder_url()
    if not base:
        return

    payload = json.dumps(_popup_payload(cfg))
    web_content.head += f"<script>window.__ctxSearchConfig = {payload};</script>"
    web_content.js.append(f"{base}/ctxsearch.js")


def on_js_message(
    handled: tuple[bool, Any], message: str, context: Any
) -> tuple[bool, Any]:
    # Someone already dealt with this message. That happens when the add-on is
    # installed twice (say a copied folder next to the AnkiWeb install) - without
    # this check one icon click would open two browser tabs.
    try:
        if handled[0]:
            return handled
    except (TypeError, IndexError):
        pass

    if not isinstance(message, str) or not message.startswith(_JS_PREFIX):
        return handled

    body = message[len(_JS_PREFIX) :]

    # the popup asks for a fresh config after the settings are saved
    if body == "config":
        return (True, _popup_payload(get_config()))

    parts = body.split(":", 1)
    if len(parts) != 2:
        return (True, None)

    cfg = get_config()
    searches = cfg.get("searches") or []
    try:
        index = int(parts[0])
    except (TypeError, ValueError):
        return (True, None)
    if not 0 <= index < len(searches):
        return (True, None)

    query = clean_selection(parts[1], cfg)
    if not query:
        tooltip(f"{ADDON_NAME}: nothing to search")
        return (True, None)

    entry = searches[index]
    run_search(entry["name"], entry["url"], query)
    return (True, None)


# ---------------------------------------------------------------------------
# hook handlers
# ---------------------------------------------------------------------------


def on_webview_will_show_context_menu(webview: Any, menu: QMenu) -> None:
    key = "enable_in_editor" if _is_editor_webview(webview) else "enable_in_reviewer"
    _decorate_menu(menu, webview, key)


def on_editor_will_show_context_menu(editor_webview: Any, menu: QMenu) -> None:
    _decorate_menu(menu, editor_webview, "enable_in_editor")


def on_reviewer_will_show_context_menu(reviewer: Any, menu: QMenu) -> None:
    _decorate_menu(menu, getattr(reviewer, "web", None), "enable_in_more_menu")


def register_hooks() -> None:
    handlers = (
        ("webview_will_set_content", on_webview_will_set_content),
        ("webview_did_receive_js_message", on_js_message),
        ("webview_will_show_context_menu", on_webview_will_show_context_menu),
        ("editor_will_show_context_menu", on_editor_will_show_context_menu),
        ("reviewer_will_show_context_menu", on_reviewer_will_show_context_menu),
    )
    for hook_name, handler in handlers:
        hook = getattr(gui_hooks, hook_name, None)
        if hook is None:
            continue
        try:
            hook.append(handler)
        except Exception:
            pass


def register_settings() -> None:
    """Hook up the settings dialog: gear > Config, and the Tools menu."""
    if mw is None:
        return
    try:
        from . import settings
    except Exception as exc:  # pragma: no cover - keeps the add-on usable
        print(f"{ADDON_NAME}: settings dialog unavailable ({exc})")
        return
    try:
        mw.addonManager.setConfigAction(__name__, settings.open_settings)
    except Exception:
        pass
    settings.add_tools_menu_action()


_register_web_exports()
register_hooks()
register_settings()
