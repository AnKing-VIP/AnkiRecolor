import re
import sys
import simplejson
from pathlib import Path

version_string = sys.argv[1]
assert re.match(r"^(\d+).(\d+)$", version_string)

addon_dir = Path(__file__).resolve().parents[1] / "src" / "addon"

# Write version in manifest.json
json_path = addon_dir / "manifest.json"
with json_path.open("r") as f:
    manifest = simplejson.load(f)

with json_path.open("w") as f:
    manifest["human_version"] = version_string
    simplejson.dump(manifest, f, indent=2)

# human_version is only updated on install.
# For developing purposes, use VERSION file to check current version
version_path = addon_dir / "VERSION"
version_path.write_text(version_string)
