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
import uuid

from o2common.service.unit_of_work import AbstractUnitOfWork
from o2ims.domain import commands, events
from o2ims.domain.ocloud import ResourceType
from o2ims.domain.subscription_obj import NotificationEventEnum
from o2ims.service.auditor.pserver_res_handler import is_outdated, \
    create_by, update_by

from o2common.helper import o2logging
logger = o2logging.get_logger(__name__)


def update_pserver_dev(
    cmd: commands.UpdatePserverDev,
    uow: AbstractUnitOfWork
):
    stxobj = cmd.data
    with uow:
        p_resource = uow.resources.get(cmd.parentid)
        # resourcepool = uow.resource_pools.get(p_resource.resourcePoolId)

        res = uow.session.execute(
            '''
            SELECT "resourceTypeId", "name"
            FROM "resourceType"
            WHERE "resourceTypeEnum" = :resource_type_enum
            ''',
            dict(resource_type_enum=stxobj.type.name)
        )
        first = res.first()
        if first is None:
            res_type_name = 'pserver_dev'
            resourcetype_id = str(uuid.uuid3(
                uuid.NAMESPACE_URL, res_type_name))
            res_type = ResourceType(
                resourcetype_id,
                res_type_name, stxobj.type,
                description='A Device resource type of Physical Server')
            dict_id = str(uuid.uuid3(
                uuid.NAMESPACE_URL,
                str(f"{res_type_name}_alarmdictionary")))
            alarm_dictionary = uow.alarm_dictionaries.get(dict_id)
            if alarm_dictionary:
                res_type.alarmDictionary = alarm_dictionary
            res_type.events.append(events.ResourceTypeChanged(
                id=res_type.resourceTypeId,
                notificationEventType=NotificationEventEnum.CREATE,
                updatetime=stxobj.updatetime))
            uow.resource_types.add(res_type)
        else:
            resourcetype_id = first['resourceTypeId']

        resource = uow.resources.get(stxobj.id)
        if not resource:
            logger.info("add the device of pserver:" + stxobj.name
                        + " update_at: " + str(stxobj.updatetime)
                        + " id: " + str(stxobj.id)
                        + " hash: " + str(stxobj.hash))
            localmodel = create_by(stxobj, p_resource, resourcetype_id)
            uow.resources.add(localmodel)

            logger.info("Add the device of pserver: " + stxobj.id
                        + ", name: " + stxobj.name)
        else:
            localmodel = resource
            if is_outdated(localmodel, stxobj):
                logger.info("update device of pserver:" + stxobj.name
                            + " update_at: " + str(stxobj.updatetime)
                            + " id: " + str(stxobj.id)
                            + " hash: " + str(stxobj.hash))
                update_by(localmodel, stxobj, p_resource)
                uow.resources.update(localmodel)

            logger.info("Update the device of pserver: " + stxobj.id
                        + ", name: " + stxobj.name)
        uow.commit()
