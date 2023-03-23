from typing import Any, Optional, Tuple, List, Dict

from anki.hooks import wrap
import aqt
import aqt.colors
from aqt import gui_hooks, mw
from aqt.webview import AnkiWebView
from aqt.theme import theme_manager
from aqt.qt import QColor, QPalette, Qt
from anki.utils import is_mac

from .ankiaddonconfig import ConfigManager

conf = ConfigManager()


# ReColor Python Colors
def recolor_python() -> None:
    conf.load()
    color_entries = conf.get("colors")
    for color_name in color_entries:
        replace_color(color_entries, color_name)
    replace_color(color_entries, "BUTTON_GRADIENT_START", "BUTTON_HOVER")
    replace_color(color_entries, "BUTTON_GRADIENT_END", "BUTTON_HOVER")
    # theme_manager.apply_style() doesn't have an effect in 2.1.57+ if the theme and widget style didn't change,
    # so we call the private functions directly
    theme_manager._apply_palette(aqt.mw.app)
    theme_manager._apply_style(aqt.mw.app)
    _apply_style()


def replace_color(
    color_entries: Dict[str, List[str]],
    anki_name: str,
    addon_name: Optional[str] = None,
) -> None:
    if addon_name is None:
        addon_name = anki_name
    if (anki_color := getattr(aqt.colors, anki_name, None)) is not None:
        color_entry = color_entries[addon_name]
        anki_color["light"] = color_entry[1]
        anki_color["dark"] = color_entry[2]
        setattr(aqt.colors, anki_name, anki_color)


def get_window_bg_color(*args: Any) -> QColor:
    color_idx = 2 if theme_manager.night_mode else 1
    hex_color = conf.get(f"colors.CANVAS.{color_idx}")
    return QColor(hex_color)


def replace_webview_bg() -> None:
    AnkiWebView.get_window_bg_color = get_window_bg_color  # type: ignore


def _apply_style() -> None:
    """
    Used because Anki doesn't style palette in MacOS.

    Mostly identical to aqt.theme_manager._apply_style
    changed Button color to BUTTON_BG from BUTTON_GRADIENT_START
    """
    manager = theme_manager
    palette = QPalette()
    text = manager.qcolor(aqt.colors.FG)
    palette.setColor(QPalette.ColorRole.WindowText, text)
    palette.setColor(QPalette.ColorRole.ToolTipText, text)
    palette.setColor(QPalette.ColorRole.Text, text)
    palette.setColor(QPalette.ColorRole.ButtonText, text)

    hlbg = manager.qcolor(aqt.colors.HIGHLIGHT_BG)
    palette.setColor(
        QPalette.ColorRole.HighlightedText, manager.qcolor(aqt.colors.HIGHLIGHT_FG)
    )
    palette.setColor(QPalette.ColorRole.Highlight, hlbg)

    canvas = manager.qcolor(aqt.colors.CANVAS)
    palette.setColor(QPalette.ColorRole.Window, canvas)
    palette.setColor(QPalette.ColorRole.AlternateBase, canvas)

    palette.setColor(QPalette.ColorRole.Button, manager.qcolor(aqt.colors.BUTTON_BG))

    input_base = manager.qcolor(aqt.colors.CANVAS_CODE)
    palette.setColor(QPalette.ColorRole.Base, input_base)
    palette.setColor(QPalette.ColorRole.ToolTipBase, input_base)

    palette.setColor(
        QPalette.ColorRole.PlaceholderText, manager.qcolor(aqt.colors.FG_SUBTLE)
    )

    disabled_color = manager.qcolor(aqt.colors.FG_DISABLED)
    palette.setColor(
        QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, disabled_color
    )
    palette.setColor(
        QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, disabled_color
    )
    palette.setColor(
        QPalette.ColorGroup.Disabled,
        QPalette.ColorRole.HighlightedText,
        disabled_color,
    )

    palette.setColor(QPalette.ColorRole.Link, manager.qcolor(aqt.colors.FG_LINK))

    palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)

    mw.app.setPalette(palette)


# ReColor CSS Colors


def wrap_style(css: str) -> str:
    return f"<style>{css}</style>"


def get_theme_css() -> Tuple[str, str, str]:
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

    extra_css = """
html button {
    background: var(--button-bg);
}
.night-mode .isMac button {
    --canvas: %s; 
    --fg: %s; 
}
""" % (
        conf["colors.button-bg.2"],
        conf["colors.fg.2"],
    )

    return (light_mode_css, dark_mode_css, extra_css)


def inject_web(web_content: aqt.webview.WebContent, context: Optional[Any]) -> None:
    (light_mode_css, dark_mode_css, extra_css) = get_theme_css()
    web_content.head += (
        "<style id='recolor-light'>body { \n%s }</style>" % light_mode_css
    )
    web_content.head += (
        "<style id='recolor-dark'>body.night_mode { \n%s }</style>" % dark_mode_css
    )
    web_content.head += "<style id='recolor-extra'>%s</style>" % extra_css


webviews: List[AnkiWebView] = []


def recolor_web() -> None:
    global webviews
    for webview in webviews:
        update_webview_css(webview)


def update_webview_css(webview: AnkiWebView) -> None:
    (light_mode_css, dark_mode_css, extra_css) = get_theme_css()
    webview.eval(
        "document.getElementById('recolor-light').innerHTML = `body { \n%s }`"
        % light_mode_css
    )
    webview.eval(
        "document.getElementById('recolor-dark').innerHTML = `body.night_mode { \n%s }`"
        % dark_mode_css
    )
    webview.eval(
        "document.getElementById('recolor-extra').innerHTML = `%s`" % extra_css
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


AnkiWebView.__init__ = wrap(AnkiWebView.__init__, on_webview_init, "before")  # type: ignore
AnkiWebView.cleanup = wrap(AnkiWebView.cleanup, on_webview_init, "before")  # type: ignore
gui_hooks.webview_will_set_content.append(inject_web)
recolor_python()
