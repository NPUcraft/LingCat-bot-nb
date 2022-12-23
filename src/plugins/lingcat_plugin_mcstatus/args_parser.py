from nonebot.rule import ArgumentParser

mc_parser = ArgumentParser("mc")

mc_subparsers = mc_parser.add_subparsers(dest="handle")

list_parser = mc_subparsers.add_parser("list", help="查看MC服务器列表")
list_group = list_parser.add_mutually_exclusive_group()
list_group.add_argument(
    "-u", "--user", action="append", nargs="?", default=[], type=int
)
list_group.add_argument(
    "-g", "--group", action="append", nargs="?", default=[], type=int
)
list_group.add_argument(
    "-c", "--channel", action="append", nargs="?", default=[], type=int
)

ping_parser = mc_subparsers.add_parser("ping", help="查看MC服务器ping")
ping_parser.add_argument("ip", type=str, nargs="?", default="default", help="MC服务器ip地址")

online_parser = mc_subparsers.add_parser("online", help="查看MC服务器在线人数")
online_parser.add_argument(
    "ip", type=str, nargs="?", default="default", help="MC服务器ip地址"
)

add_parser = mc_subparsers.add_parser("add", help="添加MC服务器")
add_parser.add_argument("name", type=str, help="服务器名称")
add_parser.add_argument("ip", type=str, help="MC服务器ip地址")
add_parser.add_argument("-u", "--user", action="store", nargs="+", default=[], type=int)
add_parser.add_argument(
    "-g", "--group", action="store", nargs="+", default=[], type=int
)
add_parser.add_argument(
    "-c", "--channel", action="store", nargs="+", default=[], type=int
)

remove_parser = mc_subparsers.add_parser("remove", help="移除MC服务器")
remove_parser.add_argument("name", type=str, help="服务器名称")
remove_parser.add_argument(
    "-u", "--user", action="store", nargs="+", default=[], type=int
)
remove_parser.add_argument(
    "-g", "--group", action="store", nargs="+", default=[], type=int
)
remove_parser.add_argument(
    "-c", "--channel", action="store", nargs="+", default=[], type=int
)
