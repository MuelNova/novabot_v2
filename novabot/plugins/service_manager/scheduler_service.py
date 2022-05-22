import json
from typing import Callable, TypeVar, Optional, Dict, Any, Union
from pathlib import Path
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from nonebot import get_driver, get_bot
from nonebot.adapters.onebot.v11 import Bot
from nonebot.log import logger

from .rule import is_able_in_group
from .data_source import GlobalVar as gV
from ...utils import _load_file, _save_file

T = TypeVar('T', bound=Callable)
args_list = ['help_', 'bundle', 'visible', 'enable_on_default']
bot: Optional[Bot] = None


class SchedulerEvent:
    def __init__(self, group_id: int):
        self.group_id = group_id


class SchedulerService:

    def __init__(self,
                 service_name: str,
                 func: Callable,
                 help_: Optional[str] = None,
                 bundle: Optional[str] = None,
                 visible: Optional[bool] = None,
                 enable_on_default: Optional[bool] = None,
                 ):
        self.service_name = service_name
        self.func = func

        config = self._load_config()
        self.help = help_
        self.enable_group = set(config.get('enable_group', []))
        self.disable_group = set(config.get('disable_group', []))
        self.enable_on_default = config.get('enable_on_default')
        if self.enable_on_default is None:
            self.enable_on_default = enable_on_default
        if self.enable_on_default is None:
            self.enable_on_default = True
        self.visible = config.get('visible')
        if self.visible is None:
            self.visible = visible
        if self.visible is None:
            self.visible = True

        gV.loaded_service[self.service_name] = self
        gV.service_bundle[bundle or '默认'].append(self)

    def __repr__(self):
        return f"<Scheduler Service '{self.service_name}'," \
               f" enable_on_default={self.enable_on_default}," \
               f" visible={self.visible},>"

    def _load_config(self) -> Dict[str, Any]:
        path = Path.cwd() / "novabot" / "plugin_config" / "service_manager" / f"{self.service_name}.json"
        if not path.parent.exists():
            path.parent.mkdir(parents=True)
        return json.loads(_load_file(path) or "{}")

    def _save_config(self):
        path = Path.cwd() / "novabot" / "plugin_config" / "service_manager" / f"{self.service_name}.json"
        if not path.parent.exists():
            path.parent.mkdir(parents=True)
        _save_file(path,
                   {
                       "plugin_name": self.service_name,
                       "enable_on_default": self.enable_on_default,
                       "visible": self.visible,
                       "enable_group": list(self.enable_group),
                       "disable_group": list(self.disable_group),
                   })

    def set_enable(self, group_id: int):
        self.enable_group.add(group_id)
        self.disable_group.discard(group_id)
        self._save_config()
        logger.info(f'Service {self.service_name} is enabled at group {group_id}')

    def set_disable(self, group_id: int):
        self.disable_group.add(group_id)
        self.enable_group.discard(group_id)
        self._save_config()
        logger.info(f'Service {self.service_name} is disabled at group {group_id}')

    @staticmethod
    def get_loaded_services() -> Dict[str, Union["Service", "SchedulerService"]]:
        return gV.loaded_service

    async def call(self, *args, **kwargs):
        groups = await bot.call_api('get_group_list')
        print(groups)
        grp_list = []
        for i in groups:
            grp_id = i.get('group_id')
            if is_able_in_group(self, SchedulerEvent(grp_id)):
                grp_list.append(grp_id)
        return await self.func(bot=bot, groups=grp_list, *args, **kwargs)


def scheduler_service_decorator(scheduler_: AsyncIOScheduler) -> T:
    def scheduled_job(service_name: str, *args, **kwargs) -> T:
        def inner(func: T) -> T:
            service_args = {}
            for k in args_list:
                if v := kwargs.get(k):
                    service_args[k] = v
                    kwargs.pop(k)
            scheduler_.add_job(SchedulerService(service_name, func, **service_args).call, *args, **kwargs)
            return func
        return inner
    return scheduled_job


scheduler = AsyncIOScheduler()
scheduler.scheduled_job = scheduler_service_decorator(scheduler)


async def _start_scheduler():
    global bot
    bot = get_bot()
    if not scheduler.running:
        scheduler.start()
        logger.opt(colors=True).info("<y>Scheduler Started</y>")


driver = get_driver()
driver.on_bot_connect(_start_scheduler)
