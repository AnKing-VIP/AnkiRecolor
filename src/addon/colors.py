from typing import Any, Optional, Tuple, List

from anki.hooks import wrap
import aqt
import aqt.colors
from aqt import gui_hooks, mw
from aqt.webview import AnkiWebView
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


def get_theme_css() -> Tuple[str, str]:
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

    return (light_mode_css, dark_mode_css)


def inject_web(web_content: aqt.webview.WebContent, context: Optional[Any]) -> None:
    (light_mode_css, dark_mode_css) = get_theme_css()
    web_content.head += (
        "<style id='recolor-light'>body { \n%s }</style>" % light_mode_css
    )
    web_content.head += (
        "<style id='recolor-dark'>body.night_mode { \n%s }</style>" % dark_mode_css
    )


webviews: List[AnkiWebView] = []


def recolor_web() -> None:
    global webviews
    for webview in webviews:
        update_webview_css(webview)


def update_webview_css(webview: AnkiWebView) -> None:
    (light_mode_css, dark_mode_css) = get_theme_css()
    webview.eval(
        "document.getElementById('recolor-light').innerHTML = `body { \n%s }`"
        % light_mode_css
    )
    webview.eval(
        "document.getElementById('recolor-dark').innerHTML = `body.night_mode { \n%s }`"
        % dark_mode_css
    )


def on_webview_init(webview: AnkiWebView, *args: Any, **kwargs: Any) -> None:
    global webviews
    webviews.append(webview)


def on_webview_cleanup(webview: AnkiWebView) -> None:
    global webviews
    webviews.remove(webview)


if mw.web:
    webviews.append(mw.web)
if mw.toolbarWeb:
    webviews.append(mw.toolbarWeb)
if mw.bottomWeb:
    webviews.append(mw.bottomWeb)


AnkiWebView.__init__ = wrap(AnkiWebView.__init__, on_webview_init, "before")
AnkiWebView.cleanup = wrap(AnkiWebView.cleanup, on_webview_init, "before")
gui_hooks.webview_will_set_content.append(inject_web)
recolor_python()
