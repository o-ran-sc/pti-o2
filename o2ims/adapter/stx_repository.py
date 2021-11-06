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

from typing import List
# from o2ims.adapter import orm
from o2ims.domain.stx_object import StxGenericModel
from o2ims.domain.stx_repo import StxObjectRepository
from o2ims.domain.resource_type import ResourceTypeEnum


class StxObjectSqlAlchemyRepository(StxObjectRepository):
    def __init__(self, session):
        super().__init__()
        self.session = session

    def _add(self, stx_obj: StxGenericModel):
        self.session.add(stx_obj)

    def _get(self, stx_obj_id) -> StxGenericModel:
        return self.session.query(StxGenericModel).filter_by(
            id=stx_obj_id).first()

    def _list(self, type: ResourceTypeEnum) -> List[StxGenericModel]:
        return self.session.query(StxGenericModel).filter_by(
            type=type).order_by(StxGenericModel.updatetime.desc()).all()

    def _update(self, stx_obj: StxGenericModel):
        self.session.add(stx_obj)
