from abc import abstractmethod

from nonebot.adapters.onebot.v11 import GroupMessageEvent


class ServiceRule:
    __slots__ = ("service_name",)

    def __init__(self, service_name: str):
        self.service_name = service_name

    @abstractmethod
    async def __call__(self, *args, **kwargs) -> bool:
        ...

    def __repr__(self):
        return f"<Rule {self.service_name}>"


class GroupMessageRule(ServiceRule):
    async def __call__(self, event: GroupMessageEvent) -> bool:
        return True
