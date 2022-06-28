import random

from nonebot import on_regex
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Bot, MessageSegment
from novabot.basic_plugins.service_manager import Service

from ...utils.utils import is_admin, get_nickname
from ...helpers import is_admin_or_owner


__help__ = """投票禁言啦!爱他就口他吧!
     Type: MessageEvent | ReplyEvent 
用法:
     口他 @QQ
     口它 @QQ
     口她 @QQ
"""

vote_to_mute = on_regex(r"(.*)口([他它她]+)(.*)", priority=5, block=True)
vote_to_mute = Service("投票禁言",
                       vote_to_mute,
                       bundle="群管",
                       help_=__help__,
                       cd=900,
                       cd_reply="口的太快啦！会坏掉的！每次间隔需要 15 分钟呢")

mute_list = {}


@vote_to_mute.handle([is_admin_or_owner(MessageSegment.text(f"咕咕，{get_nickname()}口不了人，呜"))])
async def _(bot: Bot, event: GroupMessageEvent):
    usr_id = 0
    if event.reply:
        usr_id = event.reply.sender.user_id
    else:
        for i in event.message:
            if i.type == 'at':
                print(i, i.data.get('qq'))
                usr_id = int(i.data.get('qq'))
                break
        if usr_id == 0:
            await vote_to_mute.finish("是要口你自己嘛，哼哼")
    if await is_admin(usr_id, event.group_id, bot):
        await vote_to_mute.finish(f"{get_nickname()}不敢口他，QAQ")

    mute_dict = mute_list.get(str(event.group_id), {})
    user_mute = mute_dict.get(str(usr_id), set())
    user_mute.add(event.sender.user_id)

    if len(user_mute) == 3 or await is_admin(event.sender.user_id, event.group_id, bot):
        await bot.call_api("set_group_ban",
                           user_id=usr_id,
                           group_id=event.group_id,
                           duration=random.randint(600, 1200))
        await vote_to_mute.send(f"哼哼哼，好好带上吧，这是{get_nickname()}的奖励!")
        user_mute = set()
    else:
        await vote_to_mute.send(f"哦呀呀，已经有 {len(user_mute)} 个人想要给" + MessageSegment.at(usr_id) +
                                f"带上口球啦，集齐 3 票的话{get_nickname()}就要过来啦OpO")

    mute_dict[str(usr_id)] = user_mute
    mute_list[str(event.group_id)] = mute_dict
