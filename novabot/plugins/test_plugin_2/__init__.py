from nonebot_plugin_apscheduler import scheduler


@scheduler.scheduled_job('cron', id='abcdefe', second='3')
async def _():
    ...
