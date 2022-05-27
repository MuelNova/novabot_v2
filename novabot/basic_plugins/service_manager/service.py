import json
from datetime import date
from pathlib import Path
from typing import Type, Dict, Any, Optional, Set, Union, List, Callable

from nonebot.internal.matcher import Matcher, MatcherMeta
from nonebot.log import logger
from nonebot.typing import T_Handler

from novabot.utils.utils import load_file, save_file
from .data_source import GlobalVar as gV
from .rule import GroupRule, cooldown, limitation


class Service:
    service_name: str
    matcher: Type[Matcher]
    use_priv: int
    manage_priv: int
    enable_on_default: bool
    visible: bool
    help: str
    enable_group: Set[int]
    disable_group: Set[int]
    cd: int
    limit: int
    cd_reply: Optional[str]
    limit_reply: Optional[str]
    cd_list: Optional[Dict[str, Dict[str, Union[float, int]]]]
    limit_list: Optional[Dict[str, Union[Dict[str, Union[float, int]], str]]]

    def __init__(self,
                 service_name: str,
                 matcher: Type[Matcher],
                 use_priv: Optional[int] = None,
                 manage_priv: Optional[int] = None,
                 enable_on_default: Optional[bool] = None,
                 visible: Optional[bool] = None,
                 help_: Optional[str] = None,
                 bundle: Optional[str] = None,
                 cd: Optional[int] = None,
                 limit: Optional[int] = None,
                 cd_reply: Optional[str] = None,
                 limit_reply: Optional[str] = None):
        """
        将一个matcher进行包装，成为可控制的Service对象

        :param service_name: 插件名
        :param matcher: 需要包装的matcher
        :param use_priv: 使用权限，默认值: 所有成员
        :param manage_priv: 管理权限，默认值：群管理
        :param enable_on_default: 是否默认启用，默认值: True
        :param visible: 是否可见，默认值: True
        :param help_: 帮助文档，默认值: None
        :param bundle: 插件分类，默认值: '默认'
        :param cd: 插件调用CD，单位为秒，默认值: 0
        :param limit: 插件调用限制，单位为次，0为无限制，默认值: 0
        :param cd_reply: 插件冷却时回复，空为不回复，默认值: 空
        :param limit_reply: 插件调用限制时回复，空为不回复，默认值: 空

        """

        if not isinstance(matcher, MatcherMeta):
            raise TypeError(f"matcher excepted yet {type(matcher)} found.")
        self.service_name = service_name

        class service_matcher(matcher):
            @classmethod
            def handle(cls, parameterless: Optional[List[Any]] = None) -> Callable[[T_Handler], T_Handler]:
                if parameterless is None:
                    parameterless = []
                if self.cd > 0:
                    parameterless.append(cooldown(self, self.cd, self.cd_reply))
                if self.limit > 0:
                    parameterless.append(limitation(self, self.limit, self.limit_reply))
                return super().handle(parameterless)

        self.matcher = service_matcher
        config = self._load_config()
        # To-Do: Finish Permission Enum
        """
        In this version, We set use_priv in on_* function using arg 'permission'
        We firstly set the manage_priv as '>=GROUP_ADMIN'
        """
        self.use_priv = config.get('use_priv') or use_priv or 0
        self.manage_priv = config.get('manage_priv') or manage_priv or 0
        # End To-Do
        self.help = help_
        self.enable_group = set(config.get('enable_group', []))
        self.disable_group = set(config.get('disable_group', []))
        self.cd = config.get('cd') or cd or 0
        self.limit = config.get('limit') or limit or 0
        self.cd_reply = config.get('cd_reply') or cd_reply or ''
        self.cd_list = config.get('cd_list', {})
        self.limit_reply = config.get('limit_reply') or limit_reply or ''
        self.limit_list = config.get('limit_list', {"date": str(date.today())})

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

        self.matcher.rule &= GroupRule(self)
        """if self.cd > 0:
            self.matcher.rule &= CDRule(self, self.cd_reply)
        if self.limit > 0:
            self.matcher.rule &= LimitRule(self, self.limit_reply)"""

        gV.loaded_service[self.service_name] = self
        gV.service_bundle[bundle or '默认'].append(self)

    def __repr__(self):
        return f"<Service '{self.matcher.plugin_name}'," \
               f" use_priv={self.use_priv}," \
               f" manage_priv={self.manage_priv}," \
               f" enable_on_default={self.enable_on_default}," \
               f" visible={self.visible}," \
               f" cd={self.cd}," \
               f" limit={self.limit}>"

    def __getattr__(self, item):
        return getattr(self.matcher, item)

    def _load_config(self) -> Dict[str, Any]:
        path = Path.cwd() / "novabot" / "plugin_config" / "service_manager" / f"{self.service_name}.json"
        if not path.parent.exists():
            path.parent.mkdir(parents=True)
        return json.loads(load_file(path) or "{}")

    def _save_config(self):
        path = Path.cwd() / "novabot" / "plugin_config" / "service_manager" / f"{self.service_name}.json"
        if not path.parent.exists():
            path.parent.mkdir(parents=True)
        save_file(path,
                  {
                       "service_name": self.service_name,
                       "use_priv": self.use_priv,
                       "manage_priv": self.manage_priv,
                       "enable_on_default": self.enable_on_default,
                       "visible": self.visible,
                       "enable_group": list(self.enable_group),
                       "disable_group": list(self.disable_group),
                       "cd": self.cd,
                       "cd_reply": self.cd_reply,
                       "cd_list": self.cd_list,
                       "limit": self.limit,
                       "limit_reply": self.limit_reply,
                       "limit_list": self.limit_list
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

    def get_cd(self, group_id: int, user_id: int):
        return self.cd_list.get(str(group_id), {}).get(str(user_id), 0)

    def set_cd(self, group_id: int, user_id: int, timestamp: float):
        group_cd_list = self.cd_list.get(str(group_id), {})
        group_cd_list.update({str(user_id): timestamp})
        self.cd_list[str(group_id)] = group_cd_list
        self._save_config()

    def get_limit(self, group_id: int, user_id: int):
        if self.limit_list.get('date', '') != str(date.today()):
            self.limit_list = {"date": str(date.today())}
        return self.limit_list.get(str(group_id), {}).get(str(user_id), 0)

    def set_limit(self, group_id: int, user_id: int, counts: int):
        group_limit_list = self.limit_list.get(str(group_id), {})
        group_limit_list.update({str(user_id): counts})
        self.limit_list[str(group_id)] = group_limit_list
        self._save_config()
