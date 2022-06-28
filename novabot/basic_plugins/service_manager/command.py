from nonebot import on_command
from nonebot.adapters.onebot.v11 import GroupMessageEvent, GROUP_OWNER, GROUP_ADMIN, Message, MessageEvent
from nonebot.params import CommandArg, Arg
from nonebot.permission import SUPERUSER
from nonebot.typing import T_State

from .data_source import gen_help_img, gen_servcice_help_img
from .service import Service
from ...utils.utils import get_nickname

get_service_list = on_command("lssv",
                              aliases={'服务列表', '功能列表'},
                              priority=1,
                              permission=GROUP_OWNER | GROUP_ADMIN | SUPERUSER)

set_enable = on_command("enable",
                        aliases={'启用', '开启', '打开'},
                        priority=1,
                        permission=GROUP_OWNER | GROUP_ADMIN | SUPERUSER)
set_disable = on_command('disable',
                         aliases={'禁用', '关闭'},
                         priority=1,
                         permission=GROUP_OWNER | GROUP_ADMIN | SUPERUSER)


@get_service_list.handle()
async def _(event: MessageEvent, service_name: Message = CommandArg()):
    service_name = service_name.extract_plain_text()
    r = f'呼吖，{get_nickname()}可不会悄悄告诉你呢'
    if service_name in ['-a', '--all']:
        if isinstance(event, GroupMessageEvent):
            r = await gen_help_img(event, bool(service_name))
    elif service_name:
        r = await gen_servcice_help_img(service_name)
    elif isinstance(event, GroupMessageEvent):
        r = await gen_help_img(event, False)
    await get_service_list.finish(r)


@set_enable.handle()
@set_disable.handle()
async def _(state: T_State, service: Message = CommandArg()):
    if service:
        state['service'] = service


@set_enable.got("service", prompt="唔，想开启什么服务呢？")
async def _(event: GroupMessageEvent,
            service_name: Message = Arg("service")):
    service_name = service_name.extract_plain_text()
    enabled_services = []
    if service_name.lower() in ['all', '全部']:
        for service in Service.get_loaded_services().values():
            service.set_enable(event.group_id)
        enabled_services = ["All"]
    else:
        for service in service_name.split(" "):
            if sv := Service.get_loaded_services().get(service):
                sv.set_enable(event.group_id)
                enabled_services.append(service)
    await set_enable.finish(f"{get_nickname()}已经把服务" + ",".join(enabled_services) + "启用啦！")


@set_disable.got("service", prompt="唔，想禁用什么服务呢？")
async def _(event: GroupMessageEvent,
            service_name: Message = Arg("service")):
    service_name = service_name.extract_plain_text()
    disabled_services = []
    if service_name.lower() in ['all', '全部']:
        for service in Service.get_loaded_services().values():
            service.set_disable(event.group_id)
        disabled_services = ["All"]
    else:
        for service in service_name.split(" "):
            if sv := Service.get_loaded_services().get(service):
                sv.set_disable(event.group_id)
                disabled_services.append(service)
    await set_disable.finish(f"{get_nickname()}已经把服务" + ",".join(disabled_services) + "启用啦！")
