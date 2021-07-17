import webbrowser
from typing import Optional

from aqt import mw
from aqt.theme import theme_manager
from aqt.qt import *


from .ankiaddonconfig import ConfigManager, ConfigWindow
from .colors import recolor_python

conf = ConfigManager()


def header_layout(conf_window: ConfigWindow) -> QHBoxLayout:
    icons_layout = QHBoxLayout()
    icons_layout.addStretch()
    images = [
        ("AnKingSmall.png", (31, 31), "www.ankingmed.com"),
        ("YouTube.png", (31, 31), "www.youtube.com/theanking"),
        ("Patreon.png", (221, 31), "www.patreon.com/ankingmed"),
        ("Instagram.png", (31, 31), "instagram.com/ankingmed"),
        ("Facebook.png", (31, 31), "facebook.com/ankingmed")
    ]
    for image in images:
        icon = QIcon()
        icon.addPixmap(
            QPixmap(f":/Recolor/{image[0]}"), QIcon.Normal, QIcon.Off)
        button = QToolButton(conf_window)
        button.setIcon(icon)
        button.setIconSize(QSize(*image[1]))
        button.setMaximumSize(QSize(*image[1]))
        button.setMinimumSize(QSize(*image[1]))
        button.clicked.connect(lambda _: open_web(image[2]))
        button.setCursor(QCursor(Qt.PointingHandCursor))
        button.setStyleSheet(
            "QToolButton { border: none; }")
        icons_layout.addWidget(button)
    icons_layout.addStretch()
    return icons_layout


def on_save() -> None:
    conf.save()
    recolor_python()


def with_window(conf_window: ConfigWindow) -> None:
    conf_window.setWindowTitle("Recolor Settings")
    conf_window.execute_on_save(on_save)
    conf_window.main_layout.insertLayout(0, header_layout(conf_window))
    conf_window.main_layout.insertSpacing(1, 10)


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
        "SLIGHTLY_GREY_TEXT",
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


def getMenu(parent: QWidget, menuName: str) -> QMenu:
    menubar = parent.form.menubar
    for a in menubar.actions():
        if menuName == a.text():
            return a.menu()
    else:
        return menubar.addMenu(menuName)


def create_sub_menu_if_not_exist(menu, subMenuName) -> Optional[QMenu]:
    for a in menu.actions():
        if subMenuName == a.text():
            return None
    else:
        subMenu = QMenu(subMenuName, menu)
        menu.addMenu(subMenu)
        return subMenu


def setupMenu() -> None:
    MENU_OPTIONS = [
        ("Online Mastery Course",
         "courses.ankipalace.com/?utm_source=anking_bg_add-on&utm_medium=anki_add-on&utm_campaign=mastery_course"),
        ("Daily Q and A Support", "www.ankipalace.com/memberships"),
        ("1-on-1 Tutoring", "www.ankipalace.com/tutoring")
    ]
    menu_name = "&AnKing"
    menu = getMenu(mw, menu_name)
    submenu = create_sub_menu_if_not_exist(menu, "Get Anki Help")
    if submenu:
        for t, url in MENU_OPTIONS:
            act = QAction(t, mw)
            act.triggered.connect(lambda _: open_web(url))
            submenu.addAction(act)
    a = QAction("Recolor", mw)
    a.triggered.connect(conf.open_config)
    menu.addAction(a)


def open_web(url: str) -> None:
    webbrowser.open(f"https://{url}")


setupMenu()

conf.use_custom_window()
conf.on_window_open(with_window)
conf.add_config_tab(general_tab)
conf.add_config_tab(browse_sidebar_tab)
conf.add_config_tab(browse_cards_list_tab)
