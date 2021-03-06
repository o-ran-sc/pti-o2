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
from o2dms.domain.states import NfDeploymentState
# from o2dms.domain.dms import NfDeployment
# from datetime import datetime
# from o2ims.domain.resource_type import ResourceTypeEnum

from o2common.domain.commands import Command


@dataclass
class InstallNfDeployment(Command):
    NfDeploymentId: str


@dataclass
class UninstallNfDeployment(Command):
    NfDeploymentId: str


@dataclass
class DeleteNfDeployment(Command):
    NfDeploymentId: str


@dataclass
class HandleNfDeploymentStateChanged(Command):
    NfDeploymentId: str
    FromState: NfDeploymentState
    ToState: NfDeploymentState
