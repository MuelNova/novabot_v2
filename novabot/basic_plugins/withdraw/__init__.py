from nonebot import on_command
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Bot
from nonebot.adapters.onebot.v11.exception import ActionFailed
from nonebot.adapters.onebot.v11.permission import GROUP
from nonebot.permission import SUPERUSER

from novabot.basic_plugins.service_manager import Service

from ...helpers import is_reply_my_msg, is_reply_event


__help__ = """通过回复BOT的发言并输入"撤回"即可撤回bot的发言，用于防止色图炸群刷屏等
    Type: ReplyEvent
用法:
    .withdraw
    撤回
    撤
"""

with_draw = on_command(".withdraw", aliases={"撤回", "撤"}, permission=GROUP)
s_with_draw = on_command(".withdraw", aliases={"撤回", "撤"}, permission=SUPERUSER)
with_draw = Service("回复撤回", with_draw, bundle="基础插件", help_=__help__)
s_with_draw = Service("SU回复撤回", s_with_draw, visible=False, bundle="基础插件", help_=__help__)


@with_draw.handle([is_reply_my_msg()])
@s_with_draw.handle([is_reply_event()])
async def _(bot: Bot, event: GroupMessageEvent):
    try:
        await bot.call_api("delete_msg", message_id=event.reply.message_id)
    except ActionFailed:
        pass
    try:
        await bot.call_api("delete_msg", message_id=event.message_id)
    except ActionFailed:
        pass
