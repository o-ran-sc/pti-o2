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
from o2ims.domain import ocloud
from o2ims.domain.ocloud_repo import OcloudRepository


class OcloudSqlAlchemyRepository(OcloudRepository):
    def __init__(self, session):
        super().__init__()
        self.session = session

    def _add(self, ocloud: ocloud.Ocloud):
        self.session.add(ocloud)
        # self.session.add_all(ocloud.deploymentManagers)

    def _get(self, ocloudid) -> ocloud.Ocloud:
        return self.session.query(ocloud.Ocloud).filter_by(
            oCloudId=ocloudid).first()

    def _list(self) -> List[ocloud.Ocloud]:
        return self.session.query(ocloud.Ocloud).order_by(
            ocloud.Ocloud.name).all()

    def _update(self, ocloud: ocloud.Ocloud):
        self.session.add(ocloud)
