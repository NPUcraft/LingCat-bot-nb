import nonebot
from nonebot import on_command
from nonebot.matcher import Matcher
from nonebot.params import Arg, CommandArg
from nonebot.adapters import Event
from nonebot.adapters.onebot.v11 import GroupMessageEvent, GROUP, PRIVATE
from nonebot.adapters.onebot.v11.message import Message, MessageSegment

from nonebot_plugin_guild_patch import GuildMessageEvent

# from nonebot import require

# require("src.plugins.nonebot_plugin_manager")
from src.plugins.nonebot_plugin_manager import Handle

cmd_start = list(nonebot.get_driver().config.command_start)[0]
helper = on_command("help", priority=1, aliases={"帮助"}, permission=GROUP | PRIVATE)


@helper.handle()
async def handle_no_content(
    event: Event, matcher: Matcher, args: Message = CommandArg()
):
    if args:
        matcher.set_arg("content", args)
    else:
        # 构造会话信息
        conv = {
            "user": [event.user_id],
            "group": [event.group_id] if isinstance(event, GroupMessageEvent) else [],
            "channel": [event.channel_id]
            if isinstance(event, GuildMessageEvent)
            else [],
        }
        if conv["group"]:
            conv["user"] = []
        elif conv["channel"]:
            conv["user"] = []
        # elif str(event.user_id) in nonebot.get_driver().config.superusers:
        #     args.conv["user"] = []

        plugin_dict = Handle.get_readable_plugins(conv)

        plugin_info_dict = {}
        plugin_set = nonebot.get_loaded_plugins()
        plugin_names = []
        for plugin in plugin_set:
            if plugin.name not in plugin_dict:
                continue
            plugin_info_dict[plugin.name] = plugin

        for plugin in plugin_dict:
            name = f"[{'o'if plugin_dict[plugin] else 'x'}] "
            try:
                name += plugin_info_dict[plugin].metadata.name
            except:
                name += plugin

            try:
                version = plugin_info_dict[plugin].metadata.extra.get("version", "v1.0")
            except:
                version = "v1.0"

            plugin_names.append(f"{name} | {version}")
        newline = "\n"
        result = (
            f"{' '+list(nonebot.get_driver().config.nickname)[0]+'功能一览 ':=^16}"
            + f"\n{newline.join(plugin_names)}"
        )

        await helper.finish(MessageSegment.text(result))


@helper.got("content")
async def handle_get_content(event: Event, content: Message = Arg()):
    arg = content.extract_plain_text().strip()
    plugin = nonebot.get_plugin(arg)
    if not plugin:
        plugin_set = nonebot.get_loaded_plugins()
        for p in plugin_set:
            try:
                plugin_alias = p.metadata.extra.get("alias", [])
            except:
                plugin_alias = []
            finally:
                try:
                    plugin_alias.append(p.metadata.name)
                except:
                    plugin_alias.append(p.name)

            if arg.lower() in plugin_alias:
                plugin = p

    # not found 404
    if not plugin:
        result = f"{arg} 不存在或未加载，请输入正确的插件名"
    else:
        results = []
        if plugin.metadata and plugin.metadata.name and plugin.metadata.usage:
            results.extend(
                [
                    f"{plugin.metadata.name}:{plugin.metadata.description}",
                    plugin.metadata.usage,
                ]
            )
        else:
            results.append("开发者暂未提供该插件的使用说明！")

        result = "\n".join(results)

    await helper.finish(MessageSegment.text(result))
