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

from o2ims.service.client.base_client import BaseClient
from o2ims.service.unit_of_work import AbstractUnitOfWork
from o2ims.service.watcher.resource_watcher import ResourceWatcher

from o2common.helper import logger
logger = logger.get_logger(__name__)


class PServerWatcher(ResourceWatcher):
    def __init__(self, client: BaseClient,
                 uow: AbstractUnitOfWork) -> None:
        super().__init__(client, uow)

    def _targetname(self):
        return "pserver"

    def _probe(self, parent: object = None):
        resourcepoolid = parent.id if parent else None
        newmodels = self._client.list(resourcepoolid=resourcepoolid)
        for newmodel in newmodels:
            super()._compare_and_update(newmodel)
        return newmodels
