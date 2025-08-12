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

    def _prune_stale_resourcepools_and_resources(self):
        """Prune DB resource pools that don't exist in the authoritative source.

        Steps for each prune cycle:

        Retrieve current pool IDs from client for the specified ocloud
        Get pool IDs from the database
        For each pool ID that exists only in DB:
        Remove all alarms associated with resources in that pool
        Delete all resources belonging to that pool
        Remove the resource pool itself
        """
        try:
            with self._bus.uow as uow:
                # Current pools from authoritative client
                current = self._client.list()
                current_ids = {m.id for m in current}

                # DB pools
                db_resourcepools_query = uow.resource_pools.list()
                db_resourcepools = db_resourcepools_query.all()
                db_resourcepools = list(db_resourcepools_query)
                db_ids = {r.resourcePoolId for r in db_resourcepools}

                # Pools present in DB but not in current authoritative list
                stale_ids = db_ids - current_ids
                if not stale_ids:
                    return

                # TODO: When a resource pool is deleted, the SMO must be
                #  notified.
                for pool_id in stale_ids:
                    # 1) Delete alarms for resources in this pool
                    alarms_del_result = uow.session.execute(
                        '''
                        DELETE FROM "alarmEventRecord" a
                        USING "resource" r
                        WHERE a."resourceId" = r."resourceId"
                          AND r."resourcePoolId" = :pool_id
                        ''',
                        dict(pool_id=pool_id)
                    )
                    alarms_del = getattr(alarms_del_result, 'rowcount', None)

                    # 2) Delete resources in this pool
                    res_list = uow.resources.list(pool_id)
                    res_objs = res_list.all()

                    for res in res_objs:
                        uow.resources.delete(res.resourceId)

                    resources_deleted = len(res_objs)
                    uow.resource_pools.delete(pool_id)

                    # Log per-pool pruning completion with counts
                    logger.info(
                        f'Pruned pool {pool_id}: alarms={alarms_del}, '
                        f'resources={resources_deleted}'
                    )

                uow.commit()
                # Summary log after pruning batch
                logger.info(
                    f'Pruned resource pools batch: {list(stale_ids)}'
                )
        except Exception as e:
            logger.error(
                f'Error pruning stale res pools/resources: {str(e)}'
            )

    def _probe(self, parent: StxGenericModel, tags: object = None):
        ocloudid = parent.id
        # Ensure we prune stale pools/resources before syncing
        #
        self._prune_stale_resourcepools_and_resources()
        newmodels = self._client.list(ocloudid=ocloudid)
        # for newmodel in newmodels:
        #     logger.info("detect ocloudmodel:" + newmodel.name)
        #     super()._compare_and_update(newmodel)
        # return newmodels
        return [commands.UpdateResourcePool(data=m, parentid=ocloudid)
                for m in newmodels]
