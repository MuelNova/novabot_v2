import json
from pathlib import Path

from typing import Dict

from nonebot import get_driver
from .config import Config

global_config = get_driver().config
config = Config.parse_obj(global_config)


def save(data: Dict):
    with open(config.database_path, 'w') as f:
        f.write(json.dumps(data, ensure_ascii=True, indent=2))


def read() -> Dict:
    if not Path(config.database_path).exists():
        return {}
    with open(config.database_path, 'r') as f:
        return json.loads(f.read())
