from pathlib import Path
from pydantic import BaseModel
from typing import Dict, List, Union, Optional, cast

import yaml


class UserInfo(BaseModel):
    user_id: int
    date: str
    reason: str


BlackList = Dict[str, Union[List[UserInfo], Dict[int, List[UserInfo]]]]


class BlacklistManager:
    __path: Path
    __blacklist: BlackList

    def __init__(self, path: Path = Path() / "data" / "ban" / "blacklist.yml"):
        self.__blacklist: BlackList = {"user": {}, "group": {}, "channel": {}}
        self.__path = path
        self.__load()

    # 获取黑名单列表
    def get_blacklist(
        self,
        user_id: Optional[int] = None,
        group_id: Optional[int] = None,
        channel_id: Optional[int] = None,
    ) -> Union[BlackList, List[UserInfo]]:
        blacklist = self.__blacklist

        if user_id:  # 获取私聊黑名单
            return blacklist["user"]
        elif group_id:  # 获取群黑名单列表
            if group_id not in blacklist["group"]:
                blacklist["group"][group_id] = []
            return blacklist["group"][group_id]
        elif channel_id:  # 获取频道黑名单列表
            if channel_id not in blacklist["channel"]:
                blacklist["channel"][channel_id] = []
            return blacklist["channel"][channel_id]
        else:
            return blacklist

    def is_in_blacklist(
        self, user_id: int, blacklist: List[UserInfo] = None
    ) -> Union[str, bool]:
        blacklist = list(
            filter(
                lambda user: user.user_id == user_id,
                blacklist,
            )
        )
        if blacklist:
            return blacklist[0].reason
        else:
            return False

    # 添加黑名单
    def add_blacklist(
        self,
        user: UserInfo,
        user_id: Optional[int] = None,
        group_id: Optional[int] = None,
        channel_id: Optional[int] = None,
    ):

        blacklist = cast(
            List[UserInfo], self.get_blacklist(user_id, group_id, channel_id)
        )
        if user not in blacklist:
            blacklist.append(user)

        if user_id:
            self.__blacklist["user"] = blacklist
        elif group_id:
            self.__blacklist["group"][group_id] = blacklist
        elif channel_id:
            self.__blacklist["channel"][channel_id] = blacklist

        # 保存数据
        self.__dump()

    # 移除黑名单
    def remove_blacklist(
        self,
        target_id,
        user_id: Optional[int] = None,
        group_id: Optional[int] = None,
        channel_id: Optional[int] = None,
    ):
        blacklist = list(
            filter(
                lambda user: user.user_id != target_id,
                cast(List[UserInfo], self.get_blacklist(user_id, group_id, channel_id)),
            )
        )

        if user_id:
            if blacklist:
                self.__blacklist["user"] = blacklist
            else:
                self.__blacklist["user"] = blacklist
        elif group_id:
            if blacklist:
                self.__blacklist["group"][group_id] = blacklist
            else:
                self.__blacklist["group"].pop(group_id)
        elif channel_id:
            if blacklist:
                self.__blacklist["channel"][channel_id] = blacklist
            else:
                self.__blacklist["channel"].pop(channel_id)

        self.__dump()

    # 加载黑名单
    def __load(self):
        try:
            blacklist = yaml.safe_load(self.__path.open("r", encoding="utf-8"))
            for type in blacklist:
                for id in blacklist[type]:
                    if type == "user":
                        self.__blacklist[type] = [
                            UserInfo(**user) for user in blacklist[type]
                        ]
                    else:
                        self.__blacklist[type][id] = [
                            UserInfo(**user) for user in blacklist[type][id]
                        ]
        except:
            self.__blacklist = {"user": {}, "group": {}, "channel": {}}

    # 保存黑名单
    def __dump(self):
        self.__path.parent.mkdir(parents=True, exist_ok=True)
        blacklist = {"user": {}, "group": {}, "channel": {}}
        for type in self.__blacklist:
            for id in self.__blacklist[type]:
                if type == "user":
                    blacklist[type] = [user.dict() for user in self.__blacklist[type]]
                else:
                    blacklist[type][id] = [
                        user.dict() for user in self.__blacklist[type][id]
                    ]
        yaml.dump(
            blacklist,
            self.__path.open("w", encoding="utf-8"),
            allow_unicode=True,
        )
