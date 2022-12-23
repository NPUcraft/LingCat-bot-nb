import nonebot
from nonebot import on_command
from nonebot.plugin import PluginMetadata
from nonebot.adapters import Event
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Bot, GROUP, PRIVATE
from nonebot.adapters.onebot.v11.message import Message, MessageSegment
from nonebot.matcher import Matcher
from nonebot.params import CommandArg, RawCommand

from nonebot_plugin_guild_patch import GuildMessageEvent

default_start = sorted(list(nonebot.get_driver().config.command_start))[0]

__plugin_meta__ = PluginMetadata(
    name="意见反馈",
    description="将意见或建议反馈给开发者",
    usage=f"""可用的命令前缀：{" ".join(list(nonebot.get_driver().config.command_start))}

{default_start}send <反馈内容> # 反馈内容发送至开发者""",
    extra={
        "version": "v1.0",
        "alias": ["反馈", "send", "feedback", "fb"],
        "mode": "711",
    },
)

feedback = on_command(
    "send", priority=15, aliases={"feedback", "fb", "反馈"}, permission=GROUP | PRIVATE
)


@feedback.handle()
async def send(event: Event, matcher: Matcher, args: Message = CommandArg()):
    at_user = MessageSegment.at(event.get_user_id())
    if args:
        matcher.set_arg("content", args)
    else:
        await matcher.finish(at_user + MessageSegment.text("你好像什么也没说呢~"))


@feedback.got("content")
async def _(bot: Bot, event: Event, content: Message = RawCommand()):
    messages = []
    messages.append(
        f"发送者：{(event.sender.nickname if not event.sender.card else event.sender.card) if isinstance(event,GroupMessageEvent) else event.sender.nickname}({event.sender.user_id})"
    )
    messages.append(
        f"来自：{f'群[{event.group_id}]' if isinstance(event,GroupMessageEvent) else f'频道[{event.channel_id}]' if isinstance(event,GuildMessageEvent)else f'用户[{event.user_id}]'}"
    )
    messages.append("反馈内容：")
    header = MessageSegment.text("\n".join(messages))
    msg = event.message
    if msg[0].type == "text" and msg[0].data["text"].startswith(content):
        msg[0].data["text"] = msg[0].data["text"][len(content) :].lstrip()
    else:
        msg = MessageSegment.text("反馈失败！")

    await bot.send_private_msg(
        user_id=list(nonebot.get_driver().config.superusers)[0], message=header + msg
    )
    await feedback.finish("已成功反馈给我的主人~")
