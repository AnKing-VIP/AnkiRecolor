from typing import Callable, List, Tuple, TYPE_CHECKING, Optional
from pathlib import Path

import aqt.addons
from aqt import mw
from aqt.qt import *
from aqt.utils import tooltip, showText, saveGeom, restoreGeom

from .errors import InvalidConfigValueError

if TYPE_CHECKING:
    from .manager import ConfigManager

QT6 = QT_VERSION_STR.split(".")[0] == "6"


class ConfigWindow(QDialog):
    def __init__(self, conf: "ConfigManager") -> None:
        QDialog.__init__(self, mw, Qt.WindowType.Window)  # type: ignore
        self.setModal(True)
        self.conf = conf
        self.mgr = mw.addonManager
        self.widget_updates: List[Callable[[], None]] = []
        self.should_save_hook: List[Callable[[], bool]] = []
        self._on_save_hook: List[Callable[[], None]] = []
        self._on_close_hook: List[Callable[[], None]] = []
        self.geom_key = f"addonconfig-{conf.addon_name}"

        self.setWindowTitle(f"Config for {conf.addon_name}")
        self.setup()

    def setup(self) -> None:
        self.outer_layout = ConfigLayout(self, QBoxLayout.Direction.TopToBottom)
        self.main_layout = ConfigLayout(self, QBoxLayout.Direction.TopToBottom)
        self.btn_layout = ConfigLayout(self, QBoxLayout.Direction.LeftToRight)
        self.outer_layout.addLayout(self.main_layout)
        self.outer_layout.addLayout(self.btn_layout)
        self.setLayout(self.outer_layout)

        self.main_tab = QTabWidget()
        main_tab = self.main_tab
        main_tab.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.main_layout.addWidget(main_tab)
        self.setup_buttons(self.btn_layout)

    def setup_buttons(self, btn_box: "ConfigLayout") -> None:
        self.advanced_btn = QPushButton("Advanced")
        self.advanced_btn.clicked.connect(self.on_advanced)
        btn_box.addWidget(self.advanced_btn)

        self.reset_btn = QPushButton("Restore Defaults")
        self.reset_btn.clicked.connect(self.on_reset)
        btn_box.addWidget(self.reset_btn)

        btn_box.addStretch(1)

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.on_cancel)
        btn_box.addWidget(self.cancel_btn)

        self.save_btn = QPushButton("Save")
        self.save_btn.setDefault(True)
        self.save_btn.setShortcut("Ctrl+Return")
        self.save_btn.clicked.connect(self.on_save)
        btn_box.addWidget(self.save_btn)

    def update_widgets(self) -> None:
        try:
            for widget_update in self.widget_updates:
                widget_update()
        except Exception as e:
            advanced = self.advanced_window()
            dial, bbox = showText(
                "Invalid Config. Please fix the following issue in the advanced config editor. \n\n"
                + str(e),
                title="Invalid Config",
                parent=advanced,
                run=False,
            )
            button = QPushButton("Quit Config")
            bbox.addButton(button, QDialogButtonBox.ButtonRole.DestructiveRole)
            bbox.button(QDialogButtonBox.StandardButton.Close).setDefault(True)

            def quit() -> None:
                self.widget_updates = []
                dial.close()
                advanced.reject()
                self.close()

            button.clicked.connect(quit)
            dial.setModal(True)
            dial.show()

    def on_open(self) -> None:
        self.update_widgets()
        restoreGeom(self, self.geom_key)

    def on_save(self) -> None:
        for hook in self.should_save_hook:
            if not hook():
                return
        for hook in self._on_save_hook:
            hook()
        self.conf.save()
        self.close()

    def on_cancel(self) -> None:
        self.close()

    def on_reset(self) -> None:
        self.conf.load_defaults()
        self.update_widgets()
        tooltip("Press save to save changes")

    def on_advanced(self) -> None:
        self.advanced_window()

    def advanced_window(self) -> aqt.addons.ConfigEditor:
        def on_finish(result: int) -> None:
            self.conf.load()
            self.update_widgets()

        diag = aqt.addons.ConfigEditor(
            self, self.conf.addon_dir, self.conf._config  # type: ignore
        )
        diag.finished.connect(on_finish)
        diag.show()
        return diag

    def closeEvent(self, evt: QCloseEvent) -> None:
        # Discard the contents when clicked cancel,
        # and also in case the window was clicked without clicking any of the buttons
        for hook in self._on_close_hook:
            hook()
        self.conf.load()
        saveGeom(self, self.geom_key)
        evt.accept()

    # Add Widgets

    def add_tab(self, name: str) -> "ConfigLayout":
        tab = QWidget(self)
        layout = ConfigLayout(self, QBoxLayout.Direction.TopToBottom)
        tab.setLayout(layout)
        self.main_tab.addTab(tab, name)
        return layout

    def execute_on_save(self, hook: Callable[[], None]) -> None:
        self._on_save_hook.append(hook)

    def execute_on_close(self, hook: Callable[[], None]) -> None:
        self._on_close_hook.append(hook)

    def set_footer(
        self,
        text: str,
        html: bool = False,
        size: int = 0,
        multiline: bool = False,
        tooltip: Optional[str] = None,
    ) -> QLabel:
        footer = QLabel(text)
        if html:
            footer.setTextFormat(Qt.TextFormat.RichText)
            footer.setOpenExternalLinks(True)
        else:
            footer.setTextFormat(Qt.TextFormat.PlainText)
        if size:
            font = QFont()
            font.setPixelSize(size)
            footer.setFont(font)
        if multiline:
            footer.setWordWrap(True)
        if tooltip is not None:
            footer.setToolTip(tooltip)

        self.main_layout.addWidget(footer)
        return footer


class ConfigLayout(QBoxLayout):
    def __init__(self, conf_window: ConfigWindow, direction: QBoxLayout.Direction):
        QBoxLayout.__init__(self, direction)
        self.conf = conf_window.conf
        self.config_window = conf_window
        self.widget_updates = conf_window.widget_updates

    # Config Input Widgets

    def checkbox(
        self, key: str, description: Optional[str] = None, tooltip: Optional[str] = None
    ) -> QCheckBox:
        "For boolean config"
        checkbox = QCheckBox()
        if description is not None:
            checkbox.setText(description)
        if tooltip is not None:
            checkbox.setToolTip(tooltip)

        def update() -> None:
            value = self.conf.get(key)
            if not isinstance(value, bool):
                raise InvalidConfigValueError(key, "boolean", value)
            checkbox.setChecked(value)

        self.widget_updates.append(update)

        checkbox.stateChanged.connect(
            lambda s: self.conf.set(
                key,
                s == (Qt.CheckState.Checked.value if QT6 else Qt.CheckState.Checked),  # type: ignore
            )
        )
        self.addWidget(checkbox)
        return checkbox

    def dropdown(
        self,
        key: str,
        labels: list,
        values: list,
        description: Optional[str] = None,
        tooltip: Optional[str] = None,
    ) -> QComboBox:
        combobox = QComboBox()
        combobox.insertItems(0, labels)
        if tooltip is not None:
            combobox.setToolTip(tooltip)

        def update() -> None:
            conf = self.conf
            try:
                val = conf.get(key)
                index = values.index(val)
            except ValueError:
                raise InvalidConfigValueError(
                    key, "any value in list " + str(values), val
                )
            combobox.setCurrentIndex(index)

        self.widget_updates.append(update)

        combobox.currentIndexChanged.connect(
            lambda idx: self.conf.set(key, values[idx])
        )

        if description is not None:
            row = self.hlayout()
            row.text(description, tooltip=tooltip)
            row.space(7)
            row.addWidget(combobox)
            row.stretch()
        else:
            self.addWidget(combobox)

        return combobox

    def text_input(
        self, key: str, description: Optional[str] = None, tooltip: Optional[str] = None
    ) -> QLineEdit:
        "For string config"
        line_edit = QLineEdit()
        if tooltip is not None:
            line_edit.setToolTip(tooltip)

        def update() -> None:
            val = self.conf.get(key)
            if not isinstance(val, str):
                raise InvalidConfigValueError(key, "string", val)
            line_edit.setText(val)
            line_edit.setCursorPosition(0)

        self.widget_updates.append(update)

        line_edit.textChanged.connect(lambda text: self.conf.set(key, text))

        if description is not None:
            row = self.hlayout()
            row.text(description, tooltip=tooltip)
            row.space(7)
            row.addWidget(line_edit)
        else:
            self.addWidget(line_edit)
        return line_edit

    def number_input(
        self,
        key: str,
        description: Optional[str] = None,
        tooltip: Optional[str] = None,
        minimum: int = 0,
        maximum: int = 99,
        step: int = 1,
        decimal: bool = False,
        precision: int = 2,
    ) -> Union[QDoubleSpinBox, QSpinBox]:
        "For integer config"
        spin_box: Union[QDoubleSpinBox, QSpinBox]
        if decimal:
            spin_box = QDoubleSpinBox()
            spin_box.setDecimals(precision)
        else:
            spin_box = QSpinBox()
        if tooltip is not None:
            spin_box.setToolTip(tooltip)
        spin_box.setMinimum(minimum)
        spin_box.setMaximum(maximum)
        spin_box.setSingleStep(step)

        def update() -> None:
            val = self.conf.get(key)
            if not decimal and not isinstance(val, int):
                raise InvalidConfigValueError(key, "integer number", val)
            if decimal and not isinstance(val, (int, float)):
                raise InvalidConfigValueError(key, "number", val)
            if minimum is not None and val < minimum:
                raise InvalidConfigValueError(
                    key, f"integer number greater or equal to {minimum}", val
                )
            if maximum is not None and val > maximum:
                raise InvalidConfigValueError(
                    key, f"integer number lesser or equal to {maximum}", val
                )
            spin_box.setValue(val)

        self.widget_updates.append(update)

        spin_box.valueChanged.connect(lambda val: self.conf.set(key, val))

        if description is not None:
            row = self.hlayout()
            row.text(description, tooltip=tooltip)
            row.space(7)
            row.addWidget(spin_box)
            row.stretch()
        else:
            self.addWidget(spin_box)
        return spin_box

    def color_input(
        self,
        key: str,
        description: Optional[str] = None,
        tooltip: Optional[str] = None,
        opacity: bool = False,
    ) -> QPushButton:
        """For hex color config.
        If opacity is true, allows changing opacity. Note that color is stored in RGBA format, not ARGB.
            When creating using the RGBA in Qt, you need to change it to ARGB format first.
        """
        color: QColor
        button = QPushButton()
        button.setFixedWidth(25)
        button.setFixedHeight(25)
        button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        if tooltip is not None:
            button.setToolTip(tooltip)

        def set_color(rgb: str) -> None:
            nonlocal color
            if len(rgb) == 9:
                rgb = "#" + rgb[7:] + rgb[1:7]  # RGBA to ARGB

            button.setStyleSheet(
                'QPushButton{ background-color: "%s"; border: none; border-radius: 3px}'
                % rgb  # QT bug? CSS accepts ARGB instead of RGBA.
            )
            color = QColor()
            color.setNamedColor(rgb)  # Accepts #RGB, #RRGGBB or #AARRGGBB
            if not color.isValid():
                raise InvalidConfigValueError(key, "rgb hex color string", rgb)

        def update() -> None:
            value = self.conf.get(key)
            set_color(value)

        def save(color: QColor) -> None:
            if opacity:
                rgb = color.name(QColor.NameFormat.HexArgb)
                rgb = "#" + rgb[3:] + rgb[1:3]  # ARGB to RGBA
            else:
                rgb = color.name()
            self.conf.set(key, rgb)
            set_color(rgb)

        def open_color_dialog() -> None:
            color_dialog = QColorDialog(self.config_window)
            if opacity:
                color_dialog.setOptions(QColorDialog.ColorDialogOption.ShowAlphaChannel)
            color_dialog.setCurrentColor(color)
            color_dialog.colorSelected.connect(lambda c: save(c))
            color_dialog.exec()

        self.widget_updates.append(update)

        button.clicked.connect(lambda _: open_color_dialog())

        if description is not None:
            row = self.hlayout()
            row.text(description, tooltip=tooltip)
            row.space(7)
            row.addWidget(button)
            row.stretch()
        else:
            self.addWidget(button)

        return button

    def path_input(
        self,
        key: str,
        description: Optional[str] = None,
        tooltip: Optional[str] = None,
        get_directory: bool = False,
        filter: str = "Any files (*)",
    ) -> Tuple[QLineEdit, QPushButton]:
        "For path string config"

        row = self.hlayout()
        if description is not None:
            row.text(description, tooltip=tooltip)
            row.space(7)
        line_edit = QLineEdit()
        line_edit.setReadOnly(True)
        row.addWidget(line_edit)
        button = QPushButton("Browse")
        row.addWidget(button)
        if tooltip is not None:
            line_edit.setToolTip(tooltip)

        def update() -> None:
            val = self.conf.get(key)
            if not isinstance(val, str):
                raise InvalidConfigValueError(key, "string file path", val)
            line_edit.setText(val)

        def get_path() -> None:
            val = self.conf.get(key)
            parent_dir = str(Path(val).parent)

            if get_directory:
                path = QFileDialog.getExistingDirectory(
                    self.config_window, directory=parent_dir
                )
            else:
                path = QFileDialog.getOpenFileName(
                    self.config_window, directory=parent_dir, filter=filter
                )[0]
            if path:  # is None if cancelled
                self.conf.set(key, path)
                update()

        self.widget_updates.append(update)
        button.clicked.connect(get_path)

        return (line_edit, button)

    def shortcut_input(
        self, key: str, description: Optional[str] = None, tooltip: Optional[str] = None
    ) -> Tuple[QKeySequenceEdit, QPushButton]:
        edit = QKeySequenceEdit()

        if description is not None:
            row = self.hlayout()
            row.text(description, tooltip=tooltip)

        def update() -> None:
            val = self.conf.get(key)
            if not isinstance(val, str):
                raise InvalidConfigValueError(key, "str", val)
            val = val.replace(" ", "")
            edit.setKeySequence(val)

        self.widget_updates.append(update)

        edit.keySequenceChanged.connect(  # type: ignore
            lambda s: self.conf.set(key, edit.keySequence().toString())
        )

        def on_shortcut_clear_btn_click() -> None:
            edit.clear()

        shortcut_clear_btn = QPushButton("Clear")
        shortcut_clear_btn.setSizePolicy(
            QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed
        )
        shortcut_clear_btn.clicked.connect(on_shortcut_clear_btn_click)  # type: ignore

        layout = QHBoxLayout()
        layout.addWidget(edit)
        layout.addWidget(shortcut_clear_btn)

        self.addLayout(layout)
        return edit, shortcut_clear_btn

    # Layout widgets

    def text(
        self,
        text: str,
        bold: bool = False,
        html: bool = False,
        size: int = 0,
        multiline: bool = False,
        tooltip: Optional[str] = None,
    ) -> QLabel:
        label_widget = QLabel(text)
        label_widget.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextBrowserInteraction
        )
        if html:
            label_widget.setTextFormat(Qt.TextFormat.RichText)
            label_widget.setOpenExternalLinks(True)
        else:
            label_widget.setTextFormat(Qt.TextFormat.PlainText)
        if bold or size:
            font = QFont()
            if bold:
                font.setBold(True)
            if size:
                font.setPixelSize(size)
            label_widget.setFont(font)
        if multiline:
            label_widget.setWordWrap(True)
        if tooltip is not None:
            label_widget.setToolTip(tooltip)

        self.addWidget(label_widget)
        return label_widget

    def text_button(
        self,
        text: str,
        tooltip: str = "",
        on_click: Optional[Callable] = None,
        color: str = "",
        size: int = 0,
        url: str = "/",
    ) -> QLabel:
        """A QLabel that behaves like a button.

        on_click is provided 1 argument: 'url'.
        """
        css = "text-decoration: none;"
        if color:
            css += f" color: {color};"
        if size:
            css += f" font-size: {size}px;"
        label = QLabel(f'<a href="{url}" style="{css}">{text}</a>')
        label.setTextFormat(Qt.TextFormat.RichText)
        if tooltip:
            label.setToolTip(tooltip)
        if on_click:
            label.linkActivated.connect(on_click)

        self.addWidget(label)
        return label

    def _separator(self, direction: QFrame.Shape) -> QFrame:
        """direction should be either QFrame.HLine or QFrame.VLine"""
        line = QFrame()
        line.setLineWidth(0)
        line.setFrameShape(direction)
        line.setFrameShadow(QFrame.Shadow.Plain)
        self.addWidget(line)
        return line

    def hseparator(self) -> QFrame:
        return self._separator(QFrame.Shape.HLine)

    def vseparator(self) -> QFrame:
        return self._separator(QFrame.Shape.VLine)

    def _container(self, direction: QBoxLayout.Direction) -> "ConfigLayout":
        """Adds (empty) QWidget > ConfigLayout.

        You can access its parent widget using ConfigLayout.parentWidget()
        """
        container = QWidget()
        inner_layout = ConfigLayout(self.config_window, direction)
        container.setLayout(inner_layout)
        self.addWidget(container)
        return inner_layout

    def hcontainer(self) -> "ConfigLayout":
        """Adds (empty) QWidget > ConfigLayout."""
        return self._container(QBoxLayout.Direction.RightToLeft)

    def vcontainer(self) -> "ConfigLayout":
        """Adds (empty) QWidget > ConfigLayout."""
        return self._container(QBoxLayout.Direction.TopToBottom)

    def _layout(self, direction: QBoxLayout.Direction) -> "ConfigLayout":
        layout = ConfigLayout(self.config_window, direction)
        self.addLayout(layout)
        return layout

    def hlayout(self) -> "ConfigLayout":
        return self._layout(QBoxLayout.Direction.LeftToRight)

    def vlayout(self) -> "ConfigLayout":
        return self._layout(QBoxLayout.Direction.TopToBottom)

    def space(self, space: int = 1) -> None:
        self.addSpacing(space)

    def stretch(self, factor: int = 0) -> None:
        self.addStretch(factor)

    def _scroll_layout(
        self,
        hsizepolicy: QSizePolicy.Policy,
        vsizepolicy: QSizePolicy.Policy,
        hscrollbarpolicy: Qt.ScrollBarPolicy,
        vscrollbarpolicy: Qt.ScrollBarPolicy,
    ) -> "ConfigLayout":
        """Adds QScrollArea > QWidget*2 > ConfigLayout, returns the layout."""
        # QScrollArea seems to automatically add a child widget.
        layout = ConfigLayout(self.config_window, QBoxLayout.Direction.TopToBottom)
        inner_widget = QWidget()
        inner_widget.setLayout(layout)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setWidget(inner_widget)
        scroll.setSizePolicy(hsizepolicy, vsizepolicy)
        scroll.setHorizontalScrollBarPolicy(hscrollbarpolicy)
        scroll.setVerticalScrollBarPolicy(vscrollbarpolicy)
        self.addWidget(scroll)
        return layout

    def hscroll_layout(self, always: bool = False) -> "ConfigLayout":
        """Adds QScrollArea > QWidget*2 > ConfigLayout, returns the layout."""
        scroll = (
            Qt.ScrollBarPolicy.ScrollBarAlwaysOn
            if always
            else Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )
        return self._scroll_layout(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Minimum,
            scroll,
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff,
        )

    def vscroll_layout(self, always: bool = False) -> "ConfigLayout":
        """Adds QScrollArea > QWidget*2 > ConfigLayout, returns the layout."""
        scroll = (
            Qt.ScrollBarPolicy.ScrollBarAlwaysOn
            if always
            else Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )
        return self._scroll_layout(
            QSizePolicy.Policy.Minimum,
            QSizePolicy.Policy.Expanding,
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff,
            scroll,
        )

    def scroll_layout(
        self,
        horizontal: bool = True,
        vertical: bool = True,
    ) -> "ConfigLayout":
        """Legacy. Adds QScrollArea > QWidget*2 > ConfigLayout, returns the layout."""
        return self._scroll_layout(
            QSizePolicy.Policy.Expanding if horizontal else QSizePolicy.Policy.Minimum,
            QSizePolicy.Policy.Expanding if vertical else QSizePolicy.Policy.Minimum,
            Qt.ScrollBarPolicy.ScrollBarAsNeeded,
            Qt.ScrollBarPolicy.ScrollBarAsNeeded,
        )
