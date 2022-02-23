from nonebot.rule import ArgumentParser

list_parser = ArgumentParser("ls")

list_parser.add_argument("-d", "--details", action="store_true", help="show plugin with matcher list")
list_parser.add_argument("-u", "--user", action="store", type=str)
list_parser.add_argument("-g", "--group", action="store", type=str)

chmod_parser = ArgumentParser("chmod")

chmod_parser.add_argument("mode", type=str, help="mode you want to set", action="store")
chmod_parser.add_argument("-p", "--plugin", nargs="*", help="plugin you want to set")
chmod_parser.add_argument("-m", "--matcher", nargs="*", help="matcher you want to set")
chmod_parser.add_argument("-g", "--group", action="append")
chmod_parser.add_argument("-u", "--user", action="append")
