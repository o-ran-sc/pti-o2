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

from o2ims.domain.stx_object import StxGenericModel
from o2common.service.client.base_client import BaseClient
# from o2common.service.unit_of_work import AbstractUnitOfWork
from o2common.service.watcher.base import BaseWatcher
from o2ims.domain import commands
from o2common.service.messagebus import MessageBus

from o2common.helper import o2logging
logger = o2logging.get_logger(__name__)


class ResourcePoolWatcher(BaseWatcher):

    def __init__(self, client: BaseClient,
                 bus: MessageBus) -> None:
        super().__init__(client, bus)

    def _targetname(self):
        return "resourcepool"

    def _probe(self, parent: StxGenericModel, tags: object = None):
        ocloudid = parent.id
        newmodels = self._client.list(ocloudid=ocloudid)
        # for newmodel in newmodels:
        #     logger.info("detect ocloudmodel:" + newmodel.name)
        #     super()._compare_and_update(newmodel)
        # return newmodels
        return [commands.UpdateResourcePool(data=m, parentid=ocloudid)
                for m in newmodels]
