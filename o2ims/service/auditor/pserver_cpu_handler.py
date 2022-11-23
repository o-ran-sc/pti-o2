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
import json

from o2ims.domain import commands, events
from o2ims.domain.stx_object import StxGenericModel
from o2common.service.unit_of_work import AbstractUnitOfWork
from o2ims.domain.resource_type import MismatchedModel
from o2ims.domain.ocloud import Resource, ResourceType
from o2ims.domain.subscription_obj import NotificationEventEnum

from o2common.helper import o2logging
logger = o2logging.get_logger(__name__)


class InvalidResourceType(Exception):
    pass


def update_pserver_cpu(
    cmd: commands.UpdatePserverCpu,
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
            res_type_name = 'pserver_cpu'
            resourcetype_id = str(uuid.uuid3(
                uuid.NAMESPACE_URL, res_type_name))
            res_type = ResourceType(
                resourcetype_id,
                res_type_name, stxobj.type,
                description='A CPU resource type of the Physical Server')
            dict_id = str(uuid.uuid3(
                uuid.NAMESPACE_URL,
                str(f"{res_type_name}_alarmdictionary")))
            alarm_dictionary = uow.alarm_dictionaries.get(dict_id)
            if alarm_dictionary:
                res_type.alarmDictionary = alarm_dictionary
            uow.resource_types.add(res_type)
        else:
            resourcetype_id = first['resourceTypeId']

        resource = uow.resources.get(stxobj.id)
        if not resource:
            logger.info("add the cpu of pserver:" + stxobj.name
                        + " update_at: " + str(stxobj.updatetime)
                        + " id: " + str(stxobj.id)
                        + " hash: " + str(stxobj.hash))
            localmodel = create_by(stxobj, p_resource, resourcetype_id)
            uow.resources.add(localmodel)

            logger.info("Add the cpu of pserver: " + stxobj.id
                        + ", name: " + stxobj.name)
        else:
            localmodel = resource
            if is_outdated(localmodel, stxobj):
                logger.info("update cpu of pserver:" + stxobj.name
                            + " update_at: " + str(stxobj.updatetime)
                            + " id: " + str(stxobj.id)
                            + " hash: " + str(stxobj.hash))
                update_by(localmodel, stxobj, p_resource)
                uow.resources.update(localmodel)

            logger.info("Update the cpu of pserver: " + stxobj.id
                        + ", name: " + stxobj.name)
        uow.commit()


def is_outdated(resource: Resource, stxobj: StxGenericModel):
    return True if resource.hash != stxobj.hash else False


def create_by(stxobj: StxGenericModel, parent: Resource, resourcetype_id: str)\
        -> Resource:
    # content = json.loads(stxobj.content)
    resourcetype_id = resourcetype_id
    resourcepool_id = parent.resourcePoolId
    parent_id = parent.resourceId
    gAssetId = ''  # TODO: global ID
    # description = "%s : A CPU resource of the physical server" % stxobj.name
    content = json.loads(stxobj.content)
    selected_keys = [
        "cpu", "core", "thread", "allocated_function", "numa_node",
        "cpu_model", "cpu_family"
    ]
    filtered = dict(
        filter(lambda item: item[0] in selected_keys, content.items()))
    extensions = json.dumps(filtered)
    description = ";".join([f"{k}:{v}" for k, v in filtered.items()])
    resource = Resource(stxobj.id, resourcetype_id, resourcepool_id,
                        parent_id, gAssetId, stxobj.content, description,
                        extensions)
    resource.createtime = stxobj.createtime
    resource.updatetime = stxobj.updatetime
    resource.hash = stxobj.hash

    return resource


def update_by(target: Resource, stxobj: StxGenericModel,
              parentid: str) -> None:
    if target.resourceId != stxobj.id:
        raise MismatchedModel("Mismatched Id")
    target.createtime = stxobj.createtime
    target.updatetime = stxobj.updatetime
    target.hash = stxobj.hash
    target.version_number = target.version_number + 1
    target.events.append(events.ResourceChanged(
        id=stxobj.id,
        resourcePoolId=target.resourcePoolId,
        notificationEventType=NotificationEventEnum.MODIFY,
        updatetime=stxobj.updatetime
    ))
