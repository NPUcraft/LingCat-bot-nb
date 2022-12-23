from nonebot import get_driver
from nonebot import on_message
from nonebot.adapters.onebot.v11 import (
    Bot,
    Event,
    Message,
    MessageEvent,
    GROUP,
    PRIVATE,
)


config = get_driver().config
command_start = config.command_start


async def not_command_checker(event: Event):
    mes = event.get_message().extract_plain_text().strip(' \r\n')
    return mes == '' or mes.strip(' \r\n')[0] not in command_start


repeater = on_message(rule=not_command_checker, priority=500, permission=GROUP|PRIVATE)

last = dict()
last_equal_count = dict()

@repeater.handle()
async def handle(bot: Bot, Event: MessageEvent):
    global last
    global last_equal_count
    id = Event.get_session_id()
    if id.find("group") != -1:
        ids = id.split('_')
        id = ids[0] + '_' + ids[1]
    if id in last.keys() and last[id] == Event.get_message().extract_plain_text():
        last_equal_count[id] += 1
        if last_equal_count[id] >= 2:
            last_equal_count[id] = -3
            await repeater.finish(Event.message)
    else:
        last[id] = Event.get_message().extract_plain_text()
        last_equal_count[id] = 0
        await repeater.finish()
