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

# pylint: disable=too-few-public-methods
# from datetime import date
# from typing import Optional
from dataclasses import dataclass
# from datetime import datetime
# from o2ims.domain.resource_type import ResourceTypeEnum
from o2ims.domain.stx_object import StxGenericModel
from o2ims.domain.subscription_obj import Message2SMO
from o2common.domain.commands import Command


@dataclass
class UpdateStxObject(Command):
    data: StxGenericModel


@dataclass
class PubMessage2SMO(Command):
    data: Message2SMO


@dataclass
class UpdateOCloud(UpdateStxObject):
    pass


@dataclass
class UpdateDms(UpdateStxObject):
    parentid: str


@dataclass
class UpdateResourcePool(UpdateStxObject):
    parentid: str


@dataclass
class UpdateResourceType(UpdateStxObject):
    parentid: str


@dataclass
class UpdateResource(UpdateStxObject):
    parentid: str


@dataclass
class UpdatePserver(UpdateResource):
    pass


@dataclass
class UpdatePserverCpu(UpdateResource):
    pass


@dataclass
class UpdatePserverMem(UpdateResource):
    pass


@dataclass
class UpdatePserverEth(UpdateResource):
    pass


@dataclass
class UpdatePserverIf(UpdateResource):
    pass


@dataclass
class UpdatePserverIfPort(UpdateResource):
    pass
