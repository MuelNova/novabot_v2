from nonebot.adapters.onebot.v11 import GroupMessageEvent, Bot, Event
from nonebot.matcher import Matcher
from nonebot.params import Depends


def is_reply_my_msg() -> None:
    async def _is_reply_my_msg(matcher: Matcher, event: GroupMessageEvent):
        if event.reply and event.self_id == event.reply.sender.user_id:
            return
        await matcher.finish()

    return Depends(_is_reply_my_msg)


def is_reply_event() -> None:
    async def _is_reply_event(matcher: Matcher, event: GroupMessageEvent):
        if event.reply:
            return
        await matcher.finish()

    return Depends(_is_reply_event)


def is_admin_or_owner() -> None:
    async def _is_admin_or_owner(matcher: Matcher, event: Event, bot: Bot):
        # sourcery skip: merge-nested-ifs
        if hasattr(event, 'group_id'):
            if (await bot.call_api("get_group_member_info", group_id=event.group_id, user_id=event.self_id)).\
                    get('role') in ['owner', 'admin']:
                return
        await matcher.finish()
