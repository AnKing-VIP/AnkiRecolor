from pathlib import Path
import json
import os

from aqt.utils import showInfo

from .ankiaddonconfig import ConfigManager, Version


def maybe_migrate_config(conf: ConfigManager) -> None:
    version = Version(conf["version.major"], conf["version.minor"])
    version_string = get_new_version_string()
    if version == "-1.-1":
        if detect_v2(conf):
            v2_to_v3(conf)
    elif version < "2.0":
        maybe_v1_to_v2(conf)
        v2_to_v3(conf)
    elif version < "3.0":
        v2_to_v3(conf)

    if version != version_string:
        conf["version.major"] = int(version_string.split(".")[0])
        conf["version.minor"] = int(version_string.split(".")[1])
        conf.save()

# some versions of v2 may be incorrectly in -1.-1
def detect_v2(conf: ConfigManager) -> bool:
    return "CANVAS_GLASS" not in conf["colors"] and "CANVAS" in conf["colors"]


def get_new_version_string() -> str:
    version_string = os.environ.get("ANKIRECOLOR_VERSION")
    if not version_string:
        version_file = Path(__file__).parent / "VERSION"
        version_string = version_file.read_text()
    return version_string


# To Anki 2.1.55+ theme style
def maybe_v1_to_v2(conf: ConfigManager) -> None:
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

    # old -> new for colors not identical to vanilla anki
    for old_name in COLOR_MAP:
        new_name = COLOR_MAP[old_name]
        if new_name:
            if v1_colors[old_name][1] != v1_anki_colors[old_name][1]:
                new_colors[new_name][1] = v1_colors[old_name][1]
            if v1_colors[old_name][2] != v1_anki_colors[old_name][2]:
                new_colors[new_name][2] = v1_colors[old_name][2]

    # Copy over color to another if changed
    V2_ALIAS_MAP = {
        "CANVAS_OVERLAY": "CANVAS",
        "CANVAS_ELEVATED": "CANVAS_INSET",
        "BUTTON_HOVER": "CANVAS_INSET",
    }

    for alias in V2_ALIAS_MAP:
        orig = V2_ALIAS_MAP[alias]
        if new_colors[orig][1] != v2_colors[orig][1]:
            new_colors[alias][1] = new_colors[orig][1]
        if new_colors[orig][2] != v2_colors[orig][2]:
            new_colors[alias][2] = new_colors[orig][2]
    # Only for light mode
    if new_colors["CANVAS_INSET"][1] != v2_colors["CANVAS_INSET"][1]:
        new_colors["CANVAS_CODE"][1] = v2_colors["CANVAS_INSET"][1]

    # Make sure button hover is different from button bg for top bar buttons
    if new_colors["BUTTON_HOVER"][1] == new_colors["BUTTON_BG"][1]:
        new_colors["BUTTON_HOVER"][1] = darken(new_colors["BUTTON_HOVER"][1], 5)
    if new_colors["BUTTON_HOVER"][2] == new_colors["BUTTON_BG"][2]:
        new_colors["BUTTON_HOVER"][2] = darken(new_colors["BUTTON_HOVER"][2], 5)

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


# if by is negative, lightens color
def darken(hex: str, by: int) -> str:
    r = int(hex[1:3], 16)
    g = int(hex[3:5], 16)
    b = int(hex[5:7], 16)
    r = r + by
    g = g + by
    b = b + by
    r = max(0, min(16 ** 2 - 1, r))
    g = max(0, min(16 ** 2 - 1, g))
    b = max(0, min(16 ** 2 - 1, b))
    new_r = "%0.2X" % r
    return "%s%0.2X%0.2X%0.2X%s" % (hex[0], r, g, b, hex[7:])


def adjust_alpha(color: str, by: float) -> str:
    alpha = 255
    if color.startswith("#"):
        if len(color) == 9:
            alpha = int(color[8:10], 16)
            body = color[0:8]
        elif len(color) == 7:
            body = color
        elif len(color) == 4:
            body = f"#{color[0]*2}{color[1]*2}{color[2]*2}"
    elif color.startswith("rgba"):
        [r, g, b, a] = map(int, color.split(")")[0].split(","))
        alpha = a
        body = f"#{r:02X}{g:02X}{b:02X}"
    elif color == "white":
        body = "#ffffff"
    elif color == "black":
        body = "#000000"
    else:
        # probably some other keyword-named color that is difficult to adjust alpha
        return color

    alpha = int(alpha * by)
    return f"{body}{alpha:02X}"


def v2_to_v3(conf: ConfigManager) -> None:
    conf.load()
    colors = conf.get("colors")

    # add canvas-glass
    elevated = colors["CANVAS_ELEVATED"]
    colors["CANVAS_GLASS"] = [
        "Background (transparent text surface)",
        adjust_alpha(elevated[1], 0.4),
        adjust_alpha(elevated[2], 0.4),
        "--canvas-glass",
    ]

    canvas = colors["CANVAS"]
    if not isinstance(canvas[3], list):
        canvas[3] = [canvas[3]]
    canvas[3].append("--bs-body-bg")

    fg = colors["FG"]
    if not isinstance(fg[3], list):
        fg[3] = [fg[3]]
    fg[3].append("--bs-body-color")

    conf.set("colors", colors)
    conf.save()


# for Anki v2.66+
def adjust_colors_v3(colors: dict) -> None:
    # add canvas-glass
    elevated = colors["CANVAS_ELEVATED"]
    colors["CANVAS_GLASS"] = [
        "Background (transparent text surface)",
        adjust_alpha(elevated[1], 0.4),
        adjust_alpha(elevated[2], 0.4),
        "--canvas-glass",
    ]

    canvas = colors["CANVAS"]
    if not isinstance(canvas[3], list):
        canvas[3] = [canvas[3]]
    canvas[3].append("--bs-body-bg")

    fg = colors["FG"]
    if not isinstance(fg[3], list):
        fg[3] = [fg[3]]
    fg[3].append("--bs-body-color")
