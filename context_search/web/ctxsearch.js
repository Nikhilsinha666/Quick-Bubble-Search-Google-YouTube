/* Context Search - floating search icons for the selected text.
 *
 * Injected into the reviewer / previewer webview by __init__.py.
 * Select (or click) a word on the card and a small bubble with one icon per
 * search provider appears next to it. Clicking an icon sends the selection to
 * Python via pycmd, which opens the search in the user's browser.
 *
 * The bubble lives in a shadow root so the note's own CSS cannot restyle it.
 */
(function () {
  "use strict";

  if (window.__ctxSearchLoaded) {
    return;
  }
  window.__ctxSearchLoaded = true;

  var STYLE = [
    ":host { all: initial; position: absolute; z-index: 2147483000; }",
    ".bubble { display: flex; align-items: center; gap: 2px; padding: 3px;",
    "  border-radius: 12px; background: #fff; border: 1px solid rgba(0,0,0,.14);",
    "  box-shadow: 0 6px 18px rgba(0,0,0,.22); }",
    ".bubble.dark { background: #2f2f31; border-color: rgba(255,255,255,.16);",
    "  box-shadow: 0 6px 18px rgba(0,0,0,.55); }",
    "button { display: flex; align-items: center; justify-content: center;",
    "  padding: 0; margin: 0; border: 0; border-radius: 9px; background: transparent;",
    "  cursor: pointer; -webkit-appearance: none; appearance: none; }",
    "button:hover { background: rgba(0,0,0,.09); }",
    ".dark button:hover { background: rgba(255,255,255,.15); }",
    "button:focus-visible { outline: 2px solid #4285f4; outline-offset: 1px; }",
    "svg { display: block; pointer-events: none; width: 68%; height: 68%; }",
    ".letter { font-family: system-ui, sans-serif; font-weight: 600; color: #444;",
    "  pointer-events: none; }",
    ".dark .letter { color: #e0e0e0; }",
  ].join("\n");

  var ICONS = {
    youtube:
      '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">' +
      '<path fill="#ff0000" d="M23 7.6a3 3 0 0 0-2.1-2.1C19 5 12 5 12 5s-7 0-8.9.5A3 3 0 0 0 1 7.6C.5 9.5.5 12 .5 12s0 2.5.5 4.4a3 3 0 0 0 2.1 2.1C5 19 12 19 12 19s7 0 8.9-.5a3 3 0 0 0 2.1-2.1c.5-1.9.5-4.4.5-4.4s0-2.5-.5-4.4z"/>' +
      '<path fill="#ffffff" d="M9.8 15.5v-7l6 3.5z"/></svg>',
    "google-images":
      '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">' +
      '<rect x="3" y="5" width="18" height="14" rx="2.5" fill="none" stroke="#4285f4" stroke-width="2"/>' +
      '<circle cx="8.2" cy="9.8" r="1.7" fill="#fbbc05"/>' +
      '<path fill="#34a853" d="M5 17.2l3.9-4.4 2.7 2.9 2.3-2.5 4.1 4z"/>' +
      '<circle cx="17.4" cy="8.3" r="1.4" fill="#ea4335"/></svg>',
    google:
      '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">' +
      '<circle cx="10.5" cy="10.5" r="6.2" fill="none" stroke="#4285f4" stroke-width="2"/>' +
      '<path stroke="#34a853" stroke-width="2.4" stroke-linecap="round" d="M15.2 15.2 20 20"/></svg>',
    search:
      '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">' +
      '<circle cx="10.5" cy="10.5" r="6.2" fill="none" stroke="currentColor" stroke-width="2"/>' +
      '<path stroke="currentColor" stroke-width="2.4" stroke-linecap="round" d="M15.2 15.2 20 20"/></svg>',
  };

  var WORD_BREAK = /[\s.,;:!?"'`()\[\]{}<>\/\\|~*_=+\u2026\u2014\u2013\u00ab\u00bb\u201c\u201d\u2018\u2019]/;

  var host = null;
  var bubble = null;
  var query = "";
  var config = null;

  function cfg() {
    // read lazily: this file may be evaluated before the inline config script
    if (config === null) {
      var raw = window.__ctxSearchConfig;
      config = raw && typeof raw === "object" ? raw : {};
    }
    return config;
  }

  function searches() {
    var list = cfg().searches;
    return Object.prototype.toString.call(list) === "[object Array]" ? list : [];
  }

  function isDark() {
    var cls = (document.body ? document.body.className : "") + " " + document.documentElement.className;
    if (/night/i.test(String(cls))) {
      return true;
    }
    try {
      return window.matchMedia("(prefers-color-scheme: dark)").matches;
    } catch (err) {
      return false;
    }
  }

  function iconMarkup(entry) {
    var key = String(entry.icon || "").toLowerCase();
    if (ICONS[key]) {
      return ICONS[key];
    }
    var name = String(entry.name || "?");
    var letter = name.charAt(0).toUpperCase() || "?";
    return '<span class="letter" aria-hidden="true">' + letter + "</span>";
  }

  function build() {
    var size = parseInt(cfg().icon_size, 10);
    if (!isFinite(size) || size < 18 || size > 64) {
      size = 30;
    }

    host = document.createElement("div");
    host.id = "ctxsearch-host";
    host.style.cssText = "all: initial; position: absolute; top: 0; left: 0; z-index: 2147483000; display: none;";

    var root = host.attachShadow ? host.attachShadow({ mode: "open" }) : null;
    var parent = root || host;

    if (root) {
      var style = document.createElement("style");
      style.textContent = STYLE;
      root.appendChild(style);
    }

    bubble = document.createElement("div");
    bubble.className = "bubble";
    bubble.setAttribute("role", "toolbar");
    bubble.setAttribute("aria-label", "Context search");

    searches().forEach(function (entry, index) {
      var button = document.createElement("button");
      button.type = "button";
      button.style.width = size + "px";
      button.style.height = size + "px";
      button.title = entry.name || "Search";
      button.setAttribute("aria-label", entry.name || "Search");
      button.innerHTML = iconMarkup(entry);
      button.addEventListener("mousedown", function (event) {
        // keep the selection alive while the button is pressed
        event.preventDefault();
        event.stopPropagation();
      });
      button.addEventListener("click", function (event) {
        event.preventDefault();
        event.stopPropagation();
        run(index);
      });
      bubble.appendChild(button);
    });

    parent.appendChild(bubble);
    document.body.appendChild(host);
  }

  function ensure() {
    if (!host || !host.isConnected) {
      build();
    }
    return host && bubble;
  }

  function hide() {
    if (host) {
      host.style.display = "none";
    }
    query = "";
  }

  function show(rect, text) {
    if (!ensure()) {
      return;
    }
    query = text;
    bubble.className = isDark() ? "bubble dark" : "bubble";
    host.style.display = "block";
    host.style.left = "0px";
    host.style.top = "0px";

    var width = host.offsetWidth;
    var height = host.offsetHeight;
    var viewportWidth = document.documentElement.clientWidth;
    var scrollX = window.pageXOffset || 0;
    var scrollY = window.pageYOffset || 0;

    var left = rect.left + rect.width / 2 - width / 2 + scrollX;
    var top = rect.top - height - 8 + scrollY;
    if (top < scrollY + 2) {
      top = rect.bottom + 8 + scrollY;
    }
    var maxLeft = scrollX + viewportWidth - width - 4;
    if (left > maxLeft) {
      left = maxLeft;
    }
    if (left < scrollX + 4) {
      left = scrollX + 4;
    }

    host.style.left = Math.round(left) + "px";
    host.style.top = Math.round(top) + "px";
  }

  function run(index) {
    var text = query;
    hide();
    if (!text) {
      return;
    }
    var bridge = window.pycmd || window.bridgeCommand;
    if (typeof bridge === "function") {
      bridge("ctxsearch:" + index + ":" + text);
    }
  }

  function isInteractive(node) {
    if (!node || !node.closest) {
      return false;
    }
    return !!node.closest(
      'a, button, input, textarea, select, label, [contenteditable="true"], .replay-button, .replaybutton'
    );
  }

  function caretRange(x, y) {
    if (document.caretRangeFromPoint) {
      return document.caretRangeFromPoint(x, y);
    }
    if (document.caretPositionFromPoint) {
      var position = document.caretPositionFromPoint(x, y);
      if (position && position.offsetNode) {
        var range = document.createRange();
        range.setStart(position.offsetNode, position.offset);
        range.collapse(true);
        return range;
      }
    }
    return null;
  }

  function wordRangeAt(x, y) {
    var range = caretRange(x, y);
    if (!range) {
      return null;
    }
    var node = range.startContainer;
    if (!node || node.nodeType !== 3) {
      return null;
    }
    var text = node.textContent || "";
    var start = range.startOffset;
    var end = range.startOffset;

    function isWordChar(ch) {
      return !!ch && !WORD_BREAK.test(ch);
    }

    if (!isWordChar(text.charAt(start)) && !isWordChar(text.charAt(start - 1))) {
      return null;
    }
    while (start > 0 && isWordChar(text.charAt(start - 1))) {
      start -= 1;
    }
    while (end < text.length && isWordChar(text.charAt(end))) {
      end += 1;
    }
    if (start === end) {
      return null;
    }
    var word = document.createRange();
    word.setStart(node, start);
    word.setEnd(node, end);
    return word;
  }

  function selectionRect(selection) {
    if (!selection || !selection.rangeCount) {
      return null;
    }
    var rect = selection.getRangeAt(0).getBoundingClientRect();
    if (!rect || (!rect.width && !rect.height)) {
      return null;
    }
    return rect;
  }

  function onMouseUp(event) {
    if (event.button !== 0 || !searches().length) {
      return;
    }
    if (host && (event.target === host || (host.contains && host.contains(event.target)))) {
      return;
    }
    if (isInteractive(event.target)) {
      hide();
      return;
    }

    var x = event.clientX;
    var y = event.clientY;

    // let the browser finish updating the selection first
    setTimeout(function () {
      var selection = window.getSelection();
      var text = selection ? String(selection.toString()) : "";

      if (!text.trim() && cfg().trigger !== "selection") {
        var word = wordRangeAt(x, y);
        if (word && selection) {
          selection.removeAllRanges();
          selection.addRange(word);
          text = word.toString();
        }
      }

      text = text.replace(/\s+/g, " ").trim();
      if (!text) {
        hide();
        return;
      }

      var limit = parseInt(cfg().max_query_chars, 10);
      if (isFinite(limit) && limit > 0 && text.length > limit) {
        text = text.slice(0, limit);
      }

      var rect = selectionRect(selection);
      if (!rect) {
        hide();
        return;
      }
      show(rect, text);
    }, 0);
  }

  function onMouseDown(event) {
    if (host && host.contains && host.contains(event.target)) {
      return;
    }
    hide();
  }

  document.addEventListener("mouseup", onMouseUp, true);
  document.addEventListener("mousedown", onMouseDown, true);
  document.addEventListener(
    "keydown",
    function (event) {
      if (event.key === "Escape") {
        hide();
      }
    },
    true
  );
  window.addEventListener("scroll", hide, true);
  window.addEventListener("resize", hide);

  window.__ctxSearch = { hide: hide };
})();
