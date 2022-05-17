import json
from pathlib import Path
from typing import Union, Dict

from nonebot import logger


def _load_file(path: Union[str, Path]) -> str:
    if isinstance(path, str):
        path = Path(path)
    if not path.exists():
        return ""
    try:
        with open(path, encoding='UTF-8') as f:
            file = f.read()
            return file
    except Exception as e:
        logger.error(e)
        return ""


def _save_file(path: Union[str, Path], content: Union[str, Dict], make_dir: bool = True, **kwargs):
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
