from nonebot import get_driver, on_command
from nonebot.params import CommandArg, Arg
from nonebot.typing import T_State
from nonebot.adapters.onebot.v11 import Message, MessageSegment
from .browser import install, init, get_tracker_data

driver = get_driver()

driver.on_startup(install)
driver.on_startup(init)

apex_stat = on_command(".apex", aliases={'.APEX', '.Apex'})


@apex_stat.handle()
async def _(state: T_State,
            args: Message = CommandArg()):
    if args:
        args = str(args)
        if len(args := args.strip().split(' ')) >= 2:
            state['platform'] = args[1].lower()
        state['user'] = args[0]


@apex_stat.got('user', prompt="""Apex Tracker
Who do you want to track?

usage: .apex {user} {platform}
arg:
    user: username, for steam user, it should be your origin username
    platform: Optional, default is 'origin', it should be Literal['origin', 'psn', 'xbl']
""")
async def _(state: T_State,
            user: str = Arg('user')):
    img = await get_tracker_data(
        f"https://apex.tracker.gg/apex/profile/{state.get('platform', 'origin')}/{user}/overview"
    )

    await apex_stat.finish(MessageSegment.image(f'base64://{img}'))

