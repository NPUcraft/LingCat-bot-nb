import nonebot

from .handler import helper


cmd_start = sorted(list(nonebot.get_driver().config.command_start))[0]

__plugin_meta__ = nonebot.plugin.PluginMetadata(
    name="帮助菜单",
    description="帮助菜单插件",
    usage=f"""欢迎使用Help Menu
本插件提供查看机器人帮助菜单能力
可用命令前缀：{" ".join(list(nonebot.get_driver().config.command_start))}

{cmd_start}help  # 展示已加载插件列表
{cmd_start}help <插件名>  # 展示目标插件帮助信息""",
    extra={
        "version": "v1.0",
        "alias": ["帮助菜单", "help", "帮助"],
        "mode": "755",
    },
)
