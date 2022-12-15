from argparse import Namespace
from typing import List, cast, Union, Dict
import base64
from mcstatus import JavaServer

from nonebot.adapters.onebot.v11.message import MessageSegment

from .data import McServerData, Server


class Handle:
    @classmethod
    def list(cls, args: Namespace) -> str:
        msg = ""

        if args.conv["group"]:
            args.conv["user"] = []
        elif args.conv["channel"]:
            args.conv["user"] = []

        if args.user or args.group:
            if args.is_superuser:
                args.conv = {
                    "user": args.user,
                    "group": args.group,
                    "channel": args.channel,
                }
            else:
                return "[ERROR] 获取指定会话的服务器列表需要超级用户权限！"

        for type in args.conv:
            for id in args.conv[type]:
                msg += f"{'用户'if type =='user'else '群' if type == 'group' else '频道'}{id}关注的服务器列表如下：\n"
                mcserver_list = McServerData().get_mcserver_list(
                    id if type == "user" else None,
                    id if type == "group" else None,
                    id if type == "channel" else None,
                )

        if mcserver_list:
            msg += "\n".join(
                f"[{'o'if server.status else 'x'}] {server.name}"
                for server in cast(List[Server], mcserver_list)
            )
        else:
            msg += "关注的服务器列表为空！"

        return msg

    @classmethod
    def ping(cls, args: Namespace) -> Union[str, MessageSegment]:

        if args.conv["group"]:
            args.conv["user"] = []
        elif args.conv["channel"]:
            args.conv["user"] = []

        # 无ip地址则选择列表第一个服务器，列表空则返回错误
        if args.ip == "default":
            for type in args.conv:
                for id in args.conv[type]:
                    mcserver_list = McServerData().get_mcserver_list(
                        id if type == "user" else None,
                        id if type == "group" else None,
                        id if type == "group" else None,
                    )
                    if mcserver_list:
                        args.ip = cast(str, mcserver_list[0].dict()["address"]).split(
                            "|"
                        )[0]
                    else:
                        return "请输入服务器ip地址！"

        try:
            mc_status = JavaServer.lookup(args.ip).status()
            ping = mc_status.latency
            fav = (
                base64.b64decode(mc_status.favicon.split(",")[1])
                if not mc_status.favicon == None
                else None
            )
            status = True
        except:
            fav = None
            ping = None
            status = False

        return MessageSegment.image(fav) + MessageSegment.text(
            f"服务器地址：{args.ip}\n"
            + f"状态：{'On' if status else 'Off'}"
            + (f"\nPing: {int(ping)}ms" if status else "")
        )

    @classmethod
    def online(cls, args: Namespace) -> str:

        if args.conv["group"]:
            args.conv["user"] = []
        elif args.conv["channel"]:
            args.conv["user"] = []

        # 无ip地址则选择列表第一个服务器，列表空则返回错误
        if args.ip == "default":
            for type in args.conv:
                for id in args.conv[type]:
                    mcserver_list = McServerData().get_mcserver_list(
                        id if type == "user" else None,
                        id if type == "group" else None,
                        id if type == "channel" else None,
                    )
                    if mcserver_list:
                        args.ip = cast(str, mcserver_list[0].dict()["address"])
                    else:
                        return "请输入服务器ip地址！"

        playersName = []
        online = False
        num = 0
        for ip in cast(str, args.ip).split("|"):
            try:
                playersInfo = JavaServer.lookup(ip).status().raw["players"]
                num += cast(Dict, playersInfo).get("online", 0)
                if not num == 0:
                    online = True
                playersList = cast(Dict, playersInfo).get("sample", [])
                for p in playersList:
                    playersName.append(p["name"])
            except:
                pass

            """
            try:
                query = server.query()
                players = "The server has the following players online: {0}".format(", ".join(query.players.names))
            except Exception as e:
                print("ERROR: " + str(e))
                players = "The server has the following players online: " + str([ user['name'] for user in status.raw['players']['sample'] ]).replace("'", "").replace("[", "").replace("]", "")
                pass
            """

        return f"服务器当前在线：{'空荡荡~' if not online else f'{num}人在线，暂无法获取玩家名称~' if len(playersName)==0 else '，'.join(playersName)}"

    @classmethod
    def remove(cls, args: Namespace) -> str:

        if args.conv["group"]:
            if not args.is_admin and not args.is_superuser:
                return "管理服务器需要管理员权限！"
            args.conv["user"] = []
        if args.conv["channel"]:
            if not args.is_admin and not args.is_superuser:
                return "管理服务器需要管理员权限！"
            args.conv["user"] = []

        if args.user or args.group:
            if args.is_superuser:
                args.conv = {
                    "user": args.user,
                    "group": args.group,
                    "channel": args.channel,
                }
            else:
                return "[ERROR] 管理指定会话的服务器列表需要超级用户权限！"

        # 移除服务器
        for type in args.conv:
            for id in args.conv[type]:
                McServerData().remove_server(
                    args.name,
                    id if type == "user" else None,
                    id if type == "group" else None,
                    id if type == "channel" else None,
                )

        return "移除服务器成功！"

    @classmethod
    def add(cls, args: Namespace) -> str:

        if args.conv["group"]:
            if not args.is_admin and not args.is_superuser:
                return "管理群插件需要群管理员权限！"
            args.conv["user"] = []
        if args.conv["channel"]:
            if not args.is_admin and not args.is_superuser:
                return "管理服务器需要管理员权限！"
            args.conv["user"] = []

        if args.user or args.group:
            if args.is_superuser:
                args.conv = {
                    "user": args.user,
                    "group": args.group,
                    "channel": args.channel,
                }
            else:
                return "[ERROR] 管理指定会话的服务器列表需要超级用户权限！"

        # 尝试连接mc服务器
        try:
            mc_status = (
                JavaServer.lookup(cast(str, args.ip).split("|")[0]).status().latency
            )
            status = True
        except:
            status = False

        for type in args.conv:
            for id in args.conv[type]:
                McServerData().add_server(
                    Server(name=args.name, address=args.ip, status=status),
                    id if type == "user" else None,
                    id if type == "group" else None,
                    id if type == "channel" else None,
                )

        return "添加服务器成功！"
