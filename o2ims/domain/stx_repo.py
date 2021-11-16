# Copyright (C) 2021 Wind River Systems, Inc.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import abc
from typing import List, Set
from o2ims.domain.stx_object import StxGenericModel
from o2ims.domain.resource_type import ResourceTypeEnum


class StxObjectRepository(abc.ABC):
    def __init__(self):
        self.seen = set()  # type: Set[StxGenericModel]

    def add(self, stx_obj: StxGenericModel):
        self._add(stx_obj)
        self.seen.add(stx_obj)

    def get(self, stx_obj_id) -> StxGenericModel:
        stx_obj = self._get(stx_obj_id)
        if stx_obj:
            self.seen.add(stx_obj)
        return stx_obj

    def list(self, type: ResourceTypeEnum) -> List[StxGenericModel]:
        return self._list(type)

    def update(self, stx_obj: StxGenericModel):
        self._update(stx_obj)
        self.seen.add(stx_obj)

    # def update_fields(self, stx_obj_id: str, updatefields: dict):
    #     self._update(stx_obj_id, updatefields)

    @abc.abstractmethod
    def _add(self, stx_obj: StxGenericModel):
        raise NotImplementedError

    @abc.abstractmethod
    def _get(self, stx_obj_id) -> StxGenericModel:
        raise NotImplementedError

    @abc.abstractmethod
    def _update(self, stx_obj: StxGenericModel):
        raise NotImplementedError

    @abc.abstractmethod
    def _list(self, type: ResourceTypeEnum):
        raise NotImplementedError
