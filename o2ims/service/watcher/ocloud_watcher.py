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

# from o2ims.domain.resource_type import ResourceTypeEnum
from o2common.service.client.base_client import BaseClient
from o2ims.domain.stx_object import StxGenericModel
# from o2common.service.unit_of_work import AbstractUnitOfWork
from o2common.service.watcher.base import BaseWatcher
from o2ims.domain import commands
from o2common.service.messagebus import MessageBus

from o2common.helper import o2logging
logger = o2logging.get_logger(__name__)


class OcloudWatcher(BaseWatcher):
    def __init__(self, ocloud_client: BaseClient,
                 bus: MessageBus) -> None:
        super().__init__(ocloud_client, bus)

    def _targetname(self):
        return "ocloud"

    def _probe(self, parent: object = None, tags: object = None):
        newmodel = self._client.get(None)
        if newmodel:
            logger.debug("found ocloud: " + newmodel.name)
        else:
            logger.warning("Failed to find out any ocloud")
        #     self._compare_and_update(ocloudmodel)
        return [commands.UpdateOCloud(newmodel)] if newmodel else []

# def _compare_and_update(self, ocloudmodel: StxGenericModel) -> bool:
#     with self._uow:
#         # localmodel = self._uow.stxobjects.get(str(ocloudmodel.id))
#         oclouds = self._uow.stxobjects.list(ResourceTypeEnum.OCLOUD)
#         if len(oclouds) > 1:
#             raise InvalidOcloudState("More than 1 ocloud is found")
#         if len(oclouds) == 0:
#             logger.info("add ocloud:" + ocloudmodel.name
#                         + " update_at: " + str(ocloudmodel.updatetime)
#                         + " id: " + str(ocloudmodel.id)
#                         + " hash: " + str(ocloudmodel.hash))
#             self._uow.stxobjects.add(ocloudmodel)
#         else:
#             localmodel = oclouds.pop()
#             if localmodel.is_outdated(ocloudmodel):
#                 logger.info("update ocloud:" + ocloudmodel.name
#                             + " update_at: " + str(ocloudmodel.updatetime)
#                             + " id: " + str(ocloudmodel.id)
#                             + " hash: " + str(ocloudmodel.hash))
#                 localmodel.update_by(ocloudmodel)
#                 self._uow.stxobjects.update(localmodel)
#         self._uow.commit()


class DmsWatcher(BaseWatcher):
    def __init__(self, client: BaseClient,
                 bus: MessageBus) -> None:
        super().__init__(client, bus)

    def _targetname(self):
        return "dms"

    def _probe(self, parent: StxGenericModel, tags: object = None):
        ocloudid = parent.id
        newmodels = self._client.list(ocloudid=ocloudid)
        # for newmodel in newmodels:
        #     super()._compare_and_update(newmodel)
        # return newmodels
        return [commands.UpdateDms(data=m, parentid=ocloudid)
                for m in newmodels]
