from typing import Dict, Union, List

from nonebot.adapters.onebot.v11 import MessageSegment
from nonebot.typing import T_State


def update_inner_dict(raw_dict: Dict, key: Union[str, int], default_dict: Dict = None, **kwargs) -> Dict:
    if default_dict is None:
        default_dict = {}
    inner_dict = raw_dict.get(key, default_dict)
    for k, v in kwargs.items():
        inner_dict[k] = v
    print(raw_dict, {key: inner_dict})
    raw_dict.update({key: inner_dict})
    print(raw_dict)
    return raw_dict


async def get_command_arg_text(state: T_State, default_text="") -> str:
    if arg := state['_prefix'].get('command_arg'):
        arg: List[MessageSegment]
        msg = str(arg[0]) if arg[0].type == 'text' else default_text
        if msg.startswith('\\'):
            msg = msg[1:]
    else:
        msg = default_text
    return msg
