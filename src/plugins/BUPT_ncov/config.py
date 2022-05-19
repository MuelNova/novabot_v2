from pathlib import Path

from pydantic import BaseModel, Extra


class Config(BaseModel, extra=Extra.ignore):
    data_path: Path = Path.cwd() / "data" / "bupt_ncov"
    database_path: Path = data_path / "data.sql"
    secret_path: Path = data_path / "secret"
    salt_path: Path = data_path / "salt"
    api_timeout: int = 20  # in seconds
