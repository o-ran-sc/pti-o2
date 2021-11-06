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

from o2ims.domain.resource_type import ResourceTypeEnum
from o2ims.service.client.base_client import BaseClient
from o2ims.domain.stx_object import StxGenericModel
from o2ims.service.unit_of_work import AbstractUnitOfWork

import logging
logger = logging.getLogger(__name__)


class InvalidOcloudState(Exception):
    pass


class BaseWatcher(object):
    def __init__(self, client: BaseClient) -> None:
        super().__init__()
        self._client = client

    def targetname(self) -> str:
        return self._targetname()

    def probe(self):
        self._probe()

    def _probe(self):
        raise NotImplementedError

    def _targetname(self):
        raise NotImplementedError


class OcloudWatcher(BaseWatcher):
    def __init__(self, ocloud_client: BaseClient,
                 uow: AbstractUnitOfWork) -> None:
        super().__init__(ocloud_client)
        self._uow = uow

    def _targetname(self):
        return "ocloud"

    def _probe(self):
        ocloudmodel = self._client.get(None)
        if ocloudmodel:
            self._compare_and_update(ocloudmodel)

    def _compare_and_update(self, ocloudmodel: StxGenericModel) -> bool:
        with self._uow:
            # localmodel = self._uow.stxobjects.get(str(ocloudmodel.id))
            oclouds = self._uow.stxobjects.list(ResourceTypeEnum.OCLOUD)
            if len(oclouds) > 1:
                raise InvalidOcloudState("More than 1 ocloud is found")
            if len(oclouds) == 0:
                logger.warning("add ocloud:" + ocloudmodel.name
                               + " update_at: " + str(ocloudmodel.updatetime)
                               + " id: " + str(ocloudmodel.id)
                               + " hash: "+ str(ocloudmodel.hash))
                self._uow.stxobjects.add(ocloudmodel)
            else:
                localmodel = oclouds.pop()
                if localmodel.is_outdated(ocloudmodel):
                    logger.warning("update ocloud:" + ocloudmodel.name
                                   + " update_at: " + str(ocloudmodel.updatetime)
                                   + " id: " + str(ocloudmodel.id)
                                   + " hash: "+ str(ocloudmodel.hash))
                    localmodel.update_by(ocloudmodel)
                    self._uow.stxobjects.update(localmodel)
            self._uow.commit()


class DmsWatcher(BaseWatcher):
    def __init__(self, client: BaseClient,
                 uow: AbstractUnitOfWork) -> None:
        super().__init__(client)
        self._uow = uow

    def _targetname(self):
        return "dms"

    def _probe(self):
        ocloudmodel = self._client.get(None)
        if ocloudmodel:
            self._compare_and_update(ocloudmodel)

    def _compare_and_update(self, newmodel: StxGenericModel) -> bool:
        with self._uow:
            # localmodel = self._uow.stxobjects.get(ocloudmodel.id)
            localmodel = self._uow.stxobjects.get(str(newmodel.id))
            if not localmodel:
                logger.warning("add dms:" + newmodel.name)
                self._uow.stxobjects.add(newmodel)
            elif localmodel.is_outdated(newmodel):
                logger.warning("update dms:" + newmodel.name)
                localmodel.update_by(newmodel)
                self._uow.stxobjects.update(newmodel)
            self._uow.commit()


class ResourcePoolWatcher(BaseWatcher):
    def __init__(self, client: BaseClient,
                 uow: AbstractUnitOfWork) -> None:
        super().__init__()
        self._uow = uow

    def _targetname(self):
        return "resourcepool"

    def _probe(self):
        ocloudmodel = self._client.get(None)
        if ocloudmodel:
            logger.warning("detect ocloudmodel:" + ocloudmodel.name)
            self._compare_and_update(ocloudmodel)

    def _compare_and_update(self, newmodel: StxGenericModel) -> bool:
        with self._uow:
            # localmodel = self._uow.stxobjects.get(ocloudmodel.id)
            localmodel = self._uow.stxobjects.get(str(newmodel.id))
            if not localmodel:
                self._uow.stxobjects.add(newmodel)
            elif localmodel.is_outdated(newmodel):
                localmodel.update_by(newmodel)
                self._uow.stxobjects.update(newmodel)
            self._uow.commit()


class ResourceWatcher(BaseWatcher):
    def __init__(self, client: BaseClient,
                 uow: AbstractUnitOfWork) -> None:
        super().__init__()
        self._uow = uow

    def _targetname(self):
        return "resource"

    def _probe(self):
        ocloudmodel = self._client.get(None)
        if ocloudmodel:
            self._compare_and_update(ocloudmodel)

    def _compare_and_update(self, newmodel: StxGenericModel) -> bool:
        with self._uow:
            # localmodel = self._repo.get(ocloudmodel.id)
            localmodel = self._uow.stxobjects.get(str(newmodel.id))
            if not localmodel:
                self._uow.stxobjects.add(newmodel)
            elif localmodel.is_outdated(newmodel):
                localmodel.update_by(newmodel)
                self._uow.stxobjects.update(newmodel)
            self._uow.commit()
