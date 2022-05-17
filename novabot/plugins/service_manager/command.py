from nonebot import on_command
from nonebot.adapters.onebot.v11 import GroupMessageEvent

from .data_source import GlobalVar as gV
from .rule import is_able_in_group
from .service import Service

__all__ = [
    "get_service_list"
]

get_service_list = on_command("lssm", priority=1)
get_service_list = Service("service_manager", get_service_list)


@get_service_list.handle()
async def _(event: GroupMessageEvent):
    msg = f"{event.group_id}的服务开启情况:\n"
    for name_, services in gV.service_bundle.items():
        msg += f"  {name_}:\n"
        for service in services:
            msg += ("    |" +
                    ("√" if is_able_in_group(service, event) else "×") +
                    f"| {service.plugin_name}\n") if service.visible else ""
    await get_service_list.finish(msg)
