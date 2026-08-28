"""Settings dialog for Context Search (YouTube & Google Images).

Opened from `Tools > Context Search (YouTube & Google Images)...` and from the
gear menu next to the add-on in `Tools > Add-ons`, so users never have to touch
the raw JSON config.
"""

from __future__ import annotations

import copy
import os
import re
import shutil
from typing import Any

from aqt import mw

# Anki's own convention: the wildcard keeps this working across the Qt5 and Qt6
# builds without listing three dozen widget names.
from aqt.qt import *  # noqa: F401,F403

from aqt.utils import askUser, showWarning, tooltip

from . import (
    ADDON_NAME,
    DEFAULT_CONFIG,
    get_raw_config,
    refresh_webviews,
    run_search,
    save_config,
    user_icons_dir,
)

# built-in icons drawn by web/ctxsearch.js
ICON_CHOICES: list[tuple[str, str]] = [
    ("youtube", "YouTube"),
    ("google", "Google"),
    ("google-images", "Google Images"),
    ("search", "Magnifying glass"),
]

LETTER_CHOICE = "\x00letter"
FILE_CHOICE = "\x00file"

SAMPLE_WORD = "photosynthesis"


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------


def copy_icon_file(path: str) -> str:
    """Copy a chosen image into user_files/icons and return its file name."""
    folder = user_icons_dir()
    os.makedirs(folder, exist_ok=True)

    name = re.sub(r"[^A-Za-z0-9._-]", "_", os.path.basename(path)) or "icon.png"
    stem, ext = os.path.splitext(name)
    target = os.path.join(folder, name)
    counter = 1
    while os.path.exists(target):
        name = f"{stem}-{counter}{ext}"
        target = os.path.join(folder, name)
        counter += 1

    shutil.copyfile(path, target)
    return name


def describe_icon(icon: str, name: str) -> str:
    """Short human description of an icon value, for the table."""
    icon = str(icon or "")
    key = icon.lower()
    for choice, label in ICON_CHOICES:
        if key == choice:
            return label
    if key.startswith("file:"):
        return f"Image: {icon[5:]}"
    text = icon[5:] if key.startswith("text:") else icon
    if text:
        return f"Letter: {text}"
    first = (name or "?")[:1].upper()
    return f"Letter: {first}"


# ---------------------------------------------------------------------------
# one search provider
# ---------------------------------------------------------------------------


class ProviderDialog(QDialog):
    def __init__(self, parent: QWidget, entry: dict[str, Any] | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Add a search" if entry is None else "Edit search")
        self.setMinimumWidth(560)
        self._entry: dict[str, Any] = dict(entry) if entry else {
            "name": "",
            "url": "",
            "icon": "",
            "enabled": True,
        }
        self._icon_file = ""
        self._build_ui()
        self._load()

    # -- ui ----------------------------------------------------------------

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        form = QFormLayout()
        form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)

        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Wikipedia")
        form.addRow("Name", self.name_edit)

        self.url_edit = QLineEdit()
        self.url_edit.setPlaceholderText(
            "https://en.wikipedia.org/w/index.php?search={query}"
        )
        url_row = QHBoxLayout()
        url_row.addWidget(self.url_edit, 1)
        insert_button = QPushButton("Insert {query}")
        qconnect(insert_button.clicked, self._insert_placeholder)
        url_row.addWidget(insert_button)
        form.addRow("Search URL", url_row)

        hint = QLabel(
            "Put <b>{query}</b> where the selected word belongs. Use "
            "<b>{query_path}</b> when the word sits in the path instead of a "
            "query string, for example "
            "<code>https://forvo.com/word/{query_path}/</code>. With no "
            "placeholder at all, the word is added to the end of the URL."
        )
        hint.setWordWrap(True)
        form.addRow("", hint)

        self.icon_combo = QComboBox()
        for key, label in ICON_CHOICES:
            self.icon_combo.addItem(label, key)
        self.icon_combo.addItem("Letter or emoji...", LETTER_CHOICE)
        self.icon_combo.addItem("Image file...", FILE_CHOICE)
        qconnect(self.icon_combo.currentIndexChanged, self._icon_changed)
        form.addRow("Icon", self.icon_combo)

        self.letter_box = QWidget()
        letter_layout = QHBoxLayout(self.letter_box)
        letter_layout.setContentsMargins(0, 0, 0, 0)
        self.letter_edit = QLineEdit()
        self.letter_edit.setMaxLength(2)
        self.letter_edit.setFixedWidth(60)
        self.letter_edit.setPlaceholderText("W")
        letter_layout.addWidget(QLabel("Letter or emoji"))
        letter_layout.addWidget(self.letter_edit)
        letter_layout.addStretch(1)
        form.addRow("", self.letter_box)

        self.file_box = QWidget()
        file_layout = QHBoxLayout(self.file_box)
        file_layout.setContentsMargins(0, 0, 0, 0)
        choose_button = QPushButton("Choose image...")
        qconnect(choose_button.clicked, self._choose_file)
        self.file_label = QLabel("No image chosen")
        file_layout.addWidget(choose_button)
        file_layout.addWidget(self.file_label, 1)
        form.addRow("", self.file_box)

        layout.addLayout(form)

        self.enabled_cb = QCheckBox("Show this search")
        layout.addWidget(self.enabled_cb)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        test_button = buttons.addButton("Test", QDialogButtonBox.ButtonRole.ActionRole)
        qconnect(test_button.clicked, self._test)
        qconnect(buttons.accepted, self.accept)
        qconnect(buttons.rejected, self.reject)
        layout.addWidget(buttons)

    def _load(self) -> None:
        self.name_edit.setText(str(self._entry.get("name") or ""))
        self.url_edit.setText(str(self._entry.get("url") or ""))
        self.enabled_cb.setChecked(bool(self._entry.get("enabled", True)))

        icon = str(self._entry.get("icon") or "")
        key = icon.lower()
        index = self.icon_combo.findData(key)
        if index >= 0:
            self.icon_combo.setCurrentIndex(index)
        elif key.startswith("file:"):
            self._icon_file = icon[5:]
            self.icon_combo.setCurrentIndex(self.icon_combo.findData(FILE_CHOICE))
        else:
            self.letter_edit.setText(icon[5:] if key.startswith("text:") else icon)
            self.icon_combo.setCurrentIndex(self.icon_combo.findData(LETTER_CHOICE))
        self._icon_changed()

    # -- slots -------------------------------------------------------------

    def _icon_changed(self, *_: Any) -> None:
        data = self.icon_combo.currentData()
        self.letter_box.setVisible(data == LETTER_CHOICE)
        self.file_box.setVisible(data == FILE_CHOICE)
        self.file_label.setText(self._icon_file or "No image chosen")

    def _insert_placeholder(self, *_: Any) -> None:
        self.url_edit.insert("{query}")
        self.url_edit.setFocus()

    def _choose_file(self, *_: Any) -> None:
        path, _filter = QFileDialog.getOpenFileName(
            self,
            "Choose an icon image",
            "",
            "Images (*.png *.jpg *.jpeg *.gif *.webp *.svg)",
        )
        if not path:
            return
        try:
            self._icon_file = copy_icon_file(path)
        except Exception as exc:
            showWarning(f"Could not use that image:\n{exc}", parent=self)
            return
        self.file_label.setText(self._icon_file)

    def _test(self, *_: Any) -> None:
        url = self.url_edit.text().strip()
        if not re.match(r"^https?://", url, re.IGNORECASE):
            showWarning(
                "Enter a search URL first, starting with https://", parent=self
            )
            return
        run_search(self.name_edit.text().strip() or "Search", url, SAMPLE_WORD)

    # -- result ------------------------------------------------------------

    def icon_value(self) -> str:
        data = self.icon_combo.currentData()
        if data == LETTER_CHOICE:
            text = self.letter_edit.text().strip()
            return f"text:{text}" if text else ""
        if data == FILE_CHOICE:
            return f"file:{self._icon_file}" if self._icon_file else ""
        return str(data or "")

    def accept(self) -> None:
        name = self.name_edit.text().strip()
        url = self.url_edit.text().strip()
        if not name:
            showWarning("Give the search a name.", parent=self)
            return
        if not re.match(r"^https?://", url, re.IGNORECASE):
            showWarning(
                "The search URL has to start with https:// or http://", parent=self
            )
            return
        if self.icon_combo.currentData() == FILE_CHOICE and not self._icon_file:
            showWarning("Choose an image, or pick a different icon.", parent=self)
            return

        self._entry = {
            "name": name,
            "url": url,
            "icon": self.icon_value(),
            "enabled": self.enabled_cb.isChecked(),
        }
        super().accept()

    def entry(self) -> dict[str, Any]:
        return dict(self._entry)


# ---------------------------------------------------------------------------
# main settings dialog
# ---------------------------------------------------------------------------


class SettingsDialog(QDialog):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent or mw)
        self.setWindowTitle(ADDON_NAME)
        self.setMinimumSize(700, 560)
        self._loading = False
        self._cfg = get_raw_config()
        self._entries: list[dict[str, Any]] = [dict(e) for e in self._cfg["searches"]]
        self._build_ui()
        self._load()

    # -- ui ----------------------------------------------------------------

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        tabs = QTabWidget()
        tabs.addTab(self._searches_tab(), "Searches")
        tabs.addTab(self._behaviour_tab(), "Behaviour")
        layout.addWidget(tabs, 1)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        restore = buttons.addButton(
            "Restore defaults", QDialogButtonBox.ButtonRole.ResetRole
        )
        qconnect(restore.clicked, self._restore_defaults)
        qconnect(buttons.accepted, self._save)
        qconnect(buttons.rejected, self.reject)
        layout.addWidget(buttons)

    def _searches_tab(self) -> QWidget:
        tab = QWidget()
        outer = QVBoxLayout(tab)

        intro = QLabel(
            "Tick the searches you want. Each one becomes an icon next to the "
            "word you click, and an entry in the right-click menu. Add any "
            "website you like with <b>Add...</b>"
        )
        intro.setWordWrap(True)
        outer.addWidget(intro)

        row = QHBoxLayout()
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Search", "Icon", "URL"])
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        qconnect(self.table.itemChanged, self._item_changed)
        qconnect(self.table.doubleClicked, self._edit_search)
        row.addWidget(self.table, 1)

        side = QVBoxLayout()
        for label, slot in (
            ("Add...", self._add_search),
            ("Edit...", self._edit_search),
            ("Remove", self._remove_search),
            ("Move up", self._move_up),
            ("Move down", self._move_down),
        ):
            button = QPushButton(label)
            qconnect(button.clicked, slot)
            side.addWidget(button)
        side.addStretch(1)
        row.addLayout(side)

        outer.addLayout(row, 1)
        return tab

    def _behaviour_tab(self) -> QWidget:
        tab = QWidget()
        outer = QVBoxLayout(tab)

        icons_group = QGroupBox("Floating icons on cards")
        icons_form = QFormLayout(icons_group)
        self.popup_cb = QCheckBox("Show the search icons next to the word")
        icons_form.addRow(self.popup_cb)
        self.trigger_combo = QComboBox()
        self.trigger_combo.addItem("As soon as a word is clicked", "click")
        self.trigger_combo.addItem("Only when I select text myself", "selection")
        icons_form.addRow("Show them", self.trigger_combo)
        self.size_spin = QSpinBox()
        self.size_spin.setRange(18, 64)
        self.size_spin.setSuffix(" px")
        icons_form.addRow("Icon size", self.size_spin)
        outer.addWidget(icons_group)

        menu_group = QGroupBox("Right-click menu")
        menu_form = QFormLayout(menu_group)
        self.reviewer_cb = QCheckBox("On cards while reviewing")
        self.editor_cb = QCheckBox("In the note editor (Add and Browse)")
        self.more_cb = QCheckBox("In the reviewer More menu (m key)")
        self.submenu_cb = QCheckBox("Group the searches in a submenu")
        menu_form.addRow(self.reviewer_cb)
        menu_form.addRow(self.editor_cb)
        menu_form.addRow(self.more_cb)
        menu_form.addRow(self.submenu_cb)
        self.submenu_edit = QLineEdit()
        menu_form.addRow("Submenu name", self.submenu_edit)
        self.show_selection_cb = QCheckBox("Show the selected text in each entry")
        menu_form.addRow(self.show_selection_cb)
        self.label_length_spin = QSpinBox()
        self.label_length_spin.setRange(8, 80)
        self.label_length_spin.setSuffix(" characters")
        menu_form.addRow("Shorten it to", self.label_length_spin)
        outer.addWidget(menu_group)

        text_group = QGroupBox("Selected text")
        text_form = QFormLayout(text_group)
        self.max_chars_spin = QSpinBox()
        self.max_chars_spin.setRange(10, 500)
        self.max_chars_spin.setSuffix(" characters")
        text_form.addRow("Search at most", self.max_chars_spin)
        self.cloze_cb = QCheckBox("Search {{c1::word}} as word")
        self.sound_cb = QCheckBox("Drop [sound:...] tags")
        self.punct_cb = QCheckBox("Trim quotes, brackets and commas")
        text_form.addRow(self.cloze_cb)
        text_form.addRow(self.sound_cb)
        text_form.addRow(self.punct_cb)
        outer.addWidget(text_group)

        outer.addStretch(1)
        return tab

    # -- load / save -------------------------------------------------------

    def _load(self) -> None:
        cfg = self._cfg
        self.popup_cb.setChecked(bool(cfg.get("popup_enabled", True)))
        trigger = "selection" if str(cfg.get("popup_trigger")) == "selection" else "click"
        index = self.trigger_combo.findData(trigger)
        self.trigger_combo.setCurrentIndex(max(0, index))
        self.size_spin.setValue(int(cfg.get("popup_icon_size") or 30))

        self.reviewer_cb.setChecked(bool(cfg.get("enable_in_reviewer", True)))
        self.editor_cb.setChecked(bool(cfg.get("enable_in_editor", True)))
        self.more_cb.setChecked(bool(cfg.get("enable_in_more_menu", True)))
        self.submenu_cb.setChecked(bool(cfg.get("use_submenu", True)))
        self.submenu_edit.setText(str(cfg.get("submenu_label") or ADDON_NAME))
        self.show_selection_cb.setChecked(bool(cfg.get("show_selection_in_label", True)))
        self.label_length_spin.setValue(int(cfg.get("max_label_length") or 32))

        self.max_chars_spin.setValue(int(cfg.get("max_query_chars") or 200))
        self.cloze_cb.setChecked(bool(cfg.get("strip_cloze_markers", True)))
        self.sound_cb.setChecked(bool(cfg.get("strip_sound_tags", True)))
        self.punct_cb.setChecked(bool(cfg.get("strip_surrounding_punctuation", True)))

        self._refresh_table()

    def _refresh_table(self, select_row: int | None = None) -> None:
        self._loading = True
        try:
            self.table.setRowCount(0)
            for entry in self._entries:
                row = self.table.rowCount()
                self.table.insertRow(row)

                name_item = QTableWidgetItem(str(entry.get("name") or ""))
                name_item.setFlags(name_item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                name_item.setCheckState(
                    Qt.CheckState.Checked
                    if entry.get("enabled", True)
                    else Qt.CheckState.Unchecked
                )
                self.table.setItem(row, 0, name_item)
                self.table.setItem(
                    row,
                    1,
                    QTableWidgetItem(
                        describe_icon(entry.get("icon", ""), entry.get("name", ""))
                    ),
                )
                self.table.setItem(row, 2, QTableWidgetItem(str(entry.get("url") or "")))
        finally:
            self._loading = False

        if select_row is not None and 0 <= select_row < len(self._entries):
            self.table.selectRow(select_row)

    def _current_row(self) -> int:
        rows = self.table.selectionModel().selectedRows() if self.table.selectionModel() else []
        if rows:
            return rows[0].row()
        return self.table.currentRow()

    def _save(self, *_: Any) -> None:
        cfg = dict(self._cfg)
        cfg["popup_enabled"] = self.popup_cb.isChecked()
        cfg["popup_trigger"] = self.trigger_combo.currentData() or "click"
        cfg["popup_icon_size"] = self.size_spin.value()
        cfg["enable_in_reviewer"] = self.reviewer_cb.isChecked()
        cfg["enable_in_editor"] = self.editor_cb.isChecked()
        cfg["enable_in_more_menu"] = self.more_cb.isChecked()
        cfg["use_submenu"] = self.submenu_cb.isChecked()
        cfg["submenu_label"] = self.submenu_edit.text().strip() or ADDON_NAME
        cfg["show_selection_in_label"] = self.show_selection_cb.isChecked()
        cfg["max_label_length"] = self.label_length_spin.value()
        cfg["max_query_chars"] = self.max_chars_spin.value()
        cfg["strip_cloze_markers"] = self.cloze_cb.isChecked()
        cfg["strip_sound_tags"] = self.sound_cb.isChecked()
        cfg["strip_surrounding_punctuation"] = self.punct_cb.isChecked()
        cfg["searches"] = [dict(entry) for entry in self._entries]

        if not any(entry.get("enabled") for entry in cfg["searches"]):
            if not askUser(
                "No search is ticked, so no icons or menu entries will show up.\n"
                "Save anyway?",
                parent=self,
            ):
                return

        save_config(cfg)
        refresh_webviews()
        tooltip("Settings saved")
        super().accept()

    # -- search list slots -------------------------------------------------

    def _item_changed(self, item: QTableWidgetItem) -> None:
        if self._loading or item is None or item.column() != 0:
            return
        row = item.row()
        if 0 <= row < len(self._entries):
            self._entries[row]["enabled"] = (
                item.checkState() == Qt.CheckState.Checked
            )

    def _add_search(self, *_: Any) -> None:
        dialog = ProviderDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self._entries.append(dialog.entry())
            self._refresh_table(len(self._entries) - 1)

    def _edit_search(self, *_: Any) -> None:
        row = self._current_row()
        if not 0 <= row < len(self._entries):
            return
        dialog = ProviderDialog(self, self._entries[row])
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self._entries[row] = dialog.entry()
            self._refresh_table(row)

    def _remove_search(self, *_: Any) -> None:
        row = self._current_row()
        if not 0 <= row < len(self._entries):
            return
        name = self._entries[row].get("name") or "this search"
        if not askUser(f"Remove {name}?", parent=self):
            return
        del self._entries[row]
        self._refresh_table(min(row, len(self._entries) - 1))

    def _move(self, offset: int) -> None:
        row = self._current_row()
        target = row + offset
        if not (0 <= row < len(self._entries) and 0 <= target < len(self._entries)):
            return
        self._entries[row], self._entries[target] = (
            self._entries[target],
            self._entries[row],
        )
        self._refresh_table(target)

    def _move_up(self, *_: Any) -> None:
        self._move(-1)

    def _move_down(self, *_: Any) -> None:
        self._move(1)

    def _restore_defaults(self, *_: Any) -> None:
        if not askUser(
            "Put every setting and every search back to the defaults?", parent=self
        ):
            return
        self._cfg = copy.deepcopy(DEFAULT_CONFIG)
        self._entries = [dict(entry) for entry in self._cfg["searches"]]
        self._load()


# ---------------------------------------------------------------------------
# entry points
# ---------------------------------------------------------------------------

_menu_action: Any = None


def open_settings() -> None:
    dialog = SettingsDialog(mw)
    dialog.exec()


def add_tools_menu_action() -> None:
    global _menu_action
    if mw is None or _menu_action is not None:
        return
    label = f"{ADDON_NAME}..."
    try:
        # a second copy of the add-on (e.g. a copied folder next to the AnkiWeb
        # install) must not add a second Tools entry
        for existing in mw.form.menuTools.actions():
            if existing.text() == label:
                _menu_action = existing
                return
    except Exception:
        pass
    try:
        action = QAction(label, mw)
        qconnect(action.triggered, lambda *_: open_settings())
        mw.form.menuTools.addAction(action)
        _menu_action = action
    except Exception as exc:  # pragma: no cover - depends on Anki's UI state
        print(f"{ADDON_NAME}: could not add the Tools menu entry ({exc})")
