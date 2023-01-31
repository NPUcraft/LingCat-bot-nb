from pathlib import Path
from typing import Union, Set, List

import yaml
from pydantic import ValidationError

from .Models import StaffDict


class StaffDictManager:
    __staff_dict: StaffDict
    __path: Path

    def __init__(self, path: Path = Path() / "data" / "bridge" / "staffDict.yml"):
        self.__path = path
        self.__load()

    def __load(self):
        try:
            staffs = yaml.safe_load(self.__path.open('r', encoding='utf-8'))
            self.__staff_dict = StaffDict(staffs=staffs)
        except Union[FileNotFoundError, ValueError, ValidationError]:
            self.__staff_dict = StaffDict(staffs={})

    def __dump(self):
        self.__path.parent.mkdir(parents=True, exist_ok=True)
        yaml.dump(self.__staff_dict.staff_groups,
                  self.__path.open('w', encoding='utf-8'),
                  allow_unicode=True)

    def add_staff(self, staff_ids: Union[Set[int], List[int], int], group_ids: Union[Set[int], List[int], int]):
        self.__staff_dict.add_staff(staff_ids, group_ids)
        self.__dump()

    def del_staff(self, staff_ids: Union[Set[int], List[int], int], group_ids: Union[Set[int], List[int], int]):
        self.__staff_dict.del_staff(staff_ids, group_ids)
        self.__dump()

    def del_staff_all(self, staff_ids: Union[Set[int], List[int], int]):
        self.__staff_dict.del_staff_all(staff_ids)
        self.__dump()

    def groups_of_staff(self, staff_id: int) -> Set[int]:
        return self.__staff_dict.groups_of_staff(staff_id)
