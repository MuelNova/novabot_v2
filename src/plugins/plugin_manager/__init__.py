from argparse import Namespace

from nonebot import get_driver, on_shell_command, get_loaded_plugins
from nonebot.adapters.onebot.v11 import Event, Bot, MessageEvent, GroupMessageEvent
from nonebot.dependencies import Dependent
from nonebot.exception import IgnoredException, ParserExit
from nonebot.matcher import Matcher
from nonebot.log import logger
from nonebot.message import run_preprocessor
from nonebot.params import ShellCommandArgs
from nonebot.rule import CommandRule, ShellCommandRule

from .manager import PluginManager
from .parser import list_parser, chmod_parser
from .handler import Handle

driver = get_driver()

ls = on_shell_command("ls", parser=list_parser, priority=1)
chmod = on_shell_command("chmod", parser=chmod_parser, priority=1)


@run_preprocessor
async def _(matcher: Matcher, bot: Bot, event: Event):
    try:
        plugin, matcher_name = matcher.plugin_name, get_matcher_name(matcher)
        plugin_manager = PluginManager()

        plugin_manager.add_plugin(plugin, matcher_name)

        if not plugin_manager.is_matcher_available(plugin, matcher_name, bot, event):
            raise IgnoredException(f"Plugin Manager has blocked {plugin}{matcher_name} !")
    except ParserExit as e:
        message = e.message
        await bot.send(event, message)


@ls.handle()
async def _(bot: Bot, event: MessageEvent, args: Namespace = ShellCommandArgs()):
    try:
        draw_args(bot, event, args)

        message = Handle.ls(args)
        if message:
            await bot.send(event, message)
    except ParserExit as e:
        message = e.message
        await bot.send(event, message)


@chmod.handle()
async def _(bot: Bot, event: MessageEvent, args: Namespace = ShellCommandArgs()):
    try:
        draw_args(bot, event, args)

        message = Handle.chmod(args)
        if message:
            await bot.send(event, message)
    except ParserExit as e:
        message = e.message
        await bot.send(event, message)


@driver.on_startup
async def _():
    for plugin in get_loaded_plugins():
        for matcher in plugin.matcher:
            matcher_name = get_matcher_name(matcher())
            plugin_manager = PluginManager()

            plugin_manager.add_plugin(plugin.name, matcher_name)


def draw_args(bot: Bot, event: MessageEvent, args: Namespace) -> Namespace:
    args.conv = {
        "user": [event.user_id],
        "group": [event.group_id] if isinstance(event, GroupMessageEvent) else [],
    }
    args.is_admin = (
        event.sender.role in ["admin", "owner"]
        if isinstance(event, GroupMessageEvent)
        else False
    )
    args.is_superuser = str(event.user_id) in bot.config.superusers
    return args


def get_matcher_name(matcher: Matcher) -> str:
    matcher_name = '-'
    for checker in matcher.rule.checkers:
        if isinstance(checker, Dependent) and isinstance(
            checker.call, (CommandRule, ShellCommandRule)
        ):
            cmds = [x[0] for x in checker.call.cmds]
            cmds.sort()
            matcher_name = cmds[0]
            return matcher_name
    return matcher_name

