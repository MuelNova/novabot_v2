from pydantic import BaseSettings, Extra
from pathlib import Path


class Config(BaseSettings, extra=Extra.ignore):
    # Your Config Here
    data_path: Path = Path.cwd() / "data" / "video_to_video"
