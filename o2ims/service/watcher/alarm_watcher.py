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

from o2common.domain import tags
from o2common.service.messagebus import MessageBus
from o2common.service.watcher.base import BaseWatcher
from o2common.service.client.base_client import BaseClient

from o2ims.domain import commands
from o2ims.domain.stx_object import StxGenericModel

from o2common.helper import o2logging
logger = o2logging.get_logger(__name__)


class AlarmWatcher(BaseWatcher):
    def __init__(self, fault_client: BaseClient,
                 bus: MessageBus) -> None:
        super().__init__(fault_client, bus)
        self._tags = tags.Tag()
        self.poolid = None

    def _targetname(self):
        return "alarm"

    def _probe(self, parent: StxGenericModel, tags: object = None):
        # Set a tag for children resource
        self._tags.pool = parent.res_pool_id
        self._set_respool_client()

        resourcepoolid = parent.id
        newmodels = self._client.list()
        return [commands.UpdateAlarm(m, resourcepoolid) for m in newmodels] \
            if len(newmodels) > 0 else []

    def _set_respool_client(self):
        self.poolid = self._tags.pool
        self._client.set_pool_driver(self.poolid)
