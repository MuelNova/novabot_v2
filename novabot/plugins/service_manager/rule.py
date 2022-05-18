from abc import abstractmethod
from datetime import datetime
from typing import Optional

from nonebot.rule import Rule
from nonebot.typing import T_State
from nonebot.adapters.onebot.v11 import Event, Bot



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


class OnlyRule(ServiceRule):
    @abstractmethod
    async def __call__(self, *args, **kwargs) -> bool:
        raise NotImplementedError

    async def is_correct_event(self, bot: Bot, event: Event, state: T_State) -> bool:
        """
        Improvable.

        There'll have 2*n-1 rules to be checked.
        Absolutely a waste.
        """
        rule = Rule()
        for checker in self.service.rule.checkers:
            if isinstance(checker.call, OnlyRule):
                continue
            rule &= checker
        return await rule(bot, event, state)


class CDRule(OnlyRule):

    def __init__(self, service: "Service", reply: Optional[str] = None):
        super().__init__(service)
        self.service = service
        self.reply = reply

    async def __call__(self, event: Event, bot: Bot, state: T_State) -> bool:
        result = await self.is_correct_event(bot, event, state)
        if not result:
            return False
        if hasattr(event, 'group_id') and hasattr(event, 'user_id'):
            ts = datetime.now().timestamp()
            if ts < (cd_ts := self.service.get_cd(event.group_id, event.user_id)) and cd_ts != 0:
                if self.reply:
                    await bot.send(event, self.reply)
                return False
            self.service.set_cd(event.group_id, event.user_id, ts+self.service.cd)
        return True

    def __repr__(self):
        return f"<CD Rule of {self.service.plugin_name}>"


class LimitRule(OnlyRule):

    def __init__(self, service: "Service", reply: Optional[str] = None):
        super().__init__(service)
        self.service = service
        self.reply = reply

    async def __call__(self, event: Event, bot: Bot, state: T_State) -> bool:
        result = await self.is_correct_event(bot, event, state)
        if not result:
            return False
        if hasattr(event, 'group_id') and hasattr(event, 'user_id'):
            count = self.service.get_limit(event.group_id, event.user_id)
            if count >= self.service.limit != 0:
                if self.reply:
                    await bot.send(event, self.reply)
                return False
            self.service.set_limit(event.group_id, event.user_id, count+1)
        return True

    def __repr__(self):
        return f"<Limit Rule of {self.service.plugin_name}>"


def is_able_in_group(service: "Service", event: Event) -> bool:
    if hasattr(event, 'group_id'):
        return event.group_id not in service.disable_group if service.enable_on_default \
            else event.group_id in service.enable_group
    return True
