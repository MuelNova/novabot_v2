import re

from typing import List, Dict, Union

from nonebot import on_command
# from nonebot.log import logger
from nonebot.permission import SUPERUSER
from nonebot.typing import T_State
from nonebot.adapters.onebot.v11 import Message, MessageSegment, Bot, GroupMessageEvent, ActionFailed

other_type_text = '@#OTHER_TYPE#@'

fake_forward = on_command('.forward', aliases={'.Forward'}, permission=SUPERUSER)

__help__ = """伪造聊天记录 - Fake Forward
Permission: SUPERUSER
使用方法: .forward %Args%
    -Args:
        -u: User_ID
        -n: Nick_name, Optional
        -m: Message"""


def get_json(uin: int,
             name: str,
             msgs: Union[List[MessageSegment], MessageSegment]) -> Dict:
    if isinstance(msgs, List):
        return {"type": "node", "data": {"name": name, "uin": uin, "content": [msg for msg in msgs]}}
    return {"type": "node", "data": {"name": name, "uin": uin, "content": msgs}}


@fake_forward.handle()
async def _(bot: Bot, event: GroupMessageEvent, state: T_State):
    if not (msgs := state['_prefix'].get('command_arg')):
        await fake_forward.finish(__help__)
    else:
        args = ''.join(i.data.get('text', other_type_text) for i in msgs)
        other_type_msg = [i for i in msgs if i.type != 'text']
        users = re.findall(r'-u (\d+)', args)
        msgs_node = []
        for i in args.split('-u'):
            if len((msgs := i.split('-m '))) == 1:
                continue
            msgs = [k.strip() for k in msgs]
            print(msgs)
            uin = int(users[0])
            users.pop(0)
            nickname = msgs[0].split('-n')
            if len(nickname) > 1:
                name = nickname[1]
            else:
                try:
                    user_info = await bot.call_api('get_group_member_info', group_id=event.group_id, user_id=uin)
                    name = user_info.get('card', user_info.get('name'))
                    if not name:
                        raise ActionFailed
                except ActionFailed:
                    user_info = await bot.call_api('get_stranger_info', user_id=uin)
                    name = user_info.get('nickname')
            for msg in msgs[1:]:
                if other_type_text in msg:
                    if msg == other_type_text:
                        if other_type_msg:
                            msg_list = [other_type_msg[0]]
                            other_type_msg.pop(0)
                        else:
                            continue
                    else:
                        if other_type_msg:
                            other_msg = other_type_msg[0]
                            other_type_msg.pop(0)
                        else:
                            other_msg = MessageSegment.text('')
                        msg_list = [MessageSegment.text(msg.replace(other_type_text, '')), other_msg]
                    msgs_node.append(get_json(uin, name, msg_list))
                else:
                    msgs_node.append(get_json(uin, name, MessageSegment.text(msg)))
        await bot.call_api('send_group_forward_msg', group_id=event.group_id, messages=msgs_node)
