from pathlib import Path
from typing import List, Optional
from pydantic import BaseModel, Extra


class Config(BaseModel, extra=Extra.ignore):
    custom_font_path: Optional[Path] = Path("novabot/resources/fonts")
    default_fallback_fonts: List[str] = [
        "Arial",
        "Tahoma",
        "Helvetica Neue",
        "Segoe UI",
        "PingFang SC",
        "Hiragino Sans GB",
        "Microsoft YaHei",
        "Source Han Sans SC",
        "Noto Sans SC",
        "Noto Sans CJK JP",
        "WenQuanYi Micro Hei",
        "Apple Color Emoji",
        "Noto Color Emoji",
        "Segoe UI Emoji",
        "Segoe UI Symbol",
    ]
    font_path: str = "novabot/resources/fonts"
