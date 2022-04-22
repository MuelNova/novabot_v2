from pydantic import BaseSettings, Extra
from pathlib import Path


class Config(BaseSettings, extra=Extra.ignore):
    # Your Config Here
    data_path: Path = Path.cwd() / "data" / "group_manager"
    database_path: Path = data_path / "group.json"
