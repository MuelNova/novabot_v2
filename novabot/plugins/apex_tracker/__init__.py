from nonebot import on_command
from nonebot.params import CommandArg, Arg, T_State
from nonebot.adapters.onebot.v11 import Message, MessageSegment
from .data_source import get_tracker_data

from novabot.basic_plugins.service_manager import Service

__help__ = """ Apex Tracker
usage: .apex {user} {platform}
arg:
    user: username, for steam user, it should be your origin username
    platform: Optional, default is 'origin', it should be Literal['origin', 'psn', 'xbl']
"""

apex_stat = on_command(".apex", aliases={'.APEX', '.Apex'})
apex_stat = Service("Apex Tracker",
                    apex_stat,
                    help_=__help__,
                    bundle="Apex",
                    cd=60,
                    cd_reply="You can only use this command once every 60 seconds.\n"
                             "Please try again in %cool% seconds.")


@apex_stat.handle()
async def _(state: T_State,
            args: Message = CommandArg()):
    if args:
        args = str(args)
        if len(args := args.strip().split(' ')) >= 2:
            state['platform'] = args[1].lower()
        state['user'] = args[0]


@apex_stat.got('user', prompt="""Who do you want to tracker?""")
async def _(state: T_State,
            user: str = Arg('user')):
    img = await get_tracker_data(
        f"https://apex.tracker.gg/apex/profile/{state.get('platform', 'origin')}/{user}/overview"
    )

    await apex_stat.finish(MessageSegment.image(f'base64://{img}'))
