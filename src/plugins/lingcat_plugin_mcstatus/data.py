from pathlib import Path
from typing import Dict, List, Union, Optional, cast

from pydantic import BaseModel
import yaml


class Server(BaseModel):
    name: str
    address: str
    status: bool


ServerList = Dict[str, Dict[int, List[Server]]]


class McServerData:
    __path: Path
    __mcserver_list: ServerList = {"user": {}, "group": {}, "channel": {}}

    def __init__(self, path: Path = Path() / "data" / "mcstatus" / "mcserver_list.yml"):
        self.__path = path
        self.__load()

    def get_mcserver_list(
        self,
        user_id: Optional[int] = None,
        group_id: Optional[int] = None,
        channel_id: Optional[int] = None,
    ) -> Union[ServerList, List[Server]]:
        mcserver_list = self.__mcserver_list

        if user_id:  # 获取用户mc服务器列表
            if user_id not in mcserver_list["user"]:
                mcserver_list["user"][user_id] = []
            return mcserver_list["user"][user_id]
        elif group_id:  # 获取群组mc服务器列表
            if group_id not in mcserver_list["group"]:
                mcserver_list["group"][group_id] = []
            return mcserver_list["group"][group_id]
        elif channel_id:  # 获取频道mc服务器列表
            if channel_id not in mcserver_list["channel"]:
                mcserver_list["channel"][channel_id] = []
            return mcserver_list["channel"][channel_id]
        else:
            return mcserver_list

    # 添加服务器
    def add_server(
        self,
        server: Server,
        user_id: Optional[int] = None,
        group_id: Optional[int] = None,
        channel_id: Optional[int] = None,
    ):
        mcserver_list = cast(
            List[Server], self.get_mcserver_list(user_id, group_id, channel_id)
        )
        if server not in mcserver_list:
            mcserver_list.append(server)

        if user_id:
            self.__mcserver_list["user"][user_id] = mcserver_list
        elif group_id:
            self.__mcserver_list["group"][group_id] = mcserver_list
        elif channel_id:
            self.__mcserver_list["channel"][channel_id] = mcserver_list

        # 保存数据
        self.__dump()

    # 移除服务器
    def remove_server(
        self,
        name: str,
        user_id: Optional[int] = None,
        group_id: Optional[int] = None,
        channel_id: Optional[int] = None,
    ):
        mcserver_list = list(
            filter(
                lambda server: server.name != name,
                cast(
                    List[Server], self.get_mcserver_list(user_id, group_id, channel_id)
                ),
            )
        )

        if user_id:
            if mcserver_list:
                self.__mcserver_list["user"][user_id] = mcserver_list
            else:
                self.__mcserver_list["user"].pop(user_id)
        elif group_id:
            if mcserver_list:
                self.__mcserver_list["group"][group_id] = mcserver_list
            else:
                self.__mcserver_list["group"].pop(group_id)
        elif channel_id:
            if mcserver_list:
                self.__mcserver_list["channel"][channel_id] = mcserver_list
            else:
                self.__mcserver_list["channel"].pop(channel_id)

        self.__dump()

    # 加载服务器列表
    def __load(self):
        try:
            mcserver_list = yaml.safe_load(self.__path.open("r", encoding="utf-8"))
            for type in mcserver_list:
                for id in mcserver_list[type]:
                    self.__mcserver_list[type][id] = [
                        Server(**server) for server in mcserver_list[type][id]
                    ]
        except:
            self.__mcserver_list = {"user": {}, "group": {}, "channel": {}}

    # 保存服务器列表
    def __dump(self):
        self.__path.parent.mkdir(parents=True, exist_ok=True)
        mcserver_list = {"user": {}, "group": {}, "channel": {}}
        for type in self.__mcserver_list:
            for id in self.__mcserver_list[type]:
                mcserver_list[type][id] = [
                    server.dict() for server in self.__mcserver_list[type][id]
                ]
        yaml.dump(
            mcserver_list,
            self.__path.open("w", encoding="utf-8"),
            allow_unicode=True,
        )
