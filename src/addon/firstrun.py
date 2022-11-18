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


# To Anki 2.1.55+ theme style
def v1_to_v2() -> None:
    conf.load()

    # Save v1 colors
    user_files_dir = Path(__file__).parent / "user_files"
    user_files_dir.mkdir(parents=False, exist_ok=True)
    v1_colors_path = user_files_dir / "v1_colors.json"
    with v1_colors_path.open("w") as f:
        v1_colors = conf.get("colors")
        json.dump(v1_colors, f, indent=2)
    # Load v2 colors
    new_colors = conf.get_default("colors")
    conf.set("colors", new_colors)
    conf.save()
    # Inform users that previous ReColor config is no longer valid
    showInfo(
        "\n".join(
            [
                "Anki v2.1.55+ has reworked the themes code, so the previous ReColor config no longer works with the new themes.",
                "ReColor config has been reset to work with the new Anki themes, and you will need to reconfigure ReColor.",
                "The previous ReColor config have been saved to the addon user_files directory, 'v1_colors.json'.",
            ]
        ),
        title="Anki Recolor Update",
    )
    """
    # old -> new
    color_map = {
        "TEXT_FG": "FG",
        "WINDOW_BG": "CANVAS",
        "FRAME_BG": "",
        "BORDER": "BORDER",
        "MEDIUM_BORDER": "",
        "FAINT_BORDER": "",
        "LINK": "FG_LINK",
        "REVIEW_COUNT": "",
        "NEW_COUNT": "",
        "LEARN_COUNT": "",
        "ZERO_COUNT": "",
        "SLIGHTLY_GREY_TEXT": "",
        "HIGHLIGHT_BG": "HIGHLIGHT_BG",
        "HIGHLIGHT_FG": "HIGHLIGHT_FG",
        "DISABLED": "",
        "FLAG1_FG": "",
        "FLAG2_FG": "",
        "FLAG3_FG": "",
        "FLAG4_FG": "",
        "FLAG5_FG": "",
        "FLAG6_FG": "",
        "FLAG7_FG": "",
        "FLAG1_BG": "",
        "FLAG2_BG": "",
        "FLAG3_BG": "",
        "FLAG4_BG": "",
        "FLAG5_BG": "",
        "FLAG6_BG": "",
        "FLAG7_BG": "",
        "BURIED_FG": "",
        "SUSPENDED_FG": "",
        "SUSPENDED_BG": "",
        "MARKED_BG": "",
        "TOOLTIP_BG": "",
        "BUTTON_BG": "",
        "CURRENT_DECK": "",
    }
    """


compat(prev_version)
save_current_version_to_conf()
