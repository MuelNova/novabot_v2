from pathlib import Path
from random import choice

from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from typing import Optional, Union, Any

from ..config import RESOURCE_PATH


class ImageUtils:
    width: int
    height: int
    background: Optional[bytes]
    background_opacity: float
    background_width: int
    background_height: int
    font: ImageFont
    image_mode: str

    def __init__(self,
                 width: Optional[int] = 400,
                 height: Optional[int] = 400,
                 background: Optional[Union[str, Path, BytesIO]] = None,
                 background_opacity: Optional[float] = 0.7,
                 background_width: Optional[int] = None,
                 background_height: Optional[int] = None,
                 font: Optional[Union[str, Path]] = None,
                 font_size: Optional[int] = 10,
                 image_mode: Optional[str] = 'rgba',
                 **kwargs: Optional[Any]):
        """

        :param width:
        :param height:
        :param background:
        :param background_opacity:
        :param background_width:
        :param background_height:
        :param font:
        :param font_size:
        :param image_mode:
        :param kwargs:
        """

        self.width = width
        self.height = height
        self.image_mode = image_mode

        # Background
        if isinstance(background, str) and background.lower() == 'none':
            self.background = None
        elif background is None:
            self.background = ImageUtils.get_random_background()
        elif isinstance(background, BytesIO):
            self.background = background.getvalue()
        else:
            if isinstance(background, str):
                background = Path(background)
            if not background.exists():
                raise FileNotFoundError("Can't find the specific background file.")
            self.background = open(background, 'rb').read()

        self.background_height = height if background_height is None else background_height
        self.background_width = width if background_width is None else background_width
        self.background_opacity = background_opacity

        # font
        if isinstance(font, Path):
            font = str(Path)
        self.image_font = ImageFont.truetype(font, font_size)

    @staticmethod
    def get_random_background():
        path = Path(RESOURCE_PATH) / 'background'

        if not path.is_absolute():
            path = Path.cwd() / path
        if not path.exists():
            path.mkdir(parents=True)
        backgrounds = list(path.iterdir())
        if not backgrounds:
            raise FileNotFoundError(f"No Background Found in '{path}/', please check the config!")
        return open(choice(backgrounds), 'rb').read()

