from nonebot.adapters import Bot
from typing import Dict, Any

from argparse import Namespace
import nonebot
import time
from nonebot.matcher import Matcher
from nonebot.params import ShellCommandArgs, CommandStart
from nonebot.message import run_preprocessor, run_postprocessor
from nonebot.exception import IgnoredException
from nonebot.plugin import on_shell_command
from nonebot.adapters.onebot.v11.message import MessageSegment
from nonebot.adapters.onebot.v11 import (
    Bot,
    Event,
    MessageEvent,
    GroupMessageEvent,
    PrivateMessageEvent,
    GROUP,
    PRIVATE,
)

from nonebot_plugin_guild_patch import GuildMessageEvent

from .manager import BlacklistManager, UserInfo
from .args_parser import ban_parser, unban_parser

cmd_start = sorted(list(nonebot.get_driver().config.command_start))[0]
__plugin_meta__ = nonebot.plugin.PluginMetadata(
    name="Nonebot2 Plugins Bannnnn",
    description="加入黑名单（主要是刷屏自动被拉黑）",
    usage=f"""本插件提供机器人黑名单操作
可用命令前缀：{" ".join(list(nonebot.get_driver().config.command_start))}

{cmd_start}ban @某人 -r <封禁理由> # 拉黑某人
        * -r, --reason, -原因, -封禁原因, -理由, -封禁理由  # 可选参数，拉黑原因
{cmd_start}unban @某人  # 解除某人的封禁

P.S. 欢迎频繁刷屏被拉黑至机器人黑名单
由于各群之间独立，所以你有若干次被拉黑的机会呢~~""",
    extra={
        "version": "v1.0",
        "alias": ["ban", "刷屏拉黑", "刷屏", "拉黑"],
        "mode": "311",
    },
)

ban = on_shell_command(
    "ban", priority=5, aliases={"拉黑"}, parser=ban_parser, permission=GROUP | PRIVATE
)

unban = on_shell_command(
    "unban", priority=5, aliases={"解禁"}, parser=unban_parser, permission=GROUP | PRIVATE
)

warning_list = {"user": {}, "group": {}, "channel": {}}

# 黑名单人员无视
@run_preprocessor
async def _(matcher: Matcher, bot: Bot, event: Event):

    plugin = matcher.plugin_name

    # 获取黑名单列表
    if isinstance(event, GroupMessageEvent):
        blacklist = BlacklistManager().get_blacklist(group_id=event.group_id)
    elif isinstance(event, PrivateMessageEvent):
        blacklist = BlacklistManager().get_blacklist(user_id=event.user_id)
    elif isinstance(event, GuildMessageEvent):
        blacklist = BlacklistManager().get_blacklist(channel_id=event.channel_id)

    if hasattr(event, "user_id"):
        reason_or_not_in_blacklist = BlacklistManager().is_in_blacklist(
            event.user_id, blacklist
        )
        if reason_or_not_in_blacklist:

            # 提醒已被拉黑
            if isinstance(event, GroupMessageEvent):
                if event.group_id not in warning_list["group"]:
                    has_warned_list = []
                else:
                    has_warned_list = warning_list["group"][event.group_id]
                if event.user_id not in has_warned_list:
                    has_warned_list.append(event.user_id)
                    warning_list["group"][event.group_id] = has_warned_list
                    await bot.send(
                        event,
                        f"您由于【{reason_or_not_in_blacklist}】已被登记在不可使用机器人名录之上，请联系管理员解禁",
                        reply_message=True,
                    )
            elif isinstance(event, PrivateMessageEvent):
                has_warned_list = warning_list["user"]
                if event.user_id not in has_warned_list:
                    has_warned_list.append(event.user_id)
                    warning_list["user"] = has_warned_list
                    await bot.send(
                        event,
                        f"您由于【{reason_or_not_in_blacklist}】已被登记在不可使用机器人名录之上，请联系管理员解禁",
                        reply_message=True,
                    )
            elif isinstance(event, GuildMessageEvent):
                if event.channel_id not in warning_list["channel"]:
                    has_warned_list = []
                else:
                    has_warned_list = warning_list["channel"][event.channel_id]
                if event.user_id not in has_warned_list:
                    has_warned_list.append(event.user_id)
                    warning_list["channel"][event.channel_id] = has_warned_list
                    await bot.send(
                        event,
                        f"您由于【{reason_or_not_in_blacklist}】已被登记在不可使用机器人名录之上，请联系管理员解禁",
                        reply_message=True,
                    )

            raise IgnoredException(f"Nonebot_Plugin_Ban has blocked {plugin} !")


troublemaker_list = {"user": {}, "group": {}, "channel": {}}
cmd_flag = False
# 指令刷屏拉黑
@run_postprocessor
async def _ban(matcher: Matcher, bot: Bot, event: Event):
    global cmd_flag
    if not cmd_flag:
        return

    # 获取黑名单列表
    if isinstance(event, GroupMessageEvent):
        if event.group_id not in troublemaker_list["group"]:
            _troublemaker_list = {}
        else:
            _troublemaker_list = troublemaker_list["group"][event.group_id]
        troublemaker_list["group"][event.group_id] = _troublemaker_list

        # 用户行为：五秒触发五次命令则拉黑，第五次触发需要判定
        user_behavior = _troublemaker_list.get(event.user_id, [])
        user_behavior.append(event.time)
        if len(user_behavior) == 5:
            first_match_time = user_behavior.pop(0)
            troublemaker_list["group"][event.group_id][event.user_id] = user_behavior
            if event.time - first_match_time < 5:
                # 拉黑
                t = time.gmtime()
                BlacklistManager().add_blacklist(
                    UserInfo(
                        user_id=event.user_id,
                        date=time.strftime("%Y-%m-%d %H:%M:%S", t),
                        reason="群内频繁刷屏[自动处理]",
                    ),
                    group_id=event.group_id,
                )

                await bot.send(
                    event, "您在群内的刷指令行为，导致被登记在黑名单上，请联系管理员解禁", reply_message=True
                )
        else:
            troublemaker_list["group"][event.group_id][event.user_id] = user_behavior
    elif isinstance(event, PrivateMessageEvent):
        _troublemaker_list = troublemaker_list["user"]

        # 用户行为：五秒触发五次命令则拉黑，第五次触发需要判定
        user_behavior = _troublemaker_list.get(event.user_id, [])
        user_behavior.append(event.time)
        if len(user_behavior) == 5:
            first_match_time = user_behavior.pop(0)
            troublemaker_list["user"][event.user_id] = user_behavior
            if event.time - first_match_time < 5:
                # 拉黑
                t = time.gmtime()
                BlacklistManager().add_blacklist(
                    UserInfo(
                        user_id=event.user_id,
                        date=time.strftime("%Y-%m-%d %H:%M:%S", t),
                        reason="群内频繁刷屏[自动处理]",
                    ),
                    user_id=event.user_id,
                )

                await bot.send(
                    event, "您在群内的刷指令行为，导致被登记在黑名单上，请联系管理员解禁", reply_message=True
                )
        else:
            troublemaker_list["user"][event.user_id] = user_behavior
    elif isinstance(event, GuildMessageEvent):
        if event.channel_id not in troublemaker_list["channel"]:
            _troublemaker_list = {}
        else:
            _troublemaker_list = troublemaker_list["channel"][event.channel_id]
        troublemaker_list["channel"][event.channel_id] = _troublemaker_list

        # 用户行为：五秒触发五次命令则拉黑，第五次触发需要判定
        user_behavior = _troublemaker_list.get(event.user_id, [])
        user_behavior.append(event.time)
        if len(user_behavior) == 5:
            first_match_time = user_behavior.pop(0)
            troublemaker_list["channel"][event.channel_id][
                event.user_id
            ] = user_behavior
            if event.time - first_match_time < 5:
                # 拉黑
                t = time.gmtime()
                BlacklistManager().add_blacklist(
                    UserInfo(
                        user_id=event.user_id,
                        date=time.strftime("%Y-%m-%d %H:%M:%S", t),
                        reason="群内频繁刷屏[自动处理]",
                    ),
                    channel_id=event.channel_id,
                )

                await bot.send(
                    event, "您在群内的刷指令行为，导致被登记在黑名单上，请联系管理员解禁", reply_message=True
                )
        else:
            troublemaker_list["channel"][event.channel_id][
                event.user_id
            ] = user_behavior


@ban.handle()
async def _(bot: Bot, event: MessageEvent, args: Namespace = ShellCommandArgs()):

    user_id = event.user_id
    group_id = event.group_id

    args.is_admin = (
        event.sender.role in ["admin", "owner"]
        if isinstance(event, GroupMessageEvent)
        else False
    )

    args.is_superuser = str(event.user_id) in bot.config.superusers

    if not args.is_admin:
        if not args.is_superuser:
            await ban.finish("权限不足！")

    if not args.target:
        await ban.finish(__plugin_meta__.usage)
    else:

        ban_list = []
        for user in args.target:
            if isinstance(user, MessageSegment):  # 非纯文本
                if user.type == "at":
                    if user.data.get("qq") == "all":
                        await ban.finish("可恶，全体ban掉还不如给我禁言了算了！")
                    target_id = int(user.data.get("qq"))
                    t = time.gmtime()
                    if isinstance(event, GroupMessageEvent):
                        BlacklistManager().add_blacklist(
                            UserInfo(
                                user_id=target_id,
                                date=time.strftime("%Y-%m-%d %H:%M:%S", t),
                                reason=",".join(args.reason)
                                if isinstance(args.reason, list)
                                else args.reason,
                            ),
                            group_id=group_id,
                        )
                    elif isinstance(event, PrivateMessageEvent):
                        BlacklistManager().add_blacklist(
                            UserInfo(
                                user_id=target_id,
                                date=time.strftime("%Y-%m-%d %H:%M:%S", t),
                                reason=args.reason,
                            ),
                            user_id=user_id,
                        )
                    ban_list.append(str(target_id))
            else:
                pass

        # 返回处理结果
        if not ban_list:
            await ban.finish("无效的操作，请检查命令格式")
        else:
            await ban.finish(f"已将id={','.join(ban_list)}加入黑名单")


@unban.handle()
async def _(bot: Bot, event: MessageEvent, args: Namespace = ShellCommandArgs()):
    user_id = event.user_id
    group_id = event.group_id

    args.is_admin = (
        event.sender.role in ["admin", "owner"]
        if isinstance(event, GroupMessageEvent)
        else False
    )

    args.is_superuser = str(event.user_id) in bot.config.superusers

    if not args.is_admin:
        if not args.is_superuser:
            await unban.finish("权限不足！")

    if not args.target:
        await unban.finish(__plugin_meta__.usage)
    else:

        unban_list = []
        for user in args.target:
            if isinstance(user, MessageSegment):  # 非纯文本
                if user.type == "at":
                    if user.data.get("qq") == "all":
                        await unban.finish("全员赦免？HOW DARE YOU!")
                    target_id = int(user.data.get("qq"))
                    if isinstance(event, GroupMessageEvent):
                        BlacklistManager().remove_blacklist(
                            target_id=target_id,
                            group_id=group_id,
                        )
                        # 重新开启警告
                        if event.group_id not in warning_list["group"]:
                            has_warned_list = []
                        else:
                            has_warned_list = warning_list["group"][event.group_id]
                        if target_id in has_warned_list:
                            has_warned_list.remove(target_id)
                            warning_list["group"][event.group_id] = has_warned_list
                    elif isinstance(event, PrivateMessageEvent):
                        BlacklistManager().remove_blacklist(
                            target_id=target_id,
                            user_id=user_id,
                        )
                        # 重新开启警告
                        has_warned_list = warning_list["user"]
                        if target_id in has_warned_list:
                            has_warned_list.remove(target_id)
                            warning_list["user"] = has_warned_list

                    unban_list.append(str(target_id))
            else:
                pass

        # 返回处理结果
        if not unban_list:
            await unban.finish("无效的操作，请检查命令格式")
        else:
            await unban.finish(f"已将id={','.join(unban_list)}从黑名单中删除")


@Bot.on_calling_api
async def handle_api_call(bot: Bot, api: str, data: Dict[str, Any]):
    global cmd_flag
    if api == "send_msg":
        cmd_flag = True
    else:
        cmd_flag = False
