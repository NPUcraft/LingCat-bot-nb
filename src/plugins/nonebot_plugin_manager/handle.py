from argparse import Namespace
from typing import Dict, cast

from .manager import plugin_manager


class Handle:
    @classmethod
    def get_readable_plugins(cls, conv) -> Dict[str, bool]:
        plugins = plugin_manager.get_plugin(conv, 0b0001)
        plugins = {
            p: plugins[p] for p in plugins if plugin_manager.get_plugin(conv, 0b0100)[p]
        }
        plugins = {k: v for k, v in sorted(plugins.items(), key=lambda item: item[0])}
        return plugins

    @classmethod
    def info(cls, args: Namespace) -> str:
        msg = ""

        if args.conv["group"]:
            args.conv["user"] = []
        elif args.conv["channel"]:
            args.conv["user"] = []
        elif args.is_superuser:
            args.conv["user"] = []

        if args.user or args.group or args.channel:
            if args.is_superuser:
                args.conv = {
                    "user": args.user,
                    "group": args.group,
                    "channel": args.channel,
                }
            else:
                return "[ERROR] 获取指定会话的插件列表需要超级用户权限！"

        for t in args.conv:
            for i in args.conv[t]:
                msg += (
                    f"{'用户'if t == 'user'else '群' if t == 'group' else '频道'}{i}的插件列表：\n"
                )

        plugin = plugin_manager.get_plugin(args.conv, 0b0001)
        # plugin = cls.get_readable_plugins(args.conv)
        if not args.all:
            plugin = {
                p: plugin[p]
                for p in plugin
                if plugin_manager.get_plugin(args.conv, 0b0100)[p]
            }
        plugin = {k: v for k, v in sorted(plugin.items(), key=lambda item: item[0])}

        plugin_mode = plugin_manager.get_mode()
        msg += "\n".join(
            f"[{plugin_mode[p]if p in plugin_mode else 'xxx'} | {'o'if plugin[p] else 'x'}] {p}"
            for p in plugin
            if plugin_mode[p] != "000"
        )
        return msg

    @classmethod
    def chmod(cls, args: Namespace) -> str:
        if not args.is_superuser:
            return "[ERROR] 权限不足，设置插件权限需要超级用户权限！"

        for ch in args.mode:
            if not (ch.isdigit() and int(ch) <= 7):
                return "[ERROR] 权限等级应为不大于7的三位正整数组成！"

        # plugin = plugin_manager.get_plugin()
        # if args.all:
        #     args.plugin = list(plugin.keys())
        # if args.reverse:
        #     args.plugin = list(filter(lambda p: p not in args.plugin, plugin))

        result = plugin_manager.chmod_plugin(args.plugin, args.mode)

        return "\n".join(
            f"""插件{p}的权限等级成功设置为{args.mode}！""" if result[p] else f"插件{p}不存在！"
            for p in result
        )

    @classmethod
    def off(cls, args: Namespace) -> str:
        if args.is_superuser:
            plugin = plugin_manager.get_plugin(perm=0b0110)
        else:
            plugin = plugin_manager.get_plugin(conv=args.conv, perm=0b0110)

        if args.conv["group"]:
            if not args.is_admin and not args.is_superuser:
                return "管理群插件需要群管理员权限！"
            args.conv["user"] = []
        elif args.conv["channel"]:
            if not args.is_admin and not args.is_superuser:
                return "管理频道插件需要频道管理员权限！"
            args.conv["user"] = []

        if args.all:
            args.plugin = list(plugin.keys())
        if args.reverse:
            args.plugin = list(filter(lambda p: p not in args.plugin, plugin))

        # 记录关闭插件结果：操作失败
        result = {}
        for p in plugin:
            if p in args.plugin and not plugin[p]:
                args.plugin.remove(p)
                result[p] = False

        # 如果需要管理指定群或用户设置conv
        if args.user or args.group or args.channel:
            if args.is_superuser:
                args.conv = {
                    "user": args.user,
                    "group": args.group,
                    "channel": args.channel,
                }
            else:
                return "管理指定群、频道或用户的插件需要超级用户权限！"

        result.update(plugin_manager.off_plugin(args.plugin, args.conv))

        msg = ""
        for t in args.conv:
            if args.conv[t]:
                msg += "用户 " if t == "user" else "群 " if t == "group" else "频道 "
                msg += ",".join(str(i) for i in args.conv[t])
        msg += " 中："

        for plugin, value in result.items():
            msg += "\n"
            if value:
                msg += f"插件{plugin}已关闭！"
            else:
                msg += f"插件{plugin}不存在或已关闭编辑权限！"
        return msg

    @classmethod
    def on(cls, args: Namespace) -> str:
        if args.is_superuser:
            plugin = plugin_manager.get_plugin(perm=0b0110)
        else:
            plugin = plugin_manager.get_plugin(conv=args.conv, perm=0b0110)

        if args.conv["group"]:
            if not args.is_admin and not args.is_superuser:
                return "管理群插件需要群管理员权限！"
            args.conv["user"] = []
        elif args.conv["channel"]:
            if not args.is_admin and not args.is_superuser:
                return "管理频道插件需要频道管理员权限！"
            args.conv["user"] = []

        if args.all:
            args.plugin = list(plugin.keys())
        if args.reverse:
            args.plugin = list(filter(lambda p: p not in args.plugin, plugin))

        # 记录开启插件结果：操作失败
        result = {}
        for p in plugin:
            if p in args.plugin and not plugin[p]:
                args.plugin.remove(p)
                result[p] = False

        # 如果需要管理指定群或用户设置conv
        if args.user or args.group or args.channel:
            if args.is_superuser:
                args.conv = {
                    "user": args.user,
                    "group": args.group,
                    "channel": args.channel,
                }
            else:
                return "管理指定群、频道或用户的插件需要超级用户权限！"

        result.update(plugin_manager.on_plugin(args.plugin, args.conv))

        msg = ""
        for t in args.conv:
            if args.conv[t]:
                msg += "用户 " if t == "user" else "群 " if t == "group" else "频道 "
                msg += ",".join(str(i) for i in args.conv[t])
        msg += " 中："

        for plugin, value in result.items():
            msg += "\n"
            if value:
                msg += f"插件{plugin}已开启！"
            else:
                msg += f"插件{plugin}不存在或已关闭编辑权限！"
        return msg
