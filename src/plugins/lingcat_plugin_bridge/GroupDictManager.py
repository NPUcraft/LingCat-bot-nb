from typing import Union, Optional, Dict

import yaml

from .Models import GroupDict, GroupRelation, News_Type
from pydantic import ValidationError
from pathlib import Path


class GroupDictManager:
    __group_dict: GroupDict
    __path: Path

    def __init__(self, path: Path = Path() / "data" / "bridge" / "groupDict.json"):
        self.__path = path
        self.__load()

    def __load(self):
        try:
            groups = yaml.safe_load(self.__path.open('r', encoding='utf-8'))
            self.__group_dict = GroupDict(groups=groups)
        except Union[FileNotFoundError, ValueError, ValidationError]:
            self.__group_dict = GroupDict(groups={})

    def __dump(self):
        self.__path.parent.mkdir(parents=True, exist_ok=True)
        yaml.dump(self.__group_dict.groups,
                  self.__path.open('w', encoding='utf-8'),
                  allow_unicode=True)

    def add_group(self, group_id: int, group_name: str = 'Unknown', subscribe_set: Optional[Dict[News_Type]] = None):
        if subscribe_set is None:
            subscribe_set = {}
        if group_id not in self.__group_dict.groups.keys():
            self.__group_dict[group_id] = GroupRelation(name=group_name, subscribe_set=subscribe_set)
