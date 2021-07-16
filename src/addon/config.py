import webbrowser

from aqt import mw
from aqt.theme import theme_manager
from aqt.qt import QAction, QKeySequence, QMenu


from .ankiaddonconfig import ConfigManager, ConfigWindow
from .colors import recolor_python

conf = ConfigManager()


def on_save() -> None:
    conf.save()
    recolor_python()


def with_window(conf_window: ConfigWindow) -> None:
    conf_window.execute_on_save(on_save)


def color_idx() -> int:
    return 2 if theme_manager.night_mode else 1


def general_tab(conf_window: ConfigWindow) -> None:
    conf_keys = [
        "TEXT_FG",
        "WINDOW_BG",
        "FRAME_BG",
        "BUTTON_BG",
        "BORDER",
        "MEDIUM_BORDER",
        "FAINT_BORDER",
        "LINK",
        "SLIGHTLY_GREY_TEXT",
        "HIGHLIGHT_BG",
        "HIGHLIGHT_FG",
        "DISABLED",
        "NEW_COUNT",
        "LEARN_COUNT",
        "REVIEW_COUNT",
        "ZERO_COUNT"
    ]
    tab = conf_window.add_tab("General")
    for conf_key in conf_keys:
        description = conf.get(f"colors.{conf_key}.0")
        tab.color_input(f"colors.{conf_key}.{color_idx()}", description)
    tab.stretch()


def browse_sidebar_tab(conf_window: ConfigWindow) -> None:
    conf_keys = [
        "BURIED_FG",
        "SUSPENDED_FG",
        "FLAG1_FG",
        "FLAG2_FG",
        "FLAG3_FG",
        "FLAG4_FG",
        "FLAG5_FG",
        "FLAG6_FG",
        "FLAG7_FG",
    ]
    tab = conf_window.add_tab("Browse Sidebar")
    for conf_key in conf_keys:
        description = conf.get(f"colors.{conf_key}.0")
        tab.color_input(f"colors.{conf_key}.{color_idx()}", description)
    tab.stretch()


def browse_cards_list_tab(conf_window: ConfigWindow) -> None:
    conf_keys = [
        "SUSPENDED_BG",
        "MARKED_BG",
        "FLAG1_BG",
        "FLAG2_BG",
        "FLAG3_BG",
        "FLAG4_BG",
        "FLAG5_BG",
        "FLAG6_BG",
        "FLAG7_BG"
    ]
    tab = conf_window.add_tab("Browse Cards List")
    for conf_key in conf_keys:
        description = conf.get(f"colors.{conf_key}.0")
        tab.color_input(f"colors.{conf_key}.{color_idx()}", description)
    tab.stretch()


def getMenu(parent, menuName):
    menubar = parent.form.menubar
    for a in menubar.actions():
        if menuName == a.text():
            return a.menu()
    else:
        return menubar.addMenu(menuName)


def getSubMenu(menu, subMenuName):
    for a in menu.actions():
        if subMenuName == a.text():
            return a.menu()
    else:
        subMenu = QMenu(subMenuName, menu)
        menu.addMenu(subMenu)
        return subMenu


def setupMenu():
    MENU_OPTIONS = (  # CONF_KEY, TITLE, CALLBACK
        ("", "Online Mastery Course", openWeb1),
        ("", "Daily Q and A Support", openWeb2),
        ("", "1-on-1 Tutoring", openWeb3)
    )
    menu_name = "&AnKing"
    menu = getMenu(mw, menu_name)
    submenu = getSubMenu(menu, "Get Anki Help")
    for k, t, cb in MENU_OPTIONS:
        hk = QKeySequence()
        act = QAction(t, mw)
        act.setShortcut(QKeySequence(hk))
        act.triggered.connect(cb)
        submenu.addAction(act)
        # menuItem[k]=act
    a = QAction("Recolor", mw)
    a.triggered.connect(conf.open_config)
    menu.addAction(a)


def openWeb1():
    webbrowser.open(
        'https://courses.ankipalace.com/?utm_source=anking_bg_add-on&utm_medium=anki_add-on&utm_campaign=mastery_course')


def openWeb2():
    webbrowser.open('https://www.ankipalace.com/memberships')


def openWeb3():
    webbrowser.open('https://www.ankipalace.com/tutoring')


setupMenu()


conf.use_custom_window()
conf.on_window_open(with_window)
conf.add_config_tab(general_tab)
conf.add_config_tab(browse_sidebar_tab)
conf.add_config_tab(browse_cards_list_tab)
