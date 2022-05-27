from PIL import Image, ImageDraw
from PIL.Image import Image as IMG
from typing import List, Optional, Iterator

from .types import *
from .fonts import Font, get_proper_font, fallback_fonts_regular, fallback_fonts_bold


class Char:
    def __init__(
        self,
        char: str,
        font: Font,
        fontsize: int,
        fill: ColorType,
        stroke_width: int = 0,
        stroke_fill: Optional[ColorType] = None,
    ):
        self.char = char
        self.font = font
        self.fontsize = fontsize
        self.fill = fill
        self.stroke_width = stroke_width
        self.stroke_fill = stroke_fill

        if self.font.valid_size:
            self.pilfont = self.font.load_font(self.font.valid_size)
        else:
            self.pilfont = self.font.load_font(fontsize)

        self.ascent, self.descent = self.pilfont.getmetrics()
        self.width, self.height = self.pilfont.getsize(
            self.char, stroke_width=self.stroke_width
        )

        if self.font.valid_size:
            ratio = fontsize / self.font.valid_size
            self.ascent *= ratio
            self.descent *= ratio
            self.width *= ratio
            self.height *= ratio

    def draw_on(self, img: IMG, pos: ImgPosType):
        if self.font.valid_size:
            ratio = self.font.valid_size / self.fontsize
            new_img = Image.new(
                "RGBA", (int(self.width * ratio), int(self.height * ratio))
            )
            draw = ImageDraw.Draw(new_img)
            draw.text(
                (0, 0),
                self.char,
                font=self.pilfont,
                fill=self.fill,
                stroke_width=self.stroke_width,
                stroke_fill=self.stroke_fill,
                embedded_color=True,
            )
            new_img = new_img.resize(
                (int(self.width), int(self.height)), resample=Image.ANTIALIAS
            )
            img.paste(new_img, pos, mask=new_img)
        else:
            draw = ImageDraw.Draw(img)
            draw.text(
                pos,
                self.char,
                font=self.pilfont,
                fill=self.fill,
                stroke_width=self.stroke_width,
                stroke_fill=self.stroke_fill,
                embedded_color=True,
            )


class Line:
    def __init__(self, chars: List[Char], align: HAlignType = "left"):
        self.chars: List[Char] = chars
        self.align: HAlignType = align

    @property
    def width(self) -> int:
        return sum(char.width for char in self.chars) if self.chars else 0

    @property
    def height(self) -> int:
        return max(char.height for char in self.chars) if self.chars else 0

    @property
    def ascent(self) -> int:
        return max(char.ascent for char in self.chars) if self.chars else 0

    @property
    def descent(self) -> int:
        return max(char.descent for char in self.chars) if self.chars else 0

    def wrap(self, width: float) -> Iterator["Line"]:
        last_idx = 0
        for idx in range(len(self.chars)):
            if Line(self.chars[last_idx : idx + 1]).width > width:
                yield Line(self.chars[last_idx:idx], self.align)
                last_idx = idx
        yield Line(self.chars[last_idx:], self.align)


class Text2Image:
    def __init__(self, lines: List[Line], spacing: int = 4):
        self.lines = lines
        self.spacing = spacing

    @classmethod
    def from_text(
            cls,
            text: str,
            fontsize: int,
            bold: bool = False,
            fill: ColorType = "black",
            spacing: int = 4,
            align: HAlignType = "left",
            stroke_width: int = 0,
            stroke_fill: Optional[ColorType] = None,
            fontname: str = "",
            fallback_fonts: List[str] = None
    ) -> "Text2Image":
        """
        从文本构建 `Text2Image` 对象
        :参数:
          * ``text``: 文本
          * ``fontsize``: 字体大小
          * ``bold``: 是否加粗
          * ``fill``: 文字颜色
          * ``spacing``: 多行文字间距
          * ``align``: 多行文字对齐方式，默认为靠左
          * ``stroke_width``: 文字描边宽度
          * ``stroke_fill``: 描边颜色
          * ``fontname``: 指定首选字体
          * ``fallback_fonts``: 指定备选字体
        """
        if fallback_fonts is None:
            fallback_fonts = []
        lines: List[Line] = []
        chars: List[Char] = []

        for char in text:
            if char == "\n":
                lines.append(Line(chars, align))
                chars = []
                continue
            font = get_proper_font(char, bold, fontname, fallback_fonts)
            if not font:
                font = fallback_fonts_bold[0] if bold else fallback_fonts_regular[0]
            chars.append(Char(char, font, fontsize, fill, stroke_width, stroke_fill))
        if chars:
            lines.append(Line(chars, align))
        return cls(lines, spacing)
