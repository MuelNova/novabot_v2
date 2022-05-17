from argparse import Namespace

from . import PluginManager


class Handle:
    @classmethod
    def ls(cls, args: Namespace) -> str:
        plugin_manager = PluginManager()
        if args.user and args.group:
            return plugin_manager.get_user_rauth_in_group(args)
        elif args.group:
            return plugin_manager.get_rauth_in_group(args)
        elif args.user:
            return plugin_manager.get_user_rauth(args)
        elif args.conv.get("group"):
            args.group = str(args.conv["group"][0])
            return plugin_manager.get_rauth_in_group(args)
        else:
            args.user = str(args.conv["user"][0])
            return plugin_manager.get_user_rauth(args)

    @classmethod
    def chmod(cls, args: Namespace) -> str:
        plugin_manager = PluginManager()
        chmod_dict = {'+x': '1', '^x': '0'}

        if not args.plugin:
            return "Value Error:\n  No Plugin Selected!"
        if len(args.plugin) > 1 and args.matcher and len(args.matcher) > 1:
            return "Index Error:\n  Multiple Plugins and Matchers Found!"
        if len(args.mode) not in [1, 2, 3]:
            return "Value Error:\n  Unknown Mode Length!"
        if not (args.user and args.group):
            if args.conv.get("group"):
                args.group = str(args.conv["group"][0])
            else:
                args.user = str(args.conv["user"][0])

        if (len(args.mode) == 2 and args.mode in ['+x', '^x']) or (len(args.mode) == 1 and args.mode in ["0", "1"]):
            mode = args.mode*3 if len(args.mode) == 1 else chmod_dict[args.mode]*3
        else:
            mode = "".join(i if i in ["0", "1"] else '1' for i in args.mode)
        if args.user or (not args.conv.get('group') and args.conv.get('user')):
            mode = mode[0]
        msg = ""
        if not args.matcher:
            for plugin in args.plugin:

                type_, data = plugin_manager.gen_data(mode, args.user, args.group)
                msg += plugin_manager.update_plugin(plugin, data, type_) + "\n\n"
        else:
            plugin = args.plugin[0]
            for matcher in args.matcher:
                type_, data = plugin_manager.gen_data(mode, args.user, args.group)
                msg += plugin_manager.update_plugin(plugin, data, type_, is_matcher=True, matcher_name=matcher)

        return msg

