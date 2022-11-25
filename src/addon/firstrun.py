import os
import json
from pathlib import Path

from aqt import mw
from aqt.utils import showInfo

from .ankiaddonconfig import ConfigManager


conf = ConfigManager()


class Version:
    def __init__(self) -> None:
        self.load()

    def load(self) -> None:
        self.major = conf["version.major"]
        self.minor = conf["version.minor"]

    def __eq__(self, other: str) -> bool:  # type: ignore
        ver = [int(i) for i in other.split(".")]
        return self.major == ver[0] and self.minor == ver[1]

    def __gt__(self, other: str) -> bool:
        ver = [int(i) for i in other.split(".")]
        return self.major > ver[0] or (self.major == ver[0] and self.minor > ver[1])

    def __lt__(self, other: str) -> bool:
        ver = [int(i) for i in other.split(".")]
        return self.major < ver[0] or (self.major == ver[0] and self.minor < ver[1])

    def __ge__(self, other: str) -> bool:
        return self == other or self > other

    def __le__(self, other: str) -> bool:
        return self == other or self < other


prev_version = Version()


def save_current_version_to_conf() -> None:
    version_string = os.environ.get("ANKIRECOLOR_VERSION")
    if not version_string:
        version_file = Path(__file__).parent / "VERSION"
        version_string = version_file.read_text()
    if version_string != prev_version:
        conf["version.major"] = int(version_string.split(".")[0])
        conf["version.minor"] = int(version_string.split(".")[1])
        conf.save()


def compat(prev_version: Version) -> None:
    if prev_version == "-1.-1":
        return
    elif prev_version < "2.0":
        v1_to_v2()


#
COLOR_MAP = {
    "TEXT_FG": "FG",
    "WINDOW_BG": "CANVAS",
    "FRAME_BG": "CANVAS_INSET",  # Also CANVAS_OVERLAY
    "BORDER": "BORDER",
    "MEDIUM_BORDER": "",
    "FAINT_BORDER": "BORDER_SUBTLE",
    "LINK": "FG_LINK",
    "REVIEW_COUNT": "STATE_REVIEW",
    "NEW_COUNT": "STATE_NEW",
    "LEARN_COUNT": "STATE_LEARN",
    "ZERO_COUNT": "FG_FAINT",
    "SLIGHTLY_GREY_TEXT": "FG_SUBTLE",
    "HIGHLIGHT_BG": "HIGHLIGHT_BG",
    "HIGHLIGHT_FG": "HIGHLIGHT_FG",
    "DISABLED": "FG_DISABLED",
    "FLAG1_FG": "FLAG_1",
    "FLAG2_FG": "FLAG_2",
    "FLAG3_FG": "FLAG_3",
    "FLAG4_FG": "FLAG_4",
    "FLAG5_FG": "FLAG_5",
    "FLAG6_FG": "FLAG_6",
    "FLAG7_FG": "FLAG_7",
    "FLAG1_BG": "",
    "FLAG2_BG": "",
    "FLAG3_BG": "",
    "FLAG4_BG": "",
    "FLAG5_BG": "",
    "FLAG6_BG": "",
    "FLAG7_BG": "",
    "BURIED_FG": "",
    "SUSPENDED_FG": "STATE_SUSPENDED",
    "SUSPENDED_BG": "",
    "MARKED_BG": "STATE_MARKED",
    "TOOLTIP_BG": "CANVAS_OVERLAY",
    "BUTTON_BG": "BUTTON_BG",
    "CURRENT_DECK": "",
}


# To Anki 2.1.55+ theme style
def v1_to_v2() -> None:
    conf.load()

    # Load and save v1 colors
    user_files_dir = Path(__file__).parent / "user_files"
    user_files_dir.mkdir(parents=False, exist_ok=True)
    v1_colors_path = user_files_dir / "v1_config.json"
    v1_colors_path.write_text(json.dumps(conf.get(""), indent=2))
    v1_colors = conf.get("colors")
    v1_anki_colors_path = Path(__file__).parent / "v1_anki_config.json"
    v1_anki_colors = json.loads(v1_anki_colors_path.read_text())["colors"]

    # Load v2 vinally anki colors
    v2_colors = conf.get_default("colors")
    new_colors = conf.get_default("colors")

    # old -> new for colors not identical to vanilla anki
    for old_name in COLOR_MAP:
        new_name = COLOR_MAP[old_name]
        if new_name:
            if v1_colors[old_name][1] != v1_anki_colors[old_name][1]:
                new_colors[new_name][1] = v1_colors[old_name][1]
            if v1_colors[old_name][2] != v1_anki_colors[old_name][2]:
                new_colors[new_name][2] = v1_colors[old_name][2]

    if new_colors["CANVAS"][1] != v2_colors["CANVAS"][1]:
        new_colors["CANVAS_OVERLAY"][1] = new_colors["CANVAS"][1]
    if new_colors["CANVAS"][2] != v2_colors["CANVAS"][2]:
        new_colors["CANVAS_OVERLAY"][2] = new_colors["CANVAS"][2]
    new_colors["BUTTON_HOVER"][1:3] = new_colors["CANVAS_INSET"][1:3]

    conf.set("colors", new_colors)
    conf.save()

    # Inform users that previous ReColor config is no longer valid
    showInfo(
        "\n".join(
            [
                "Anki v2.1.55+ has reworked the themes code, so the previous ReColor config no longer works with the new themes.",
                "Your previous ReColor theme has been moved over to the new config as best as possible, but things may look different.",
                "Your previous ReColor config have been saved to the addon user_files directory, 'v1_config.json'.",
            ]
        ),
        title="Anki Recolor Update",
    )


compat(prev_version)
save_current_version_to_conf()
