"""
定义了一个Service类，用于对各种插件进行包装

用法:
from nonebot.plugin import require

service = require("service_manager").Service

cmd = on_command("some_command_here", ...)
service(cmd, ...)

"""
from nonebot.plugin import export

from .service import Service

__all__ = []

export = export()
export.Service = Service
