from typing import Any, Optional

import aqt
from aqt.theme import theme_manager, colors
from aqt import gui_hooks, mw, dialogs
from aqt.qt import QColor, QPalette, Qt

from .ankiaddonconfig import ConfigManager

conf = ConfigManager()


# Recolor Python Colors

def refresh_all_windows() -> None:
    # Redraw top toolbar
    mw.toolbar.draw()
    # Redraw main body
    if mw.state == "review":
        mw.reviewer.refresh()
    elif mw.state == "overview":
        mw.overview.refresh()
    elif mw.state == "deckBrowser":
        mw.deckBrowser.refresh()
    # Close Browser if open
    browser = dialogs._dialogs["Browser"][1]
    if browser:
        browser.closeWithCallback(lambda: None)


def recolor_python() -> None:
    conf.load()
    color_entries = conf.get("colors")
    for color_name in color_entries:
        color_entry = color_entries[color_name]
        new_color_value = (color_entry[1], color_entry[2])
        setattr(colors, color_name, new_color_value)
    # webview palette uses default one
    theme_manager.default_palette = mw.app.palette()
    theme_manager._apply_style(mw.app)
    apply_palette()
    refresh_all_windows()


def qcolor(conf_key: str) -> QColor:
    color_idx = 2 if theme_manager.night_mode else 1
    hex_color = conf.get(f"colors.{conf_key}.{color_idx}")
    return QColor(hex_color)


def apply_palette() -> None:
    # theme_manager._apply_palette() can only be run in night mode
    color_map = {
        QPalette.WindowText: "TEXT_FG",
        QPalette.ToolTipText: "TEXT_FG",
        QPalette.Text: "TEXT_FG",
        QPalette.ButtonText: "TEXT_FG",
        QPalette.HighlightedText: "HIGHLIGHT_FG",
        QPalette.Highlight: "HIGHLIGHT_BG",
        QPalette.Window: "WINDOW_BG",
        QPalette.AlternateBase: "WINDOW_BG",
        QPalette.Button: "BUTTON_BG",
        QPalette.Base: "FRAME_BG",
        QPalette.ToolTipBase: "FRAME_BG",
        QPalette.Link: "LINK"
    }
    disabled_roles = [
        QPalette.Text,
        QPalette.ButtonText,
        QPalette.HighlightedText
    ]

    palette = QPalette()

    for role in color_map:
        conf_key = color_map[role]
        palette.setColor(role, qcolor(conf_key))

    for role in disabled_roles:
        palette.setColor(
            QPalette.Disabled, role, qcolor("DISABLED"))

    if theme_manager.night_mode:
        palette.setColor(QPalette.BrightText, Qt.red)

    mw.app.setPalette(palette)
    theme_manager.default_palette = palette


# Recolor CSS Colors

def file_url(file_name: str) -> str:
    addon_package = mw.addonManager.addonFromModule(__name__)
    return f"/_addons/{addon_package}/{file_name}"


def inject_js(web_content: aqt.webview.WebContent, context: Optional[Any]) -> None:
    conf.load()
    web_content.body += "<script>Recolor.withConfig('{}')</script>".format(
        conf.to_json())
    web_content.js.append(file_url("recolor.js"))


mw.addonManager.setWebExports(__name__, "recolor.js")
gui_hooks.webview_will_set_content.append(inject_js)
recolor_python()
