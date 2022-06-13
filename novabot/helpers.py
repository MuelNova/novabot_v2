from nonebot.params import Depends
from nonebot.matcher import Matcher
from nonebot.adapters.onebot.v11 import GroupMessageEvent


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
