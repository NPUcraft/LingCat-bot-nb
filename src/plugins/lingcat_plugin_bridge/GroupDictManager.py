from pathlib import Path
from typing import Union, Optional, Dict, Set, List

import yaml
from pydantic import ValidationError

from .Models import GroupDict, News_Type


class GroupDictManager:
    __group_dict: GroupDict
    __path: Path

    def __init__(self, path: Path = Path() / "data" / "bridge" / "groupDict.yml"):
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

    def register_group(self, group_id: int, group_name: str = 'Unknown',
                       subscriber_set: Optional[Dict[int, Set[News_Type]]] = None):
        self.__group_dict.register_group(group_id, group_name, subscriber_set)
        self.__dump()

    def delete_group(self, group_id: int):
        self.__group_dict.delete_group(group_id)
        self.__dump()

    def subscribe(self, subscribers: Union[Set[int], List[int], int], groups: Union[Set[int], List[int], int],
                  news_types: Union[Set[News_Type], List[News_Type], News_Type, str]):
        self.__group_dict.subscribe(subscribers, groups, news_types)
        self.__dump()

    def unsubscribe(self, subscribers: Union[Set[int], List[int], int], groups: Union[Set[int], List[int], int],
                    news_types: Union[Set[News_Type], List[News_Type], News_Type, str]):
        self.__group_dict.unsubscribe(subscribers, groups, news_types)
        self.__dump()

    def who_should_receive(self, group_id: int, news_type: News_Type) -> List[int]:
        return self.__group_dict.who_should_receive(group_id, news_type)
