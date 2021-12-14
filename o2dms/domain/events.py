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
from dataclasses import dataclass
from o2dms.domain.states import NfDeploymentState
from o2common.domain.events import Event


@dataclass
class NfDeploymentStateChanged(Event):
    NfDeploymentId: str
    FromState: NfDeploymentState
    ToState: NfDeploymentState


# @dataclass
# class NfDeploymentCreated(Event):
#     NfDeploymentId: str


# @dataclass
# class NfDeploymentInstalled(Event):
#     NfDeploymentId: str


# @dataclass
# class NfDeploymentUninstalling(Event):
#     NfDeploymentId: str


# @dataclass
# class NfDeploymentUninstalled(Event):
#     NfDeploymentId: str


# @dataclass
# class NfDeploymentUpdating(Event):
#     NfDeploymentId: str


# @dataclass
# class NfDeploymentUpdated(Event):
#     NfDeploymentId: str


# @dataclass
# class NfDeploymentDeleted(Event):
#     NfDeploymentId: str
