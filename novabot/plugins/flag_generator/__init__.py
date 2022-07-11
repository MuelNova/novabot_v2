import random
import string

from nonebot import on_command
from nonebot.params import CommandArg, Arg, T_State
from nonebot.adapters.onebot.v11 import Message

from novabot.basic_plugins.service_manager import Service

__help__ = """为你的 flag 字符串增加变数
用法:
   /flag <str> 
"""

FLAG_DICT = {
    "a": ["a", "A", "@", "4"],
    "b": ["b", "B", "8"],
    "e": ["e", "E", "3"],
    "g": ["g", "G", "9"],
    "i": ["i", "I", "1"],
    "o": ["o", "O", "0"],
    "s": ["s", "S", "$"],
    " ": [" ", "~", "_"]
}
for i in string.ascii_lowercase:
    if not FLAG_DICT.get(i):
        FLAG_DICT[i] = [i, i.upper()]

flag_generator = on_command("/flag", priority=2, block=True)
flag_generator = Service("Flag Generator", flag_generator, help_=__help__, bundle="Utils")


@flag_generator.handle()
async def _(state: T_State, arg=CommandArg()):
    if arg:
        state['flag'] = arg


@flag_generator.got("flag", prompt="What Flag?")
async def _(flag: Message = Arg('flag')):
    flag = str(flag).lower()
    flag = map(lambda x: random.choice(FLAG_DICT.get(x, [x])), list(flag))
    flag = "".join(flag)
    await flag_generator.finish("TSCTF-J{" + flag + "}")
