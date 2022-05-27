from typing import List

from nonebot.adapters.onebot.v11 import Bot, MessageSegment

from novabot.plugins.service_manager import service_scheduler


@service_scheduler.scheduled_job("test_plugin", 'cron', id='abcdef', second='0/30')
async def _(bot: Bot, groups: List[int]):
    for i in groups:
        await bot.call_api('send_group_msg', group_id=i, message=MessageSegment.text("Test on group %s" % i))
