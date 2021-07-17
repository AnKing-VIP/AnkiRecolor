# Save current version
from aqt import mw

from .ankiaddonconfig import ConfigManager


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


version = Version()
conf = ConfigManager()


addon_dir = mw.addonManager.addonFromModule(__name__)
meta = mw.addonManager.addonMeta(addon_dir)

version_string = meta["human_version"]
conf["version.major"] = int(version_string.split(".")[0])
conf["version.minor"] = int(version_string.split(".")[1])
conf.save()
