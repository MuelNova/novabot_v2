import json
from pathlib import Path
from typing import Union, Dict

from nonebot import logger, get_driver, get_bot
from nonebot.adapters.onebot.v11 import Bot

driver = get_driver()


def load_file(path: Union[str, Path]) -> str:
    if isinstance(path, str):
        path = Path(path)
    if not path.exists():
        return ""
    try:
        with open(path, encoding='UTF-8') as f:
            return f.read()
    except Exception as e:
        logger.error(e)
        return ""


def save_file(path: Union[str, Path], content: Union[str, Dict], make_dir: bool = True, **kwargs):
    if isinstance(path, str):
        path = Path(path)
    try:
        if not path.parent.exists():
            if make_dir:
                path.parent.mkdir(parents=True)
            else:
                raise FileNotFoundError(f"Can't create the file at {path.parent} as `make_dir` is disabled.")
        with open(path, encoding='UTF-8', mode='w') as f:
            if isinstance(content, Dict):
                if not kwargs:
                    json.dump(content, f, ensure_ascii=False, indent=2)
                else:
                    json.dump(content, f, **kwargs)
            else:
                f.write(content)
    except Exception as e:
        logger.error(e)


def get_nickname() -> str:
    return sorted(list(driver.config.nickname))[-1] or '鴎'


async def is_admin(user_id: int, group_id: int, bot: Bot = None) -> bool:
    if not bot:
        bot = get_bot()
    role = (await bot.call_api("get_group_member_info", group_id=group_id, user_id=user_id)).get('role')
    return role in ['admin', 'owner'] or str(user_id) in driver.config.superusers
