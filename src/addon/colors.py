from typing import Any, Optional

import aqt
from aqt import gui_hooks, mw

from .ankiaddonconfig import ConfigManager

conf = ConfigManager()


def file_url(file_name: str) -> str:
    addon_package = mw.addonManager.addonFromModule(__name__)
    return f"/_addons/{addon_package}/{file_name}"


def inject_js(web_content: aqt.webview.WebContent, context: Optional[Any]) -> None:
    conf.load()
    web_content.body += "<script>Recolor.withConfig('{}')</script>".format(
        conf.to_json())
    web_content.js.append(file_url("recolor.js"))


mw.addonManager.setWebExports(__name__, "recolor.js")
gui_hooks.webview_will_set_content.append(inject_js)
