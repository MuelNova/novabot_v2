from nonebot import on_command
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Bot
from nonebot.adapters.onebot.v11.exception import ActionFailed
from nonebot.adapters.onebot.v11.permission import GROUP
from nonebot.permission import SUPERUSER

from novabot.basic_plugins.service_manager import Service

from ...helpers import is_reply_my_msg, is_reply_event

with_draw = on_command(".withdraw", aliases={"撤回", "撤"}, permission=GROUP)
s_with_draw = on_command(".withdraw", aliases={"撤回", "撤"}, permission=SUPERUSER)
with_draw = Service("回复撤回", with_draw)
s_with_draw = Service("SU回复撤回", s_with_draw, visible=False)


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
