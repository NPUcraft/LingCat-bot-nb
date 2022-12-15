from nonebot.rule import ArgumentParser

npm_parser = ArgumentParser("npm")

npm_subparsers = npm_parser.add_subparsers(dest="handle")

info_parser = npm_subparsers.add_parser("info", help="查看所有插件权限信息")
info_group = info_parser.add_mutually_exclusive_group()
info_group.add_argument(
    "-u", "--user", action="append", nargs="?", default=[], type=int
)
info_group.add_argument(
    "-g", "--group", action="append", nargs="?", default=[], type=int
)
info_group.add_argument(
    "-c", "--channel", action="append", nargs="?", default=[], type=int
)
info_group.add_argument("-a", "--all", action="store_true")

chmod_parser = npm_subparsers.add_parser("chmod", help="设置插件权限等级")
chmod_parser.add_argument("mode", type=str, help="权限等级")
chmod_parser.add_argument("plugin", nargs="*", help="待设置的插件名称")
chmod_parser.add_argument("-a", "--all", action="store_true")
chmod_parser.add_argument("-r", "--reverse", action="store_true")

off_parser = npm_subparsers.add_parser("off", help="关闭插件")
off_parser.add_argument("plugin", nargs="*", help="待关闭插件名")
off_parser.add_argument("-a", "--all", action="store_true")
off_parser.add_argument("-r", "--reverse", action="store_true")
off_parser.add_argument("-u", "--user", action="store", nargs="+", default=[], type=int)
off_parser.add_argument(
    "-g", "--group", action="store", nargs="+", default=[], type=int
)
off_parser.add_argument(
    "-c", "--channel", action="store", nargs="+", default=[], type=int
)

on_parser = npm_subparsers.add_parser("on", help="开启插件")
on_parser.add_argument("plugin", nargs="*", help="待开启插件名")
on_parser.add_argument("-a", "--all", action="store_true")
on_parser.add_argument("-r", "--reverse", action="store_true")
on_parser.add_argument("-u", "--user", action="store", nargs="+", default=[], type=int)
on_parser.add_argument("-g", "--group", action="store", nargs="+", default=[], type=int)
on_parser.add_argument(
    "-c", "--channel", action="store", nargs="+", default=[], type=int
)
