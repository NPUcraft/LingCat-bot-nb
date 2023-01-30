from nonebot import get_driver


default_start = sorted(list(get_driver().config.command_start))[0]


# Export something for other plugin
# export = nonebot.export()
# export.foo = "bar"

# @export.xxx
# def some_function():
#     pass

