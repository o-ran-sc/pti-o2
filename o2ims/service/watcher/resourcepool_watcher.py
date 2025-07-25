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

    def _prune_stale_resourcepools_and_resources(self, ocloudid):
        """Prune resource pools (subclouds) and their related resources from DB if they no longer exist in the authoritative source."""
        try:
            with self._bus.uow as uow:
                # 1. Get current resource pool IDs from authoritative source (client)
                current_resourcepools = self._client.list(ocloudid=ocloudid)
                current_ids = set(r.id for r in current_resourcepools)

                # 2. Get all resource pool IDs from DB
                db_resourcepools = uow.resource_pools.list()
                db_ids = set(r.resourcePoolId for r in db_resourcepools)

                # 3. Delete any in DB not in current
                deleted_ids = db_ids - current_ids

                # TODO: When an resource and resource pool is deleted, the SMO must be notified.

                for del_id in deleted_ids:
                    # Delete all related resources first
                    if hasattr(uow, 'resources'):
                        db_resources = uow.resources.list(del_id)
                        db_resources = db_resources.all()
                        for res in db_resources:
                            uow.resources.delete(res.resourceId)
                    uow.resource_pools.delete(del_id)
                if deleted_ids:
                    logger.info(f'Pruned resource pools and related resources: {deleted_ids}')
                    uow.commit()
        except Exception as e:
            logger.error(f'Error pruning stale resource pools/resources: {str(e)}')

    def _probe(self, parent: StxGenericModel, tags: object = None):
        ocloudid = parent.id
        self._prune_stale_resourcepools_and_resources(ocloudid)
        newmodels = self._client.list(ocloudid=ocloudid)
        # for newmodel in newmodels:
        #     logger.info("detect ocloudmodel:" + newmodel.name)
        #     super()._compare_and_update(newmodel)
        # return newmodels
        return [commands.UpdateResourcePool(data=m, parentid=ocloudid)
                for m in newmodels]
