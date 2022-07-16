from abc import abstractmethod
from datetime import datetime
from typing import Optional, Union

from nonebot import get_driver
from nonebot.adapters.onebot.v11 import Event, Bot
from nonebot.matcher import Matcher
from nonebot.params import Depends

from ...utils.utils import is_admin


driver = get_driver()


def cooldown(service: "Service",
             cool: float,
             prompt: Optional[str] = None):
    async def dependency(bot: Bot, matcher: Matcher, event: Event):
        if hasattr(event, 'group_id'):
            grp_id, user = event.group_id, event.user_id
            no_check = await is_admin(user, grp_id, bot)
            if (cs := service.get_cd(grp_id, user)) > datetime.now().timestamp() and cs != 0 and not no_check:
                await matcher.finish(prompt.replace("%cool%", str(int(cool - (cs - datetime.now().timestamp())))))
            else:
                service.set_cd(grp_id, user, datetime.now().timestamp() + cool)
        return

    return Depends(dependency)


def limitation(service: "Service",
               times: int,
               prompt: Optional[str] = None):
    async def dependency(bot: Bot, matcher: Matcher, event: Event):
        if hasattr(event, 'group_id'):
            grp_id, user = event.group_id, event.user_id
            no_check = await is_admin(user, grp_id, bot)
            if (count := service.get_limit(grp_id, user)) >= times != 0 and not no_check:
                await matcher.finish(prompt)
            else:
                service.set_limit(grp_id, user, count + 1)
        return

    return Depends(dependency)


class ServiceRule:
    __slots__ = ("service",)

    def __init__(self, service: "Service"):
        self.service = service

    @abstractmethod
    async def __call__(self, *args, **kwargs) -> bool:
        raise NotImplementedError

    def __repr__(self):
        return f"<Rule of {self.service.service_name}>"


class GroupRule(ServiceRule):
    async def __call__(self, event: Event) -> bool:
        return is_able_in_group(self.service, event)

    def __repr__(self):
        return f"<GroupRule of {self.service.service_name}>"


def is_able_in_group(service: Union["Service", "SchedulerService"], event: Union[Event, "SchedulerEvent"]) -> bool:
    if hasattr(event, 'group_id'):
        return event.group_id not in service.disable_group if service.enable_on_default \
            else event.group_id in service.enable_group
    return True
