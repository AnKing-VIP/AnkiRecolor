from typing import Any, Optional

from anki.utils import isWin, isMac, pointVersion
from anki.hooks import wrap

import aqt
from aqt.webview import AnkiWebView
from aqt import gui_hooks, mw, dialogs
from aqt.theme import theme_manager, colors
from aqt.qt import QColor, QPalette, Qt, QDialog

from .ankiaddonconfig import ConfigManager

ankiver_minor = pointVersion()
conf = ConfigManager()


# ReColor Python Colors


def refresh_all_windows() -> None:
    # Redraw top toolbar
    mw.toolbar.draw()
    # Redraw main body
    if mw.state == "review":
        mw.reviewer._initWeb()
        if mw.reviewer.state == "question":
            mw.reviewer._showQuestion()
        else:
            mw.reviewer._showAnswer()
    elif mw.state == "overview":
        mw.overview.refresh()
    elif mw.state == "deckBrowser":
        mw.deckBrowser.refresh()
    # Close Browser if open
    browser = dialogs._dialogs["Browser"][1]
    if browser:
        browser.closeWithCallback(lambda: None)
    if ankiver_minor >= 45:  # has mw.flags
        if mw.col is not None:
            mw.flags._load_flags()


def rgba_to_argb(rgba: str) -> None:
    if len(rgba) == 9:
        return "#" + rgba[7:] + rgba[1:7]
    else:
        return rgba


def recolor_python() -> None:
    conf.load()
    color_entries = conf.get("colors")
    for color_name in color_entries:
        if getattr(colors, color_name, None) is not None:
            color_entry = color_entries[color_name]
            new_color_value = (
                rgba_to_argb(color_entry[1]),
                rgba_to_argb(color_entry[2]),
            )
            setattr(colors, color_name, new_color_value)
    apply_palette()
    theme_manager._apply_style(mw.app)
    replace_webview_bg()
    refresh_all_windows()
    change_dialog_opacity(qcolor("WINDOW_BG").alpha() / 255)


def qcolor(conf_key: str) -> QColor:
    color_idx = 2 if theme_manager.night_mode else 1
    hex_color = conf.get(f"colors.{conf_key}.{color_idx}")
    hex_color = rgba_to_argb(hex_color)
    return QColor(hex_color)


def apply_palette() -> None:
    # theme_manager._apply_palette() can only be run in night mode
    color_map = {
        QPalette.ColorRole.WindowText: "TEXT_FG",
        QPalette.ColorRole.ToolTipText: "TEXT_FG",
        QPalette.ColorRole.Text: "TEXT_FG",
        QPalette.ColorRole.ButtonText: "TEXT_FG",
        QPalette.ColorRole.HighlightedText: "HIGHLIGHT_FG",
        QPalette.ColorRole.Window: "WINDOW_BG",
        QPalette.ColorRole.AlternateBase: "WINDOW_BG",
        QPalette.ColorRole.Button: "BUTTON_BG",
        QPalette.ColorRole.Base: "FRAME_BG",
        QPalette.ColorRole.ToolTipBase: "FRAME_BG",
        QPalette.ColorRole.Link: "LINK",
    }
    disabled_roles = [
        QPalette.ColorRole.Text,
        QPalette.ColorRole.ButtonText,
        QPalette.ColorRole.HighlightedText,
    ]

    palette = QPalette()

    for role in color_map:
        conf_key = color_map[role]
        palette.setColor(role, qcolor(conf_key))

    hlbg = qcolor("HIGHLIGHT_BG")
    if theme_manager.night_mode:
        hlbg.setAlpha(64)
    palette.setColor(QPalette.ColorRole.Highlight, hlbg)

    for role in disabled_roles:
        palette.setColor(QPalette.ColorGroup.Disabled, role, qcolor("DISABLED"))

    if theme_manager.night_mode:
        palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)

    mw.app.setPalette(palette)
    # webview palette uses default one
    theme_manager.default_palette = palette  # type: ignore


def get_window_bg_color(*args: Any) -> QColor:
    return qcolor("WINDOW_BG")


def replace_webview_bg() -> None:
    if 26 <= ankiver_minor <= 44:
        AnkiWebView._getWindowColor = get_window_bg_color  # type: ignore
    elif 45 <= ankiver_minor:
        AnkiWebView.get_window_bg_color = get_window_bg_color  # type: ignore


def change_dialog_opacity(opacity: float) -> None:
    for name in dialogs._dialogs:
        dialog = dialogs._dialogs[name]
        if dialog[1]:
            dialog[1].setWindowOpacity(opacity)
    mw.setWindowOpacity(opacity)


# ReColor CSS Colors


def file_url(file_name: str) -> str:
    addon_package = mw.addonManager.addonFromModule(__name__)
    return f"/_addons/{addon_package}/{file_name}"


def wrap_style(code: str) -> str:
    return f"<style>{code}</style>"


def inject_web(web_content: aqt.webview.WebContent, context: Optional[Any]) -> None:
    conf.load()
    night_mode = theme_manager.night_mode
    color_idx = 2 if night_mode else 1
    web_content.body += "<script>ReColor.withConfig('{}', {})</script>".format(
        conf.to_json(), color_idx
    )
    web_content.body += (
        "<style>.current{ background-color: var(--current-deck); }</style>"
    )
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
            """ % conf.get(
                "colors.HIGHLIGHT_BG.1"
            )
        elif isMac:
            extra_style += """
                button {
                    background: %(btn_bg)s;
                }
            """ % {
                "btn_bg": conf.get("colors.BUTTON_BG.1")
            }
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


def on_new_qdialog(self: QDialog, *args, **kwargs):
    self.setWindowOpacity(qcolor("WINDOW_BG").alpha() / 255)


mw.addonManager.setWebExports(__name__, "recolor.js")
gui_hooks.webview_will_set_content.append(inject_web)
recolor_python()

QDialog.__init__ = wrap(QDialog.__init__, on_new_qdialog)
