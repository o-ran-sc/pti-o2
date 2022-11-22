# Copyright (C) 2022 Wind River Systems, Inc.
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
import json

from o2ims.domain import events
from o2ims.domain.stx_object import StxGenericModel
from o2ims.domain.subscription_obj import NotificationEventEnum
from o2ims.domain.resource_type import MismatchedModel
from o2ims.domain.ocloud import Resource

from o2common.helper import o2logging
logger = o2logging.get_logger(__name__)


class InvalidResourceType(Exception):
    pass


def is_outdated(resource: Resource, stxobj: StxGenericModel):
    return True if resource.hash != stxobj.hash else False


def create_by(stxobj: StxGenericModel, parent: Resource, resourcetype_id: str)\
        -> Resource:
    resourcetype_id = resourcetype_id
    resourcepool_id = parent.resourcePoolId
    parent_id = parent.resourceId
    gAssetId = ''  # TODO: global ID
    extensions = json.dumps(stxobj.filtered)
    description = ";".join([f"{k}:{v}" for k, v in stxobj.filtered.items()])
    resource = Resource(stxobj.id, resourcetype_id, resourcepool_id,
                        parent_id, gAssetId, stxobj.content, description,
                        extensions)
    resource.createtime = stxobj.createtime
    resource.updatetime = stxobj.updatetime
    resource.hash = stxobj.hash

    return resource


def update_by(target: Resource, stxobj: StxGenericModel, parent: Resource)\
        -> None:
    if target.resourceId != stxobj.id:
        raise MismatchedModel("Mismatched Id")
    target.updatetime = stxobj.updatetime
    target.hash = stxobj.hash
    target.elements = stxobj.content
    target.extensions = json.dumps(stxobj.filtered)
    target.description = ";".join(
        [f"{k}:{v}" for k, v in stxobj.filtered.items()])
    target.version_number = target.version_number + 1
    target.events.append(events.ResourceChanged(
        id=stxobj.id,
        resourcePoolId=target.resourcePoolId,
        notificationEventType=NotificationEventEnum.MODIFY,
        updatetime=stxobj.updatetime
    ))
