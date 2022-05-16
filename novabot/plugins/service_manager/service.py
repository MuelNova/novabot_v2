import json
from pathlib import Path
from typing import Type, Dict, Any

from nonebot.internal.matcher import Matcher, MatcherMeta

from ...utils import _load_file


class Service:
    def __init__(self, plugin_name: str, matcher: Type[Matcher]):
        if not isinstance(matcher, MatcherMeta):
            raise TypeError(f"matcher excepted yet {type(matcher)} found.")
        self.plugin_name = plugin_name
        self.matcher = matcher

    def __repr__(self):
        return f"<Service '{self.matcher.plugin_name}'>"

    def __getattr__(self, item):
        return getattr(self.matcher, item)

    def _load_config(self) -> Dict[str, Any]:
        path = Path.cwd() / "novabot" / "plugin_config" / "service_manager" / f"{self.plugin_name}.json"
        if not path.parent.exists():
            path.parent.mkdir(parents=True)
        return json.loads(_load_file(path))

    def _save_config(self):
        path = Path.cwd() / "novabot" / "plugin_config" / "service_manager" / f"{self.plugin_name}.json"
        if not path.parent.exists():
            path.parent.mkdir(parents=True)
        ...  # To-Do: Save plugin config
