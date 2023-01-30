from pydantic import BaseModel
from typing import (
    Set,
    Dict,
    Union,
    List
)
from enum import IntEnum

News_Type = IntEnum('News_Type',
                    (
                        'MiniGameInvitation',
                        'OrganizationMessage',
                        'SomethingNews'
                    ))


class GroupRelation(BaseModel):
    name: str = 'Unknown'
    subscribe_set: Dict[int, Set[News_Type]]

    def subscribe(self, targets: Union[Set[int], List[int], int],
                  news_types: Union[Set[News_Type], List[News_Type], News_Type, str]):
        if type(news_types) is str:
            if news_types == 'All':
                news_types = {it for it in News_Type}
            else:
                return
        if type(targets) is int:
            targets = [targets]
        if type(news_types) is News_Type:
            news_types = [news_types]
        targets = set(targets)
        news_types = set(news_types)
        for target in targets:
            self.subscribe_set[target].union(news_types)

    def unsubscribe(self, targets: Union[Set[int], List[int], int],
                    news_types: Union[Set[News_Type], List[News_Type], News_Type, str]):
        if type(news_types) is str:
            if news_types == 'All':
                for target in targets:
                    if target in self.subscribe_set.keys():
                        del self.subscribe_set[target]
            else:
                return
        if type(targets) is int:
            targets = [targets]
        if type(news_types) is News_Type:
            news_types = [news_types]
        targets = set(targets)
        news_types = set(news_types)
        for target in targets:
            if target in self.subscribe_set.keys():
                self.subscribe_set[target] = self.subscribe_set[target] - news_types


class GroupDict(BaseModel):
    groups: Dict[int, GroupRelation]
