from enum import IntEnum
from typing import (
    Set,
    Dict,
    Union,
    List,
    Optional
)

from pydantic import BaseModel

News_Type = IntEnum('News_Type',
                    (
                        'MiniGameInvitation',
                        'OrganizationMessage',
                        'SomethingNews'
                    ))


class GroupRelation(BaseModel):
    """
    name: 群名

    subscriber_set: 该群的订阅者

    subscriber_set : Dict[int, Set[News_Type]]
    """
    name: str = 'Unknown'
    subscriber_set: Dict[int, Set[News_Type]]

    def subscribe(self, subscribers: Union[Set[int], List[int], int],
                  news_types: Union[Set[News_Type], List[News_Type], News_Type, str]):
        if type(news_types) is str:
            if news_types == 'All':
                news_types = {it for it in News_Type}
            else:
                return
        if type(subscribers) is int:
            subscribers = [subscribers]
        if type(news_types) is News_Type:
            news_types = [news_types]
        subscribers = set(subscribers)
        news_types = set(news_types)
        for subscriber in subscribers:
            self.subscriber_set[subscriber].union(news_types)

    def unsubscribe(self, subscribers: Union[Set[int], List[int], int],
                    news_types: Union[Set[News_Type], List[News_Type], News_Type, str]):
        if type(news_types) is str:
            if news_types == 'All':
                for subscriber in subscribers:
                    if subscriber in self.subscriber_set.keys():
                        del self.subscriber_set[subscriber]
            else:
                return
        if type(subscribers) is int:
            subscribers = [subscribers]
        if type(news_types) is News_Type:
            news_types = [news_types]
        subscribers = set(subscribers)
        news_types = set(news_types)
        for subscriber in subscribers:
            if subscriber in self.subscriber_set.keys():
                self.subscriber_set[subscriber] -= news_types
                if len(self.subscriber_set[subscriber]) == 0:
                    del self.subscriber_set[subscriber]

    @property
    def subscriber(self) -> List[int]:
        """
        :return: 订阅者列表List[int]
        """
        return list(self.subscriber_set.keys())

    def who_should_receive(self, news_type: News_Type) -> List[int]:
        receivers = list()
        for subscriber, news_types in self.subscriber_set.items():
            if news_type in news_types:
                receivers.append(subscriber)
        return receivers


class GroupDict(BaseModel):
    groups: Dict[int, GroupRelation]

    def register_group(self, group_id: int, group_name: str,
                       subscriber_set: Optional[Dict[int, Set[News_Type]]] = None):
        if subscriber_set is None:
            subscriber_set = {}
        if group_id not in self.groups:
            self.groups[group_id] = GroupRelation(name=group_name, subscriber_set=subscriber_set)

    def delete_group(self, group_id: int):
        if group_id in self.groups:
            del self.groups[group_id]

    def subscribe(self, subscribers: Union[Set[int], List[int], int], groups: Union[Set[int], List[int], int],
                  news_types: Union[Set[News_Type], List[News_Type], News_Type, str]):
        """
        Subscribers: 订阅者

        groups: 被订阅者

        news_types: 订阅的消息类型, 为'All'时表示订阅全部
        """
        if type(groups) is int:
            groups = [groups]
        groups = set(groups)
        for group in groups:
            self.groups[group].subscribe(subscribers, news_types)

    def unsubscribe(self, subscribers: Union[Set[int], List[int], int], groups: Union[Set[int], List[int], int],
                    news_types: Union[Set[News_Type], List[News_Type], News_Type, str]):
        if type(groups) is int:
            groups = [groups]
        groups = set(groups)
        for group in groups:
            self.groups[group].unsubscribe(subscribers, news_types)

    def who_should_receive(self, group_id: int, news_type: News_Type) -> List[int]:
        return self.groups[group_id].who_should_receive(news_type)


class StaffDict(BaseModel):
    staff_groups: Dict[int, Set[int]]

    def add_staff(self, staff_ids: Union[Set[int], List[int], int], group_ids: Union[Set[int], List[int], int]):
        if type(staff_ids) is int:
            staff_ids = [staff_ids]
        if type(group_ids) is int:
            group_ids = [group_ids]
        staff_ids = set(staff_ids)
        group_ids = set(group_ids)
        for staff_id in staff_ids:
            self.staff_groups[staff_id].union(group_ids)

    def del_staff(self, staff_ids: Union[Set[int], List[int], int], group_ids: Union[Set[int], List[int], int]):
        if type(staff_ids) is int:
            staff_ids = [staff_ids]
        if type(group_ids) is int:
            group_ids = [group_ids]
        staff_ids = set(staff_ids)
        group_ids = set(group_ids)
        for staff_id in staff_ids:
            if staff_id in self.staff_groups.keys():
                self.staff_groups[staff_id] -= group_ids
                if len(self.staff_groups) == 0:
                    del self.staff_groups[staff_id]

    def del_staff_all(self, staff_ids: Union[Set[int], List[int], int]):
        if type(staff_ids) is int:
            staff_ids = [staff_ids]
        staff_ids = set(staff_ids)
        for staff_id in staff_ids:
            if staff_id in self.staff_groups.keys():
                del self.staff_groups[staff_id]

    def groups_of_staff(self, staff_id: int) -> Set[int]:
        return self.staff_groups[staff_id]
