"""
定义了一个Service类，用于对各种插件进行包装

用法:
from novabot.plugins.service_manager import Service

foo = on_*(...)
foo = Service("foo_plugin", foo, ...)

"""

from .command import *
from .service import Service

__all__ = ["Service"]
