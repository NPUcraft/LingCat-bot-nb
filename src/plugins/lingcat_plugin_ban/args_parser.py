from nonebot.rule import ArgumentParser
from nonebot.adapters.onebot.v11.message import MessageSegment

ban_parser = ArgumentParser("ban")

ban_parser.add_argument("target", nargs="*",help="用户ID")
ban_parser.add_argument(
    "-r",
    "--reason",
    "-原因",
    "-封禁原因",
    "-理由",
    "-封禁理由",
    default="违反友好使用机器人规定",
    type=str,
    nargs="*",
    help="封禁原因",
    dest="reason",
)

unban_parser = ArgumentParser("unban")

unban_parser.add_argument("target", nargs="*",  help="用户ID")
