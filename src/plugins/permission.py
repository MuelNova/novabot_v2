from nonebot.adapters.onebot.v11 import Bot, MessageEvent, GroupMessageEvent
from nonebot.rule import Rule


class BotOwner:
    """检查当前事件是否是消息事件且BOT属于群主"""

    __slots__ = ()

    async def __call__(self, bot: Bot, event: MessageEvent) -> bool:
        if isinstance(event, GroupMessageEvent):
            grp_id = event.group_id
            self_info = await bot.call_api('get_group_member_info', group_id=grp_id, user_id=event.self_id)
            if self_info.get('role') == 'owner':
                return True
        return False


class BotAdmin(BotOwner):
    """检查当前事件是否是消息事件且BOT属于管理员"""

    __slots__ = ()

    async def __call__(self, bot: Bot, event: MessageEvent) -> bool:
        if isinstance(event, GroupMessageEvent):
            grp_id = event.group_id
            self_info = await bot.call_api('get_group_member_info', group_id=grp_id, user_id=event.self_id)
            if self_info.get('role') == 'admin':
                return True
        return await super(BotAdmin, self).__call__(bot, event)


BOT_OWNER: Rule = Rule(BotOwner())
BOT_ADMIN: Rule = Rule(BotAdmin())

__autodoc__ = {
    "Permission": True,
    "Permission.__call__": True,
    "Rule": True,
    "Rule.__call": True
}
