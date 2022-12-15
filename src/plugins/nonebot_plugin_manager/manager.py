from pathlib import Path
from typing import Dict, List, Union

import nonebot
import yaml

Conv = Dict[str, List[int]]


class PluginManager:
    __path: Path
    __plugin_list: Dict[str, Dict[str, Union[str, Dict[int, int]]]]

    def __init__(self, path: Path = Path() / "data" / "manager" / "plugin_list.yml"):
        self.__path = path
        self.__load()

    def get_plugin(
        self,
        conv: Conv = {"user": [], "group": [], "channel": []},
        perm: Union[str, int] = 0b0101,
    ) -> Dict[str, bool]:
        result = {}
        type = len(conv["user"]) + len(conv["group"]) + len(conv["channel"])

        for p in self.__plugin_list:
            mode = int(self.__plugin_list[p]["mode"][type])  # 默认权限等级
            for t in conv:
                can_break = False
                for i in conv[t]:
                    if i in self.__plugin_list[p][t]:  # 读取自定义的权限
                        mode = int(self.__plugin_list[p][t][i])
                        if t == "user":  # 针对用户的权限，无需看群与频道权限
                            can_break = True
                if can_break:
                    break
            result[p] = mode & perm == perm
        return result

    # 设置插件模式
    def chmod_plugin(self, plugin: List[str], mode: str) -> Dict[str, bool]:
        result = {}
        for p in plugin:
            result[p] = False
            if p in self.__plugin_list:
                result[p] = True
                self.__plugin_list[p]["mode"] = mode
        self.__dump()
        return result

    # 禁用插件
    def off_plugin(
        self,
        plugin: List[str] = [],
        conv: Conv = {"user": [], "group": [], "channel": []},
    ) -> Dict[str, bool]:
        result = {}
        for p in plugin:
            result[p] = False
            if p in self.get_plugin():
                result[p] = True
                for t in conv:
                    for i in conv[t]:
                        if i in self.__plugin_list[p][t]:
                            mode = (
                                self.__plugin_list[p][t][i]
                                if self.__plugin_list[p][t][i]
                                < int(
                                    self.__plugin_list[p]["mode"][
                                        1 if t == "user" else 2
                                    ]
                                )
                                else int(
                                    self.__plugin_list[p]["mode"][
                                        1 if t == "user" else 2
                                    ]
                                )
                            )
                        else:
                            mode = int(
                                self.__plugin_list[p]["mode"][1 if t == "user" else 2]
                            )
                        self.__plugin_list[p][t][i] = mode & 0b0110

        self.__dump()
        return result

    # 启用插件
    def on_plugin(
        self,
        plugin: List[str] = [],
        conv: Conv = {"user": [], "group": [], "channel": []},
    ) -> Dict[str, bool]:
        result = {}
        for p in plugin:
            result[p] = False
            if p in self.get_plugin():
                result[p] = True
                for t in conv:
                    for i in conv[t]:
                        if i in self.__plugin_list[p][t]:
                            mode = (
                                self.__plugin_list[p][t][i]
                                if self.__plugin_list[p][t][i]
                                < int(
                                    self.__plugin_list[p]["mode"][
                                        1 if t == "user" else 2
                                    ]
                                )
                                else int(
                                    self.__plugin_list[p]["mode"][
                                        1 if t == "user" else 2
                                    ]
                                )
                            )
                        else:
                            mode = int(
                                self.__plugin_list[p]["mode"][1 if t == "user" else 2]
                            )
                        self.__plugin_list[p][t][i] = mode | 0b0001
        self.__dump()
        return result

    def update_plugin(self, plugin: Dict[str, bool]) -> "PluginManager":
        for p in plugin:
            try:
                plugin_mode = nonebot.get_plugin(p)
                plugin_mode = plugin_mode.metadata.extra.get("mode", "755")
            except:
                plugin_mode = "755"

            if p not in self.__plugin_list:
                self.__plugin_list[p] = {
                    "mode": plugin_mode if plugin[p] else "311",
                    "user": {},
                    "group": {},
                    "channel": {},
                }
            elif plugin[p] ^ self.__plugin_list[p].get(
                "status",
                int(self.__plugin_list[p]["mode"][0]) & 0b0100 == 0b0100,
            ):
                self.__plugin_list[p]["mode"] = "".join(
                    str(int(m) | 0b0100 if plugin[p] else int(m) & 0b0011)
                    for m in self.__plugin_list[p]["mode"]
                )
            self.__plugin_list[p]["status"] = plugin[p]
        for p in self.__plugin_list:
            if p not in plugin:
                self.__plugin_list[p]["status"] = False
                self.__plugin_list[p]["mode"] = "".join(
                    str(int(m) & 0b0011) for m in self.__plugin_list[p]["mode"]
                )
        self.__dump()
        return self

    # 获取插件权限模式
    def get_mode(self) -> Dict[str, str]:
        plugin_mode = {}
        for p in self.__plugin_list:
            plugin_mode[p] = self.__plugin_list[p]["mode"]
        return plugin_mode

    # 加载插件列表
    def __load(self) -> "PluginManager":
        try:
            self.__plugin_list = yaml.safe_load(self.__path.open("r", encoding="utf-8"))
        except:
            self.__plugin_list = {}
        return self

    # 保存插件列表
    def __dump(self):
        self.__path.parent.mkdir(parents=True, exist_ok=True)
        yaml.dump(
            self.__plugin_list,
            self.__path.open("w", encoding="utf-8"),
            allow_unicode=True,
        )


plugin_manager = PluginManager()
