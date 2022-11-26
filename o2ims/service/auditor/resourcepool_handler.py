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

# pylint: disable=unused-argument
from __future__ import annotations
import json

from o2ims.domain.stx_object import StxGenericModel
# from dataclasses import asdict
# from typing import List, Dict, Callable, Type
# TYPE_CHECKING
from o2ims.domain import commands, events
from o2common.service.unit_of_work import AbstractUnitOfWork
# from o2ims.domain.resource_type import InvalidOcloudState
from o2ims.domain.resource_type import MismatchedModel
from o2ims.domain.ocloud import ResourcePool
from o2ims.domain.subscription_obj import NotificationEventEnum
# if TYPE_CHECKING:
#     from . import unit_of_work

from o2common.helper import o2logging
logger = o2logging.get_logger(__name__)


class InvalidResourceType(Exception):
    pass


def update_resourcepool(
    cmd: commands.UpdateResourcePool,
    uow: AbstractUnitOfWork
):
    stxobj = cmd.data
    with uow:
        resource_pool = uow.resource_pools.get(stxobj.id)
        if not resource_pool:
            logger.info("add resource pool:" + stxobj.name
                        + " update_at: " + str(stxobj.updatetime)
                        + " id: " + str(stxobj.id)
                        + " hash: " + str(stxobj.hash))
            localmodel = create_by(stxobj, cmd.parentid)
            uow.resource_pools.add(localmodel)

            logger.info("Add the resource pool: " + stxobj.id
                        + ", name: " + stxobj.name)
        else:
            localmodel = resource_pool
            if is_outdated(localmodel, stxobj):
                logger.info("update resource pool:" + stxobj.name
                            + " update_at: " + str(stxobj.updatetime)
                            + " id: " + str(stxobj.id)
                            + " hash: " + str(stxobj.hash))
                update_by(localmodel, stxobj, cmd.parentid)
                uow.resource_pools.update(localmodel)

            logger.info("Update the resource pool: " + stxobj.id
                        + ", name: " + stxobj.name)
        uow.commit()


def is_outdated(resourcepool: ResourcePool, stxobj: StxGenericModel):
    return True if resourcepool.hash != stxobj.hash else False


def create_by(stxobj: StxGenericModel, parentid: str) -> ResourcePool:
    content = json.loads(stxobj.content)
    globalLocationId = ''  # to be updated
    description = "A Resource Pool"
    location = content['location'] if content['location'] is not None else ''
    resourcepool = ResourcePool(stxobj.id, stxobj.name,
                                location,
                                parentid, globalLocationId, description)
    resourcepool.createtime = stxobj.createtime
    resourcepool.updatetime = stxobj.updatetime
    resourcepool.hash = stxobj.hash
    resourcepool.events.append(events.ResourcePoolChanged(
        id=stxobj.id,
        notificationEventType=NotificationEventEnum.CREATE,
        updatetime=stxobj.updatetime
    ))
    return resourcepool


def update_by(target: ResourcePool, stxobj: StxGenericModel,
              parentid: str) -> None:
    if target.resourcePoolId != stxobj.id:
        raise MismatchedModel("Mismatched Id")
    content = json.loads(stxobj.content)
    target.name = stxobj.name
    target.location = content['location'] if content['location'] is not None \
        else ''
    target.createtime = stxobj.createtime
    target.updatetime = stxobj.updatetime
    target.hash = stxobj.hash
    target.oCloudId = parentid
    target.version_number = target.version_number + 1
    target.events.append(events.ResourcePoolChanged(
        id=stxobj.id,
        notificationEventType=NotificationEventEnum.MODIFY,
        updatetime=stxobj.updatetime
    ))
