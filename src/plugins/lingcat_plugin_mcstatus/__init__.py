from argparse import Namespace

import nonebot
from nonebot.params import ShellCommandArgs
from nonebot.plugin import PluginMetadata, on_shell_command
from nonebot.adapters.onebot.v11 import (
    Bot,
    MessageEvent,
    GroupMessageEvent,
    GROUP,
    PRIVATE,
)

from nonebot_plugin_guild_patch import GuildMessageEvent

from .handle import Handle
from .args_parser import mc_parser

cmd_start = sorted(list(nonebot.get_driver().config.command_start))[0]

__plugin_meta__ = PluginMetadata(
    name="MC状态查询",
    description="查询MC[JE]服务器ping及在线人数",
    usage=f"""欢迎使用MC状态查询插件
可用命令前缀：{" ".join(list(nonebot.get_driver().config.command_start))}

{cmd_start}mc ping [ip]  # 查看MC服务器ping值
        * ip   # 可选参数，服务器ip地址，默认值为当前会话默认服务器地址

{cmd_start}mc online [ip]  # 查看MC服务器在线玩家
        * ip   # 可选参数，服务器ip地址，默认值为当前会话默认服务器地址

{cmd_start}mc list ...   # 查看当前会话关注的MC服务器
        * -u user_id ...   # 查看指定用户关注的服务器（仅超级用户）
        * -g group_id ...   # 查看指定群关注的服务器（仅超级用户）

{cmd_start}mc add name ip ...  # 为当前会话关注MC服务器（管理员权限）
        * name   # 服务器名称
        * ip   # 服务器ip地址
        * -u user_id ...   # 为指定用户关注服务器（仅超级用户）
        * -g group_id ...   # 为指定群关注服务器（仅超级用户）
        
{cmd_start}mc remove name ...  # 为当前会话删除指定MC服务器（管理员权限）
        * name   # 服务器名称
        * -u user_id ...   # 为指定用户关注服务器（仅超级用户）
        * -g group_id ...   # 为指定群关注服务器（仅超级用户）""",
    extra={
        "version": "v1.0",
        "alias": ["mc", "mc状态查询"],
        "mode": "757",
    },
)

mc = on_shell_command("mc", parser=mc_parser, priority=50, permission=GROUP | PRIVATE)


@mc.handle()
async def _(bot: Bot, event: MessageEvent, args: Namespace = ShellCommandArgs()):
    args.conv = {
        "user": [event.user_id],
        "group": [event.group_id] if isinstance(event, GroupMessageEvent) else [],
        "channel": [event.channel_id] if isinstance(event, GuildMessageEvent) else [],
    }

    args.is_admin = (
        event.sender.role in ["admin", "owner"]
        if isinstance(event, GroupMessageEvent)
        else False
    )

    args.is_superuser = str(event.user_id) in bot.config.superusers

    if hasattr(args, "handle"):
        if args.handle == None:
            message = __plugin_meta__.usage
        else:
            message = getattr(Handle, args.handle)(args)
        if message:
            await bot.send(event, message)
