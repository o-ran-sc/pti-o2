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

from __future__ import annotations
from enum import Enum
# from dataclasses import dataclass

from o2common.domain.base import AgRoot, Serializer


class RegistrationStatusEnum(str, Enum):
    CREATED = 'CREATED'
    NOTIFIED = 'NOTIFIED'
    FAILED = 'FAILED'


class ConfigurationTypeEnum(str, Enum):
    SMO = 'SMO'


class Configuration(AgRoot, Serializer):
    def __init__(self, id: str, url: str,
                 conf_type: ConfigurationTypeEnum,
                 status: RegistrationStatusEnum =
                 RegistrationStatusEnum.CREATED,
                 comments: str = '') -> None:
        super().__init__()
        self.configurationId = id
        self.conftype = conf_type
        self.callback = url
        self.status = status
        self.comments = comments

    def serialize_smo(self):
        if self.conftype != ConfigurationTypeEnum.SMO:
            return

        d = Serializer.serialize(self)

        d['endpoint'] = d['callback']
        return d
