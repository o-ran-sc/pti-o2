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

# from dataclasses import dataclass
import datetime
import json
from o2common.domain.base import AgRoot

from o2ims.domain.resource_type import ResourceTypeEnum, MismatchedModel
from o2common.helper import o2logging
logger = o2logging.get_logger(__name__)


class StxGenericModel(AgRoot):
    def __init__(self, type: ResourceTypeEnum,
                 api_response: dict = None, content_hash=None) -> None:
        super().__init__()
        if api_response:
            self.id = str(api_response.uuid)
            self.type = type
            self.name = api_response.name
            self.updatetime = datetime.datetime.strptime(
                api_response.updated_at.split('.')[0], "%Y-%m-%dT%H:%M:%S") \
                if api_response.updated_at else None
            self.createtime = datetime.datetime.strptime(
                api_response.created_at.split('.')[0], "%Y-%m-%dT%H:%M:%S") \
                if api_response.created_at else None
            self.hash = content_hash
            if not self.hash:
                if hasattr(api_response, 'filtered'):
                    self.filtered = api_response.filtered
                    self.hash = str(hash((self.id, str(self.filtered))))
                else:
                    self.hash = str(hash((self.id, self.updatetime)))
            self.content = json.dumps(api_response.to_dict())
            if ResourceTypeEnum.RESOURCE_POOL == type:
                self.res_pool_id = self.id

    def is_outdated(self, newmodel) -> bool:
        # return self.updatetime < newmodel.updatetime
        # logger.warning("hash1: " + self.hash + " vs hash2: " + newmodel.hash)
        return self.hash != newmodel.hash

    def update_by(self, newmodel) -> None:
        if self.id != newmodel.id:
            raise MismatchedModel("Mismatched model")
        self.name = newmodel.name
        self.createtime = newmodel.createtime
        self.updatetime = newmodel.updatetime
        self.content = newmodel.content
