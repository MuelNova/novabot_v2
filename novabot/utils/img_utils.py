from io import BytesIO
from pathlib import Path
from random import choice
from typing import Optional, Union, Any, Literal

from PIL import ImageFont, Image, ImageFilter

from config import RESOURCE_PATH


class ImageUtils:
    width: int
    height: int
    background: Optional[Image.Image]
    background_GAUSEBLUR_radius: int
    background_width: int
    background_height: int
    font: ImageFont
    image_mode: Optional[Literal["1", "CMYK", "F", "HSV", "I", "L", "LAB", "P", "RGB", "RGBA", "RGBX", "YCbCr"]]

    def __init__(self,
                 width: Optional[int] = 400,
                 height: Optional[int] = 400,
                 background: Optional[Union[str, Path, BytesIO]] = None,
                 background_GAUSEBLUR_radius: Optional[int] = 12,
                 background_width: Optional[int] = None,
                 background_height: Optional[int] = None,
                 font: Optional[Union[str, Path]] = None,
                 font_size: Optional[int] = 10,
                 image_mode: Optional[str] = 'rgba',
                 **kwargs: Optional[Any]):
        """

        :type background:
        :param width:
        :param height:
        :param background:
        :param background_GAUSEBLUR_radius:
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
        self.background_height = height if background_height is None else background_height
        self.background_width = width if background_width is None else background_width
        if isinstance(background, str) and background.lower() == 'none':
            self.background = Image.new('RGBA', (self.background_width, self.background_height), (255, 255, 255, 255))
        elif background is None:
            self.background = ImageUtils.get_random_background()
        elif isinstance(background, BytesIO):
            self.background = Image.frombuffer(self.image_mode,
                                               (self.background_width, self.background_height),
                                               background.getvalue())
        else:
            if isinstance(background, str):
                background = Path(background)
            if not background.exists():
                raise FileNotFoundError("Can't find the specific background file.")
            self.background = Image.open(background)
        self.background = self.background.resize((self.background_width, self.background_height), Image.ANTIALIAS).\
            filter(ImageFilter.GaussianBlur(radius=background_GAUSEBLUR_radius))

        # font
        if isinstance(font, Path):
            font = str(Path)
        if font:
            self.image_font = ImageFont.truetype(font, font_size)

    @staticmethod
    def get_random_background() -> Image:
        path = Path(RESOURCE_PATH) / 'background'

        if not path.is_absolute():
            path = Path.cwd() / path
        if not path.exists():
            path.mkdir(parents=True)
        backgrounds = list(path.iterdir())
        if not backgrounds:
            raise FileNotFoundError(f"No Background Found in '{path}/', please check the config!")
        return Image.open(choice(backgrounds))
