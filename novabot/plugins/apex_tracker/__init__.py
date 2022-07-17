from nonebot import on_command, get_driver
from nonebot.log import logger
from nonebot.params import CommandArg, Arg, T_State
from nonebot.adapters.onebot.v11 import Message, MessageSegment
from .data_source import get_tracker_data, get_master_and_pred_image
from .config import Config

from novabot.basic_plugins.service_manager import Service


__help__ = """ Apex Tracker
usage: .apex {user} {platform}
arg:
    user: username, for steam user, it should be your origin username
    platform: Optional, default is 'origin', it should be Literal['origin', 'psn', 'xbl']
"""

Config = Config.parse_obj(get_driver().config)

apex_stat = on_command(".apex", aliases={'.APEX', '.Apex'})
apex_stat = Service("Apex Tracker",
                    apex_stat,
                    help_=__help__,
                    bundle="Apex",
                    cd=60,
                    cd_reply="You can only use this command once every 60 seconds.\n"
                             "Please try again in %cool% seconds.")

apex_pred = on_command(".pred", aliases={'.APEXPRED', '.apexpred', '.PRED'})
apex_pred = Service("Apex Predator Tracker",
                    apex_pred,
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

    await apex_stat.finish(img)


@apex_pred.handle()
async def _():
    if not Config.APEXLEGEND_API_KEY:
        logger.warning("apex_tracker: You didn't set APEXLEGEND_API_KEY yet!")
        await apex_pred.finish("You didn't set APEXLEGEND_API_KEY yet!")
    else:
        img_fp = await get_master_and_pred_image(Config.APEXLEGEND_API_KEY)
        await apex_pred.finish(img_fp)

