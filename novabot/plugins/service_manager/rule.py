from abc import abstractmethod

from nonebot.adapters.onebot.v11 import Event


class ServiceRule:
    __slots__ = ("service",)

    def __init__(self, service: "Service"):
        self.service = service

    @abstractmethod
    async def __call__(self, *args, **kwargs) -> bool:
        ...

    def __repr__(self):
        return f"<Rule of {self.service.plugin_name}>"


class GroupRule(ServiceRule):
    async def __call__(self, event: Event) -> bool:
        return is_able_in_group(self.service, event)


def is_able_in_group(service: "Service", event: Event) -> bool:
    if hasattr(event, 'group_id'):
        return event.group_id not in service.disable_group if service.enable_on_default \
            else event.group_id in service.enable_group
    return True
