from nonebot.adapters.onebot.v11 import Bot, MessageEvent, GroupMessageEvent
from nonebot.internal.permission import Permission as Permission


class BotOwner:
    """检查当前事件是否是消息事件且属于超级管理员"""

    __slots__ = ()

    async def __call__(self, bot: Bot, event: MessageEvent) -> bool:
        if isinstance(event, GroupMessageEvent):
            grp_id = event.group_id
            self_info = await bot.call_api('get_group_member_info', group_id=grp_id, user_id=event.self_id)
            if self_info.get('role') == 'owner':
                return True
        return False


class BotAdmin(BotOwner):
    """检查当前事件是否是消息事件且属于超级管理员"""

    __slots__ = ()

    async def __call__(self, bot: Bot, event: MessageEvent) -> bool:
        if isinstance(event, GroupMessageEvent):
            grp_id = event.group_id
            self_info = await bot.call_api('get_group_member_info', group_id=grp_id, user_id=event.self_id)
            if self_info.get('role') == 'admin':
                return True
        return await super(BotAdmin, self).__call__(bot, event)


BOT_OWNER: Permission = Permission(BotOwner())
BOT_ADMIN: Permission = Permission(BotAdmin())

__autodoc__ = {
    "Permission": True,
    "Permission.__call__": True,
}
