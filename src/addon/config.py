from typing import Any, List
from pathlib import Path
import json

from aqt import colors
from aqt.qt import *
from aqt.utils import openLink, tooltip
from aqt.theme import theme_manager

from .ankiaddonconfig import ConfigManager, ConfigWindow, ConfigLayout
from .colors import recolor_python, recolor_web
from .migrate import maybe_migrate_config

THEMES_DIR = Path(__file__).parent / "themes"


conf = ConfigManager()

QDir.addSearchPath("ReColor", str(Path(__file__).parent / "AnKing"))


def open_web(url: str) -> None:
    openLink(f"https://{url}")


def header_layout(conf_window: ConfigWindow) -> QHBoxLayout:
    icons_layout = QHBoxLayout()
    icons_layout.addStretch()
    images = [
        ("AnKingSmall.png", (31, 31), "www.ankingmed.com"),
        ("YouTube.png", (31, 31), "www.youtube.com/theanking"),
        ("Patreon.png", (221, 31), "www.patreon.com/ankingmed"),
        ("Instagram.png", (31, 31), "instagram.com/ankingmed"),
        ("Facebook.png", (31, 31), "facebook.com/ankingmed"),
    ]
    for image in images:
        icon = QIcon()
        icon.addPixmap(
            QPixmap(f"ReColor:{image[0]}"), QIcon.Mode.Normal, QIcon.State.Off
        )
        button = QToolButton(conf_window)
        button.setIcon(icon)
        button.setIconSize(QSize(*image[1]))
        button.setMaximumSize(QSize(*image[1]))
        button.setMinimumSize(QSize(*image[1]))
        button.clicked.connect(lambda _, url=image[2]: open_web(url))
        button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        button.setStyleSheet("QToolButton { border: none; }")
        icons_layout.addWidget(button)
    icons_layout.addStretch()
    return icons_layout


def on_save() -> None:
    conf.save()
    recolor_python()
    recolor_web()


def with_window(conf_window: ConfigWindow) -> None:
    conf_window.setWindowTitle("ReColor Settings")
    conf_window.setMinimumWidth(500)
    conf_window.execute_on_save(on_save)
    conf_window.main_layout.insertLayout(0, header_layout(conf_window))
    conf_window.main_layout.insertSpacing(1, 10)
    conf_window.after_advanced_save_hook.append(lambda: maybe_migrate_config(conf))


def color_idx() -> int:
    return 2 if theme_manager.night_mode else 1


def populate_tab(layout: ConfigLayout, conf_keys: List[str]) -> None:
    for conf_key in conf_keys:
        name = conf.get(f"colors.{conf_key}.0")
        anki_color = getattr(colors, conf_key, None)
        description = anki_color["comment"] if anki_color is not None else None
        layout.color_input(
            f"colors.{conf_key}.{color_idx()}", name, tooltip=description, opacity=True
        )
    layout.stretch()


def main_tab(conf_window: ConfigWindow) -> None:
    conf_keys = [
        "FG",
        "FG_SUBTLE",
        "FG_DISABLED",
        "FG_FAINT",
        "FG_LINK",
        "CANVAS",
        "CANVAS_ELEVATED",
        "CANVAS_INSET",
        "CANVAS_OVERLAY",
        "CANVAS_CODE",
        "BORDER",
        "BORDER_SUBTLE",
        "BORDER_STRONG",
        "BORDER_FOCUS",
    ]
    tab = conf_window.add_tab("Main")
    populate_tab(tab, conf_keys)


def buttons_tab(conf_window: ConfigWindow) -> None:
    conf_keys = [
        "BUTTON_BG",
        "BUTTON_HOVER",
        "BUTTON_HOVER_BORDER",
        "BUTTON_DISABLED",
    ]
    tab = conf_window.add_tab("Buttons")
    populate_tab(tab, conf_keys)


def cards_tab(conf_window: ConfigWindow) -> None:
    conf_keys = [
        "STATE_NEW",
        "STATE_LEARN",
        "STATE_REVIEW",
        "STATE_SUSPENDED",
        "STATE_BURIED",
        "FLAG_1",
        "FLAG_2",
        "FLAG_3",
        "FLAG_4",
        "FLAG_5",
        "FLAG_6",
        "FLAG_7",
        "ACCENT_CARD",
        "ACCENT_NOTE",
    ]
    tab = conf_window.add_tab("Cards")
    populate_tab(tab, conf_keys)


def misc_tab(conf_window: ConfigWindow) -> None:
    conf_keys = [
        "HIGHLIGHT_BG",
        "HIGHLIGHT_FG",
        "SELECTED_BG",
        "SELECTED_FG",
        "ACCENT_DANGER",
        "SHADOW",
        "SHADOW_INSET",
        "SHADOW_SUBTLE",
        "SHADOW_FOCUS",
        "SCROLLBAR_BG",
        "SCROLLBAR_BG_ACTIVE",
        "SCROLLBAR_BG_HOVER",
    ]
    tab = conf_window.add_tab("Misc")
    populate_tab(tab, conf_keys)


def themes_list() -> List[str]:
    themes = []
    for child in sorted(THEMES_DIR.iterdir()):
        if child.is_file() and child.suffix == ".json":
            themes.append(child.stem)
    return themes


def replace_conf_color(conf: ConfigManager, theme_json: Any, dark_mode: bool) -> None:
    modeidx = 2 if dark_mode else 1

    for color in theme_json["colors"]:
        conf[f"colors.{color}.{modeidx}"] = theme_json["colors"][color][modeidx]


def apply_theme(conf_window: ConfigWindow, theme: str) -> None:
    theme_path = THEMES_DIR / f"{theme}.json"
    theme_json = json.loads(theme_path.read_text())

    # Dark mode or universal
    if not theme.startswith("(dark)"):
        replace_conf_color(conf, theme_json, False)
    # Light mode or universal
    if not theme.startswith("(light)"):
        replace_conf_color(conf, theme_json, True)

    conf_window.update_widgets()
    conf_window.main_tab.setCurrentIndex(0)

    tooltip(f"Applied theme: {theme}<br />Press save to save changes")


def themes_tab(conf_window: ConfigWindow) -> None:
    tab = conf_window.add_tab("Themes")
    tab.space(10)

    tab.text(
        "Note: You may need to toggle dark mode in Anki preferences to see changes",
        multiline=True,
    )

    apply_lay = tab.hlayout()
    apply_lay.text("Themes:")
    apply_lay.space(10)

    combobox = QComboBox(conf_window)
    combobox.insertItems(0, themes_list())
    apply_lay.addWidget(combobox)

    btn = QPushButton("Apply theme", conf_window)
    btn.clicked.connect(lambda _: apply_theme(conf_window, combobox.currentText()))
    apply_lay.addWidget(btn)
    apply_lay.stretch()

    tab.text_button(
        "View other themes on the web",
        "https://github.com/AnKingMed/AnkiRecolor/wiki/Themes",
        lambda _: open_web("github.com/AnKingMed/AnkiRecolor/wiki/Themes"),
    )

    tab.stretch()


conf.use_custom_window()
conf.on_window_open(with_window)
conf.add_config_tab(main_tab)
conf.add_config_tab(buttons_tab)
conf.add_config_tab(cards_tab)
conf.add_config_tab(misc_tab)
conf.add_config_tab(themes_tab)
