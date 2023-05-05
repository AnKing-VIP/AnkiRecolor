from aqt import mw
from aqt.utils import openLink
from aqt.qt import QMenu, QAction

from .config import conf


def create_get_help_submenu(parent: QMenu) -> QMenu:
    submenu_name = "Get Anki Help"
    menu_options = [
        (
            "Online Mastery Course",
            "https://www.theanking.com/anki-mastery-course/?utm_source=recolor_addon&utm_medium=anki_add-on&utm_campaign=mastery_course",
        ),
        ("Daily Q and A Support", "https://www.theanking.com/anking-memberships"),
        ("1-on-1 Tutoring", "https://www.theanking.com/anking-tutoring"),
    ]
    submenu = QMenu(submenu_name, parent)
    for name, url in menu_options:
        act = QAction(name, mw)
        act.triggered.connect(lambda _, u=url: openLink(u))
        submenu.addAction(act)
    return submenu


def maybe_add_get_help_submenu(menu: QMenu) -> None:
    """Adds 'Get Anki Help' submenu in 'Anking' menu if needed.

    The submenu is added if:
     - The submenu does not exist in menu
     - The submenu is an outdated version - existing is deleted

    With versioning and anking_get_help property,
    future version can rename, hide, or change contents in the submenu
    """
    submenu_property = "anking_get_help"
    submenu_ver = 2
    for act in menu.actions():
        if act.property(submenu_property) or act.text() == "Get Anki Help":
            ver = act.property("version")
            if ver and ver >= submenu_ver:
                return
            submenu = create_get_help_submenu(menu)
            menu.insertMenu(act, submenu)
            menu.removeAction(act)
            new_act = submenu.menuAction()
            new_act.setProperty(submenu_property, True)
            new_act.setProperty("version", submenu_ver)
            return
    else:
        submenu = create_get_help_submenu(menu)
        menu.addMenu(submenu)
        new_act = submenu.menuAction()
        new_act.setProperty(submenu_property, True)
        new_act.setProperty("version", submenu_ver)


def get_anking_menu() -> QMenu:
    """Return AnKing menu. If it doesn't exist, create one. Make sure its submenus are up to date."""
    menu_name = "&AnKing"
    menubar = mw.form.menubar
    for a in menubar.actions():
        if menu_name == a.text():
            menu = a.parent()
            break
    else:
        menu = menubar.addMenu(menu_name)
    maybe_add_get_help_submenu(menu)
    return menu


########################################


def setupMenu() -> None:
    menu = get_anking_menu()
    a = QAction("ReColor", menu)
    a.triggered.connect(conf.open_config)
    menu.addAction(a)


setupMenu()
