import colors
import json
from pathlib import Path

names = [item for item in dir(colors) if not item.startswith("__")]
config = {}
for name in names:
    color = getattr(colors, name)
    css_name = "--" + name.lower().replace("_", "-")
    display_name = " ".join(map(lambda n: n[0] + n[1:].lower(), name.split("_")))
    config[name] = [
        display_name,
        color["light"],
        color["dark"],
        css_name,
        color["comment"],
    ]

config_file_path = Path(__file__).parent / "colors.json"
with open(config_file_path, "w") as f:
    json.dump(config, f)
print("saved to colors.json")
