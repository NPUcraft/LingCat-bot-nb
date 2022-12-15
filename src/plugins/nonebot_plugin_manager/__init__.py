from argparse import Namespace

import nonebot
from nonebot.matcher import Matcher
from nonebot.params import ShellCommandArgs
from nonebot.message import run_preprocessor
from nonebot.exception import IgnoredException
from nonebot.plugin import on_shell_command, get_loaded_plugins, PluginMetadata
from nonebot.adapters.onebot.v11 import (
    Bot,
    Event,
    MessageEvent,
    GroupMessageEvent,
    GROUP,
    PRIVATE,
)

from nonebot_plugin_guild_patch import GuildMessageEvent

from .args_parser import npm_parser
from .manager import plugin_manager
from .handle import Handle

cmd_start = sorted(list(nonebot.get_driver().config.command_start))[0]

__plugin_meta__ = PluginMetadata(
    name="Nonebot2 Plugins Manager",
    description="用于插件管理",
    usage=f"""欢迎使用NPM
本插件提供管理机器人插件开关、读写执行(rwx)权限能力
可用命令前缀：{" ".join(list(nonebot.get_driver().config.command_start))}

{cmd_start}npm info   # 查看当前会话插件列表
        * -u user_id    # 查看指定用户插件列表（仅超级用户）
        * -g group_id   # 查看指定群插件列表（仅超级用户）
        * -a   # 查看所有插件

{cmd_start}npm off/on <插件名> ...   # 关闭/开启当前会话插件（管理员权限）
        * -a   # 全选插件
        * -r   # 反选插件
        * -u user_id ...   # 管理指定用户插件（仅超级用户）
        * -g group_id ...   # 管理指定群插件（仅超级用户）
        
{cmd_start}npm chmod mode plugin ...   # 设置插件权限等级（仅超级用户）
        * mode   # 需要设置的权限，三位数字分别代表超级用户、私聊与群聊的权限等级
                   其中，4、2、1分别对应插件可见、插件权限可编辑和插件可执行权限
        * plugin   # 插件名
        * -a   # 全选插件
        * -r   # 反选插件""",
    extra={
        "version": "v1.0",
        "alias": ["npm", "管理插件", "管理"],
        "mode": "711",
    },
)

npm = on_shell_command("npm", parser=npm_parser, priority=1, permission=GROUP | PRIVATE)


@run_preprocessor
async def _(matcher: Matcher, bot: Bot, event: Event):

    plugin = matcher.plugin_name

    # 机器人被禁言则跳过
    bot_info = (
        await bot.get_group_member_info(group_id=event.group_id, user_id=event.self_id)
        if isinstance(event, GroupMessageEvent)
        else None
    )
    if bot_info and bot_info.get("shut_up_timestamp", 0) != 0:
        raise IgnoredException(
            f"Bot was banned! Nonebot_Plugin_Manager has blocked {plugin} !"
        )

    conv = {
        "user": [event.user_id] if hasattr(event, "user_id") else [],
        "group": [event.group_id] if hasattr(event, "group_id") else [],
        "channel": [event.channel_id] if hasattr(event, "channel_id") else [],
    }

    # SUPERUSER私聊
    if (
        hasattr(event, "user_id")
        and not hasattr(event, "group_id")
        and not hasattr(event, "channel_id")
        and str(event.user_id) in bot.config.superusers
    ):
        conv["user"] = []
        conv["group"] = []

    # 更新插件权限信息
    plugin_manager.update_plugin(
        {
            str(p.name): p.name != "nonebot_plugin_manager" and bool(p.matcher)
            for p in get_loaded_plugins()
        }
    )

    if not plugin_manager.get_plugin(conv=conv, perm=0b0001)[plugin]:
        raise IgnoredException(f"Nonebot_Plugin_Manager has blocked {plugin} !")


@npm.handle()
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
