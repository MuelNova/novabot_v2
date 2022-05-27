"""
定义了一个Service类，封装了一个service_scheduler方法，用于对各种插件进行包装

用法:
from novabot.plugins.service_manager import Service, service_scheduler

foo = on_*(...)
foo = Service("foo_plugin", foo, ...)


@service_scheduler("foo_scheduler", "cron", ...)
async def _(bot: Bot, groups: List[int]):
    ...

"""
from .command import *
from .scheduler_service import scheduler as service_scheduler
from .service import Service

__all__ = ["Service", "service_scheduler"]
