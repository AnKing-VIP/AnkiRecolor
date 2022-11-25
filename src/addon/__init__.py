from .ankiaddonconfig import ConfigManager
from .migrate import maybe_migrate_config

conf = ConfigManager()
maybe_migrate_config(conf)

from . import colors
from . import menu
from . import config
