from typing import Any, Optional

import aqt
from aqt.webview import AnkiWebView
import aqt.colors
from aqt import gui_hooks, mw
from aqt.theme import theme_manager
from aqt.qt import QColor

from .ankiaddonconfig import ConfigManager

conf = ConfigManager()


# ReColor Python Colors
def recolor_python() -> None:
    conf.load()
    color_entries = conf.get("colors")
    for color_name in color_entries:
        if (anki_color := getattr(aqt.colors, color_name, None)) is not None:
            color_entry = color_entries[color_name]
            anki_color["light"] = color_entry[1]
            anki_color["dark"] = color_entry[2]
            setattr(aqt.colors, color_name, anki_color)
    theme_manager.apply_style()


def get_window_bg_color(*args: Any) -> QColor:
    color_idx = 2 if theme_manager.night_mode else 1
    hex_color = conf.get(f"colors.CANVAS.{color_idx}")
    return QColor(hex_color)


def replace_webview_bg() -> None:
    AnkiWebView.get_window_bg_color = get_window_bg_color  # type: ignore


# ReColor CSS Colors


def wrap_style(css: str) -> str:
    return f"<style>{css}</style>"


def inject_web(web_content: aqt.webview.WebContent, context: Optional[Any]) -> None:
    conf.load()
    colors_config = conf["colors"]

    light_mode_css = ""
    dark_mode_css = ""
    for name in colors_config:
        entry = colors_config[name]
        css_names = entry[3]
        if not isinstance(css_names, list):
            css_names = [css_names]
        for css_name in css_names:
            light_mode_css += f"{css_name}: {entry[1]};\n"
            dark_mode_css += f"{css_name}: {entry[2]};\n"

    web_content.head += wrap_style("body { \n%s }" % light_mode_css)
    web_content.head += wrap_style("body.night_mode { \n%s }" % dark_mode_css)


gui_hooks.webview_will_set_content.append(inject_web)
recolor_python()
