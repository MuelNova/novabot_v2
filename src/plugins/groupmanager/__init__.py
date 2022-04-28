from pathlib import Path

from nonebot import get_driver, on_command
from nonebot.params import CommandArg, Arg
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, Message
from nonebot.permission import SUPERUSER
from nonebot.typing import T_State

from .config import Config
from .data_source import save, read
from ..permission import BOT_OWNER, BOT_ADMIN
from ..utils import update_inner_dict, get_command_arg_text

driver = get_driver()
global_config = driver.config
config = Config.parse_obj(global_config)

__version__ = 0.1
__change_card_help__ = f"""修改群头衔 v{__version__}
.card [头衔] 修改头衔，不填则为删除头衔
"""

# TO-DOs: change group avatar, change group name
# To-Dos: vote mute, mute oneself


change_card = on_command('.card', aliases={"修改群头衔", "修改头衔"}, rule=BOT_OWNER)

change_group_name = on_command('.gname', rule=BOT_ADMIN)
change_group_basename = on_command('.basegname', rule=BOT_ADMIN, permission=SUPERUSER)
change_group_name_prefix = on_command('.gname_prefix', rule=BOT_ADMIN, permission=SUPERUSER)
change_group_name_suffix = on_command('.gname_suffix', rule=BOT_ADMIN, permission=SUPERUSER)
change_group_name_conn = on_command('.gname_conn', rule=BOT_ADMIN, permission=SUPERUSER)
group_name_info = on_command('.gname_info', rule=BOT_ADMIN)

change_group_avatar = on_command('.gavatar', rule=BOT_ADMIN)


group_name_data = {}
group_name_default_dict = {
    "basename": "",
    "prefix": "",
    "suffix": "",
    "conn": " - "
}


@driver.on_startup
async def _():
    if not Path(config.database_path).exists():
        Path(config.database_path).parent.mkdir(parents=True, exist_ok=True)
    global group_name_data
    group_name_data = read()


@change_card.handle()
async def _(bot: Bot, state: T_State, event: GroupMessageEvent):
    msg = await get_command_arg_text(state)

    await bot.call_api('set_group_special_title',
                       group_id=event.group_id,
                       user_id=event.user_id,
                       special_title=msg)

    await change_card.finish('给你的头衔，带好啦！')


@change_group_name.handle()
async def _(bot: Bot, event: GroupMessageEvent, state: T_State):
    global group_name_data
    msg = await get_command_arg_text(state)
    grp_info = group_name_data.get(str(event.group_id), group_name_default_dict)
    try:
        if not grp_info['basename']:
            group_name = grp_info['prefix'] + msg + grp_info['suffix']
        else:
            group_name = grp_info['prefix'] + grp_info['basename'] + grp_info['conn'] + msg + grp_info['suffix']
    except KeyError:
        group_name = msg
    await bot.call_api("set_group_name", group_id=event.group_id, group_name=group_name)
    await change_group_name.finish(f"已修改群名为： {group_name}")


@change_group_basename.handle()
async def _(event: GroupMessageEvent, state: T_State):
    msg = await get_command_arg_text(state)
    global group_name_data
    group_name_data = update_inner_dict(group_name_data,
                                        str(event.group_id),
                                        basename=msg,
                                        default_dict=group_name_default_dict)
    save(group_name_data)
    await change_group_basename.finish(f"已修改基本群名为： {msg}")


@change_group_name_prefix.handle()
async def _(event: GroupMessageEvent, state: T_State):
    msg = await get_command_arg_text(state)
    global group_name_data
    group_name_data = update_inner_dict(group_name_data,
                                        str(event.group_id),
                                        prefix=msg,
                                        default_dict=group_name_default_dict)
    save(group_name_data)
    await change_group_name_prefix.finish(f"已修改群名前缀为： {msg}")


@change_group_name_suffix.handle()
async def _(event: GroupMessageEvent, state: T_State):
    msg = await get_command_arg_text(state)
    global group_name_data
    group_name_data = update_inner_dict(group_name_data,
                                        str(event.group_id),
                                        suffix=msg,
                                        default_dict=group_name_default_dict)
    save(group_name_data)
    await change_group_name_suffix.finish(f"已修改群名后缀为： {msg}")


@change_group_name_conn.handle()
async def _(event: GroupMessageEvent, state: T_State):
    msg = await get_command_arg_text(state)
    global group_name_data
    group_name_data = update_inner_dict(group_name_data,
                                        str(event.group_id),
                                        conn=msg,
                                        default_dict=group_name_default_dict)
    save(group_name_data)
    await change_group_name_conn.finish(f"已修改群名连接符为： {msg}")


@group_name_info.handle()
async def _(event: GroupMessageEvent):
    await group_name_info.finish(f"{event.group_id}: \n"
                                 + "\n".join(f"{k}: {v}"
                                             for k, v in group_name_data.get(str(event.group_id),
                                                                             group_name_default_dict).items()))


@change_group_avatar.handle()
async def _(state: T_State,
            gavatar: Message = CommandArg()):
    if gavatar:
        state['gavatar'] = gavatar


@change_group_avatar.got('gavatar', prompt='Which Avatar?')
async def _(bot: Bot, event: GroupMessageEvent, gavatar: Message = Arg('gavatar')):
    if gavatar[0].type == 'image':
        url = gavatar[0].data['url']
        await bot.call_api("set_group_portrait", group_id=event.group_id, file=url)
        await change_group_avatar.finish("Changing...It could be failed if the token expired.")
    else:
        await change_group_avatar.finish("It's not a image!")
