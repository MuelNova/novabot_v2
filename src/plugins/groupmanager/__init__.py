import random

from nonebot import get_driver, on_command
from nonebot.adapters.onebot.v11 import Bot, MessageSegment, GroupMessageEvent
from nonebot.typing import T_State
from ..permission import BOT_OWNER

from .config import Config

global_config = get_driver().config
config = Config.parse_obj(global_config)

__version__ = 0.1
__help__ = f"""修改群头衔 v{__version__}
.card [头衔] 修改头衔，不填则为删除头衔
"""

# TO-DOs: add card, change group avatar, change group name
# To-Dos: vote mute, mute oneself


change_card = on_command('.card', aliases={"修改群头衔", "修改头衔"}, permission=BOT_OWNER)


@change_card.handle()
async def _(bot: Bot, state: T_State, event: GroupMessageEvent):
    if arg := state['_prefix'].get('command_arg'):
        arg[0]: MessageSegment
        msg = arg[0] if arg[0].type == 'text' else ''
    else:
        msg = ''
    if random.randint(1, 100) > 90:
        msg = '小猪🐖'
    await bot.call_api('set_group_special_title',
                       group_id=event.group_id,
                       user_id=event.user_id,
                       special_title=msg)

    await change_card.finish('给你的头衔，带好啦！')
