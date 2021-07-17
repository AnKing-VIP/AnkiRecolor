from typing import Any, Optional

from anki import version as ankiversion
from anki.utils import isWin, isMac

import aqt
from aqt.webview import AnkiWebView
from aqt import gui_hooks, mw, dialogs
from aqt.theme import theme_manager, colors
from aqt.qt import QColor, QPalette, Qt

from .ankiaddonconfig import ConfigManager

ankiver_minor = int(ankiversion.split(".")[2])
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
        if getattr(colors, color_name, None) is not None:
            color_entry = color_entries[color_name]
            new_color_value = (color_entry[1], color_entry[2])
            setattr(colors, color_name, new_color_value)
    apply_palette()
    theme_manager._apply_style(mw.app)
    replace_webview_bg()
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

    hlbg = qcolor("HIGHLIGHT_BG")
    if theme_manager.night_mode:
        hlbg.setAlpha(64)
    palette.setColor(QPalette.Highlight, hlbg)

    for role in disabled_roles:
        palette.setColor(
            QPalette.Disabled, role, qcolor("DISABLED"))

    if theme_manager.night_mode:
        palette.setColor(QPalette.BrightText, Qt.red)

    mw.app.setPalette(palette)
    # webview palette uses default one
    theme_manager.default_palette = palette  # type: ignore


def get_window_bg_color(*args: Any) -> QColor:
    color_idx = 2 if theme_manager.night_mode else 1
    hex_color = conf.get(f"colors.WINDOW_BG.{color_idx}")
    return QColor(hex_color)


def replace_webview_bg() -> None:
    if 26 <= ankiver_minor <= 44:
        AnkiWebView._getWindowColor = get_window_bg_color  # type: ignore
    elif 45 <= ankiver_minor:
        AnkiWebView.get_window_bg_color = get_window_bg_color  # type: ignore


# Recolor CSS Colors

def file_url(file_name: str) -> str:
    addon_package = mw.addonManager.addonFromModule(__name__)
    return f"/_addons/{addon_package}/{file_name}"


def wrap_style(code: str) -> str:
    return f"<style>{code}</style>"


def inject_web(web_content: aqt.webview.WebContent, context: Optional[Any]) -> None:
    conf.load()
    night_mode = theme_manager.night_mode
    color_idx = 2 if night_mode else 1
    web_content.body += "<script>Recolor.withConfig('{}', {})</script>".format(
        conf.to_json(), color_idx
    )
    web_content.body += "<style>.current{ background-color: var(--current-deck); }</style>"
    web_content.js.append(file_url("recolor.js"))

    # Override night mode button color
    btn_bg_night = conf.get("colors.BUTTON_BG.2")
    extra_style = ""
    if night_mode:  # Created to look good enough
        if conf.get_default("colors.BUTTON_BG.2") != btn_bg_night:
            extra_style += """
                .night_mode button {
                    background: %(btn_bg)s;
                    border: none; 
                }
                .night_mode button:hover {
                    background: %(btn_bg)s;
                    filter: brightness(1.25);
                }
            """ % {
                "btn_bg": btn_bg_night
            }
    else:  # Because v2.1.44- uses QPalette default color
        if isWin:
            extra_style += """
                button:focus {
                    outline: 1px solid %s
                }
            """ % conf.get("colors.HIGHLIGHT_BG.1")
        elif isMac:
            extra_style += """
                button {
                    background: %(btn_bg)s;
                }
            """ % {"btn_bg": conf.get("colors.BUTTON_BG.1")}
        else:
            extra_style += """
                    button {
                        background-color: %(btn_bg)s;
                    }
                    button:active, button:active:hover { 
                        background-color: %(color_hl)s; 
                        color: %(color_hl_txt)s;
                    }
                    btn:focus { border-color: %(color_hl)s }
                    textarea:focus, input:focus, input[type]:focus, 
                    .uneditable-input:focus, div[contenteditable="true"]:focus {   
                        border-color: %(color_hl)s;
                    }
            """ % {
                "btn_bg": conf.get("colors.BUTTON_BG.1"),
                "color_hl": conf.get("colors.HIGHLIGHT_BG.1"),
                "color_hl_txt": conf.get("colors.HIGHLIGHT_FG.1"),
            }

    web_content.body += wrap_style(extra_style)


mw.addonManager.setWebExports(__name__, "recolor.js")
gui_hooks.webview_will_set_content.append(inject_web)
recolor_python()
