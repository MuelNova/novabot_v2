import json

from pathlib import Path
from typing import Type, Dict, Any, Optional, Set

from nonebot.log import logger
from nonebot.internal.matcher import Matcher, MatcherMeta

from .data_source import GlobalVar as gV
from .rule import GroupMessageRule
from ...utils import _load_file, _save_file


class Service:
    plugin_name: str
    matcher: Type[Matcher]
    use_priv: Optional[int]
    manage_priv: Optional[int]
    enable_on_default: Optional[bool]
    visible: Optional[bool]
    help: Optional[str]
    enable_group: Set[int]
    disable_group: Set[int]

    def __init__(self,
                 plugin_name: str,
                 matcher: Type[Matcher],
                 use_priv=None,
                 manage_priv=None,
                 enable_on_default=None,
                 visible: Optional[bool] = None,
                 help_: Optional[str] = None,
                 bundle: Optional[str] = None):
        """
        将一个matcher进行包装，成为可控制的Service对象

        :param plugin_name: 插件名
        :param matcher: 需要包装的matcher
        :param use_priv: 使用权限，默认值: 所有成员
        :param manage_priv: 管理权限，默认值：群管理
        :param enable_on_default: 默认启用，默认值: True
        :param visible: 是否可见，默认值: True
        :param help_: 帮助文档，默认值: None
        :param bundle: 插件分类，默认值: '默认'
        """
        if not isinstance(matcher, MatcherMeta):
            raise TypeError(f"matcher excepted yet {type(matcher)} found.")
        self.plugin_name = plugin_name
        self.matcher = matcher
        config = self._load_config()
        # To-Do: Finish Permission Enum
        """
        In this version, We set use_priv in on_* function using arg 'permission'
        We firstly set the manage_priv as '>=GROUP_ADMIN'
        """
        self.use_priv = config.get('use_priv') or use_priv or 0
        self.manage_priv = config.get('manage_priv') or manage_priv or 0
        # End To-Do
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
        self.help = help_
        self.enable_group = set(config.get('enable_group', []))
        self.disable_group = set(config.get('disable_group', []))

        self.matcher.rule &= GroupMessageRule(self)

        gV.loaded_service[self.plugin_name] = self
        gV.service_bundle[bundle or '默认'].append(self)

    def __repr__(self):
        return f"<Service '{self.matcher.plugin_name}'," \
               f" use_priv={self.use_priv}," \
               f" manage_priv={self.manage_priv}," \
               f" enable_on_default={self.enable_on_default}," \
               f" visible={self.visible}>"

    def __getattr__(self, item):
        return getattr(self.matcher, item)

    def _load_config(self) -> Dict[str, Any]:
        path = Path.cwd() / "novabot" / "plugin_config" / "service_manager" / f"{self.plugin_name}.json"
        if not path.parent.exists():
            path.parent.mkdir(parents=True)
        return json.loads(_load_file(path) or "{}")

    def _save_config(self):
        path = Path.cwd() / "novabot" / "plugin_config" / "service_manager" / f"{self.plugin_name}.json"
        if not path.parent.exists():
            path.parent.mkdir(parents=True)
        _save_file(path,
                   {
                       "plugin_name": self.plugin_name,
                       "use_priv": self.use_priv,
                       "manage_priv": self.manage_priv,
                       "enable_on_default": self.enable_on_default,
                       "visible": self.visible,
                       "enable_group": list(self.enable_group),
                       "disable_group": list(self.disable_group)
                   })

    def set_enable(self, group_id: int):
        self.enable_group.add(group_id)
        self.disable_group.discard(group_id)
        self._save_config()
        logger.info(f'Service {self.plugin_name} is enabled at group {group_id}')

    def set_disable(self, group_id: int):
        self.disable_group.add(group_id)
        self.enable_group.discard(group_id)
        self._save_config()
        logger.info(f'Service {self.plugin_name} is disabled at group {group_id}')

    @staticmethod
    def get_loaded_services() -> Dict[str, "Service"]:
        return gV.loaded_service
