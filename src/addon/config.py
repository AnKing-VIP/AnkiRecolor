from .ankiaddonconfig import ConfigManager, ConfigWindow
from .colors import recolor_python

conf = ConfigManager()


def on_save() -> None:
    conf.save()
    recolor_python()


def with_window(conf_window: ConfigWindow) -> None:
    conf_window.execute_on_save(on_save)


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
        tab.color_input(f"colors.{conf_key}.1", description)
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
        tab.color_input(f"colors.{conf_key}.1", description)
    tab.stretch()


def browse_cards_list_tab(conf_window: ConfigWindow) -> None:
    conf_keys = [
        "FLAG1_BG",
        "FLAG2_BG",
        "FLAG3_BG",
        "FLAG4_BG",
        "FLAG5_BG",
        "FLAG6_BG",
        "FLAG7_BG",
        "SUSPENDED_BG",
        "MARKED_BG",
    ]
    tab = conf_window.add_tab("Browse Cards List")
    for conf_key in conf_keys:
        description = conf.get(f"colors.{conf_key}.0")
        tab.color_input(f"colors.{conf_key}.1", description)
    tab.stretch()


conf.use_custom_window()
conf.on_window_open(with_window)
conf.add_config_tab(general_tab)
conf.add_config_tab(browse_sidebar_tab)
conf.add_config_tab(browse_cards_list_tab)
