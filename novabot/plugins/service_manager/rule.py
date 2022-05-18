from abc import abstractmethod
from datetime import datetime
from typing import Optional

from nonebot.adapters.onebot.v11 import Event
from nonebot.matcher import Matcher
from nonebot.params import Depends


def cooldown(service: "Service",
             cool: float,
             prompt: Optional[str] = None):
    async def dependency(matcher: Matcher, event: Event):
        if hasattr(event, 'group_id'):
            grp_id, user = event.group_id, event.user_id
            if (cs := service.get_cd(grp_id, user)) > datetime.now().timestamp() and cs != 0:
                await matcher.finish(prompt)
            else:
                service.set_cd(grp_id, user, datetime.now().timestamp() + cool)
        return

    return Depends(dependency)


def limitation(service: "Service",
               times: int,
               prompt: Optional[str] = None):
    async def dependency(matcher: Matcher, event: Event):
        if hasattr(event, 'group_id'):
            grp_id, user = event.group_id, event.user_id
            if (count := service.get_limit(grp_id, user)) >= times != 0:
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
        return f"<Rule of {self.service.plugin_name}>"


class GroupRule(ServiceRule):
    async def __call__(self, event: Event) -> bool:
        return is_able_in_group(self.service, event)

    def __repr__(self):
        return f"<GroupRule of {self.service.plugin_name}>"


def is_able_in_group(service: "Service", event: Event) -> bool:
    if hasattr(event, 'group_id'):
        return event.group_id not in service.disable_group if service.enable_on_default \
            else event.group_id in service.enable_group
    return True
