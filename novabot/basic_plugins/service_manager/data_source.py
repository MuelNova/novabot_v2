import base64
import math

from collections import defaultdict
from typing import Dict, List, Union, Optional
from pathlib import Path
from random import choice

from nonebot.adapters.onebot.v11 import MessageSegment, GroupMessageEvent

from .rule import is_able_in_group
from ...utils.image_utils import ABuildImage, BuildImage, Text2Image


class GlobalVar(dict):
    loaded_service: Dict[str, Union["Service", "SchedulerService"]] = {}
    service_bundle: Dict[str, List[Union["Service", "SchedulerService"]]] = defaultdict(list)

    def __setattr__(self, key, value):
        self[key] = value


async def gen_help_img(event: GroupMessageEvent, all_: bool = False) -> MessageSegment:
    bundles = GlobalVar.service_bundle
    if not bundles:
        return MessageSegment.text('   No service found!')
    padding = 30
    default_y = 200
    helps_ = []
    for bundle, services in bundles.items():
        msg = f"  {bundle}:\n\n"
        for service in services:
            msg += ("    |" +
                    (" ✓ " if is_able_in_group(service, event) else " ✗ ") +
                    f"| {service.service_name}\n") if service.visible or all_ else ""
        txt = Text2Image.from_text(msg, 30).to_image((255, 255, 255, 200), (10, 5))
        helps_.append(txt)

    # This is still improvable when splitting, thus, need to re-write all.
    # Sort of something I don't event know how
    # But it works lol, though in low efficiency but faster than pasting directly, and has smaller size.
    widths = sorted(helps_, key=lambda x_: x_.width, reverse=True)
    n = math.ceil(math.sqrt(len(widths)))
    helps_ = [widths[i: i + n] for i in range(0, len(widths), n)]  # sort in width order and split averagely.
    n = len(helps_)
    heights = [sum(map(lambda i: i.height, k)) for k in helps_]  # sum of heights of every row.
    sorted_heights = sorted(heights)
    for i in range(len(sorted_heights) // 2):
        bigger_list = helps_[heights.index(sorted_heights[i])]  # the list which has bigger sum
        smaller_list = helps_[heights.index(sorted_heights[-(i+1)])]
        for k in range(min(len(bigger_list), len(smaller_list)) // 2):  # check every element
            bigger = sorted(bigger_list, key=lambda i: i.height, reverse=True)[k]
            bigger_index = bigger_list.index(bigger)
            smaller = sorted(smaller_list, key=lambda i: i.height, reverse=True)[-(k+1)]
            smaller_index = smaller_list.index(smaller)
            if bigger.height - smaller.height < bigger.width - smaller.width:
                smaller_list[smaller_index], \
                bigger_list[bigger_index] = bigger_list[bigger_index], \
                                            smaller_list[smaller_index]
            else:
                break
    width = sum(map(lambda i: max(map(lambda x_: x_.width, i)), helps_)) + (n+1)*padding
    heights = [sum(map(lambda i: i.height, k)) for k in helps_]
    height = max(heights) + default_y + n*padding
    print(width, height)
    size = max(width, height)
    img = ABuildImage.new((size, size), 'RGBA', (255, 255, 255, 200))
    if background := get_random_background():
        background = background.resize((img.width, img.height)).gauss(8)
        img = await img.call_func('paste_center', background, True)
    img = await img.a_draw_text((0, 0, size, size),
                                "TestTestTest\nTest2Test2Test2",
                                halign='left',
                                valign='top',
                                spacing=10)
    x = padding
    y = default_y
    for i in helps_:
        for j in i:
            img = await img.a_paste(j, (x, y), True)
            y += j.height + padding
        x += max(map(lambda x_: x_.width, i)) + padding
        y = default_y
    b64 = f"base64://{base64.b64encode(img.save_png().getvalue()).decode()}"
    return MessageSegment.image(b64)


def get_random_background() -> Optional[BuildImage]:
    path = Path.cwd() / "novabot" / "resources" / "images" / "background"
    path.mkdir(parents=True, exist_ok=True)
    img = list(path.iterdir())
    return BuildImage.open(choice(img)) if img else None
