import random
from datetime import date
import nonebot
from nonebot.plugin import on_command, PluginMetadata
from nonebot.adapters.onebot.v11 import (
    MessageSegment,
    Bot,
    MessageEvent,
    GROUP,
    PRIVATE,
)

default_start = sorted(list(nonebot.get_driver().config.command_start))[0]
bot_name = list(nonebot.get_driver().config.nickname)[0]

__plugin_meta__ = PluginMetadata(
    name="今日人品",
    description="查看今日人品",
    usage=f"""可用的命令前缀：{" ".join(list(nonebot.get_driver().config.command_start))}

{default_start}jrrp  # 查看今日人品""",
    extra={
        "version": "v1.0",
        "alias": ["今日人品", "jrrp"],
        "mode": "757",
    },
)


jrrp = on_command("jrrp", priority=50, aliases={"今日人品"}, permission=GROUP | PRIVATE)


@jrrp.handle()
async def jrrp_handle(bot: Bot, msg_event: MessageEvent):
    rnd = random.Random()
    rnd.seed(int(date.today().strftime("%y%m%d")) + int(msg_event.get_user_id()))
    luck_num = rnd.randint(1, 100)
    await jrrp.finish(
        MessageSegment.text(f"{msg_event.sender.nickname} ")
        + MessageSegment.text(f"今日的人品为{luck_num}")
    )
