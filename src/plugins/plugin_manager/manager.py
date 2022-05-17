import yaml
from argparse import Namespace
from pathlib import Path
from typing import Dict, List, Union, Optional, Tuple
from nonebot.adapters.onebot.v11 import Event, Bot

Conv = Dict[str, List[int]]

switch_txt: Dict[str, str] = {"0": "×", "1": "√"}


class PluginManager:
    __path: Path
    __plugin_list: Dict[str, Dict]

    def __init__(self, path: Path = Path() / "data" / "manager" / "plugin_list.yml"):
        self.__path = path
        self.__load()

    def __load(self) -> "PluginManager":
        try:
            self.__plugin_list = yaml.safe_load(self.__path.open("r", encoding="utf-8"))
        except:
            self.__plugin_list = {}
        return self

    def __dump(self):
        self.__path.parent.mkdir(parents=True, exist_ok=True)
        yaml.dump(
            self.__plugin_list,
            self.__path.open("w", encoding="utf-8"),
            allow_unicode=True,
        )

    def add_plugin(self, plugin_name: str, matcher_name: Optional[str] = None):
        if not self.__plugin_list.get(plugin_name):
            self.__plugin_list[plugin_name] = {
                "mode": "111",
                "user": {},
                "group": {},
                "matchers": {}
            }
        if matcher_name and not self.__plugin_list[plugin_name]['matchers'].get(
            matcher_name
        ):
            self.__plugin_list[plugin_name]['matchers'][matcher_name] = {
                "mode": "111",
                "user": {},
                "group": {},
            }

        self.__dump()

    def is_plugin_available(self, plugin_name: str, bot: Bot, event: Event) -> bool:
        status = self.__plugin_list[plugin_name]
        role = self.get_role(bot, event)
        if hasattr(event, "user_id"):
            if hasattr(event, "group_id"):
                if group_status := status['group'].get(str(event.group_id)):
                    if (u_status := group_status.get(str(event.user_id))) == ("1" or "0"):
                        return bool(int(u_status))
                    return bool(int(group_status["0"][role]))
            elif (u_status := status['user'].get(str(event.user_id))) == ("1" or "0"):
                return bool(int(u_status))
        return bool(int(status['mode'][role]))

    def is_matcher_available(self, plugin_name: str, matcher_name: str, bot: Bot, event: Event) -> bool:
        if not self.is_plugin_available(plugin_name, bot, event):
            return False
        status = self.__plugin_list[plugin_name]['matchers'][matcher_name]
        role = self.get_role(bot, event)
        if hasattr(event, "user_id"):
            if hasattr(event, "group_id"):
                if group_status := status['group'].get(str(event.group_id)):
                    if (u_status := group_status.get(str(event.user_id))) in ["1", "0"]:
                        return bool(int(u_status))
                    return bool(int(group_status["0"][role]))
            elif (u_status := status['user'].get(str(event.user_id))) in ["1", "0"]:
                return bool(int(u_status))
        return bool(int(status['mode'][role]))

    @staticmethod
    def get_role(bot: Bot, event: Event) -> int:
        """
        :param bot:
        :param event:
        :return: 0: SUPERUSER
                 1: OWNER / GROUP_ADMIN
                 2: USER
        """
        if hasattr(event, "user_id"):
            user = str(event.user_id)
            if user in bot.config.superusers:
                return 0
            if hasattr(event, "group_id") and hasattr(event, "sender"):
                role = event.sender.role
                if role in ['owner', 'admin']:
                    return 1
        return 2

    def get_rauth_in_group(self, args: Namespace) -> str:
        group = args.group
        details = args.details
        msg = f"群 {group} 的功能情况\n\n"

        for plugin in self.__plugin_list:
            grp_status = self.__plugin_list[plugin]['group'].get(group)
            msg += "|"
            if grp_status and (grp_general_status := grp_status.get('0')):
                msg += "-".join(switch_txt[grp_general_status[i]] for i in range(3))
            else:
                msg += "-".join(switch_txt[self.__plugin_list[plugin]['mode'][i]] for i in range(3))
            msg += f"| {plugin}\n"
            if details:
                for matcher in self.__plugin_list[plugin].get('matchers'):
                    grp_status = self.__plugin_list[plugin]['matchers'][matcher]['group'].get(group)
                    msg += " ├─|"
                    if grp_status and (grp_general_status := grp_status.get('0')):
                        msg += "-".join(switch_txt[grp_general_status[i]] for i in range(3))
                    else:
                        msg += "-".join(switch_txt[self.__plugin_list[plugin]['matchers'][matcher]['mode'][i]] for i in range(3))
                    msg += f"| {plugin} - {matcher}\n"
        msg += "\n|超级管理员 - 管理员/群主 - 群员|"
        return msg

    def get_user_rauth_in_group(self, args: Namespace) -> str:
        user = args.user
        group = args.group
        details = args.details
        if args.is_superuser:
            role = 0
        elif args.is_admin:
            role = 1
        else:
            role = 2
        msg = f"用户 {user} 在群 {group} 中的功能情况\n\n"

        for plugin in self.__plugin_list:

            if grp_status := self.__plugin_list[plugin]['group'].get(group):
                if usr_status := grp_status.get(user):
                    p_status = switch_txt[usr_status]
                elif grp_general_status := grp_status.get('0'):
                    p_status = switch_txt[grp_general_status[role]]
                else:
                    p_status = switch_txt[self.__plugin_list[plugin]['mode'][role]]
            else:
                p_status = switch_txt[self.__plugin_list[plugin]['mode'][role]]

            msg += f"|{p_status}| {plugin}\n"
            if details:
                for matcher in self.__plugin_list[plugin].get('matchers'):

                    if grp_status := self.__plugin_list[plugin]['matchers'][
                        matcher
                    ]['group'].get(group):
                        if usr_status := grp_status.get(user):
                            p_status = switch_txt[usr_status]
                        elif grp_general_status := grp_status.get('0'):
                            p_status = switch_txt[grp_general_status[role]]
                        else:
                            p_status = switch_txt[self.__plugin_list[plugin]['matchers'][matcher]['mode'][role]]
                    else:
                        p_status = switch_txt[self.__plugin_list[plugin]['matchers'][matcher]['mode'][role]]
                    msg += f" ├─|{p_status}| {plugin} - {matcher}\n"
        return msg

    def get_user_rauth(self, args: Namespace) -> str:
        user = args.user
        details = args.details
        if args.is_superuser:
            role = 0
        elif args.is_admin:
            role = 1
        else:
            role = 2
        msg = f"用户 {user} 的功能情况\n\n"

        for plugin in self.__plugin_list:
            if usr_status := self.__plugin_list[plugin]['user'].get(user):
                p_status = switch_txt[usr_status]
            else:
                p_status = switch_txt[self.__plugin_list[plugin]['mode'][role]]

            msg += f"|{p_status}| {plugin}\n"
            if details:
                for matcher in self.__plugin_list[plugin].get("matchers"):
                    if usr_status := self.__plugin_list[plugin]['matchers'][
                        matcher
                    ]['user'].get(user):
                        p_status = switch_txt[usr_status]
                    else:
                        p_status = switch_txt[self.__plugin_list[plugin]['matchers'][matcher]['mode'][role]]

                    msg += f" ├─|{p_status}| {plugin} - {matcher}\n"

        return msg

    def update_plugin(
            self,
            plugin_name: str,
            data: Union[str, Dict[str, str]],
            type_: int = 0,
            is_matcher: int = 0,
            matcher_name: str = None
    ):
        """
        :param is_matcher:
        :param matcher_name:
        :param data: type_ 0: str,
                     type_ 1: Dict[str, str]
                     type_ 2: Dict[str, str]
        :param plugin_name:
        :param type_: 0: GLOBAL
                      1: USER
                      2: GROUP
        :return:
        """
        if not self.__plugin_list.get(plugin_name):
            return f"Value Error:\n No Plugin {plugin_name} Found!"

        if is_matcher:
            if not self.__plugin_list[plugin_name]['matchers'].get(matcher_name):
                return f"Value Error:\n No Matcher {plugin_name} - {matcher_name} Found!"
            obj = self.__plugin_list[plugin_name]['matchers'][matcher_name]
            full_name = f"{plugin_name} - {matcher_name}"
        else:
            obj = self.__plugin_list[plugin_name]
            full_name = plugin_name

        if type_ == 0:
            mode = data
            obj['mode'] = mode
        elif type_ == 1:
            usr = data.get('user')
            mode = data.get('data')
            obj['user'][usr] = mode
        else:
            grp = data.get('group')
            usr = data.get('user')
            mode = data.get('data')

            grp_data = obj['group'].get(grp, dict())
            grp_data[usr] = mode
            obj['group'][grp] = grp_data
        self.__dump()
        return f"{full_name} has been successfully changed to {mode}"

    @staticmethod
    def gen_data(mode: str, usr: str = None, grp: str = None) -> Tuple[int, Union[str, Dict[str, str]]]:
        if not usr:
            return (2, {'group': grp, 'user': '0', 'data': mode}) if grp else (0, mode)
        if not grp:
            return 1, {'user': usr, 'data': mode}
        return 2, {'group': grp, 'user': usr, 'data': mode}
