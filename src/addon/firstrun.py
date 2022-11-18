import os

from aqt import mw

from .ankiaddonconfig import ConfigManager
from pathlib import Path

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
    pass
