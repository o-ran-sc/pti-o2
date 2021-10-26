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
from typing import Set
# from o2ims.adapter import orm
from o2ims.domain import ocloud


class OcloudRepository(abc.ABC):
    def __init__(self):
        self.seen = set()  # type: Set[ocloud.Ocloud]

    def add(self, ocloud: ocloud.Ocloud):
        self._add(ocloud)
        self.seen.add(ocloud)

    def get(self, ocloudid) -> ocloud.Ocloud:
        ocloud = self._get(ocloudid)
        if ocloud:
            self.seen.add(ocloud)
        return ocloud

    def update(self, ocloud: ocloud.Ocloud):
        self._update(ocloud)

    # def update_fields(self, ocloudid: str, updatefields: dict):
    #     self._update(ocloudid, updatefields)

    @abc.abstractmethod
    def _add(self, ocloud: ocloud.Ocloud):
        raise NotImplementedError

    @abc.abstractmethod
    def _get(self, ocloudid) -> ocloud.Ocloud:
        raise NotImplementedError

    @abc.abstractmethod
    def _update(self, ocloud: ocloud.Ocloud):
        raise NotImplementedError


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

    def _update(self, ocloud: ocloud.Ocloud):
        self.session.add(ocloud)

    # def _update_fields(self, ocloudid: str, updatefields: dict):
    #     dmslist = updatefields.pop("deploymentManagers", None)
    #     if dmslist:
    #         self._update_dms_list(dmslist)
    #     if updatefields:
    #         self.session.query(ocloud.Ocloud).filter_by(
    # oCloudId=ocloudid).update(updatefields)

    # def _update_dms_list(self, dms_list: list):
    #     for dms in dms_list or []:
    #         self.session.query(ocloud.DeploymentManager).filter_by(
    # deploymentManagerId=dms.deploymentManagerId).update(dms)
