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
# from os import stat
import json
from o2dms.domain import events
from o2dms.domain.states import NfDeploymentState

from o2common.domain.base import AgRoot, Serializer


class NfDeploymentDesc(AgRoot, Serializer):
    def __init__(self, id: str, name: str, dmsId: str, description: str = '',
                 inputParams: str = '', outputParams: str = '',
                 artifactRepoUrl: str = '', artifactName: str = '') -> None:
        super().__init__()
        self.id = id
        self.version_number = 0
        self.deploymentManagerId = dmsId
        self.name = name
        self.description = description
        self.artifactRepoUrl = artifactRepoUrl
        self.artifactName = artifactName
        self.status = 0

        if type(inputParams) is str:
            inputParams = json.loads(inputParams)
        self.inputParams = json.dumps(inputParams)

        if type(outputParams) is str:
            outputParams = json.loads(outputParams)
        self.outputParams = json.dumps(outputParams)

        # self.extensions = []


class NfDeployment(AgRoot, Serializer):
    def __init__(self, id: str, name: str, dmsId: str, description: str = '',
                 descriptorId: str = '', parentId: str = '',) -> None:
        super().__init__()
        self.id = id
        self.version_number = 0
        self.deploymentManagerId = dmsId
        self.name = name
        self.description = description
        self.descriptorId = descriptorId
        self.parentDeploymentId = parentId
        self.status = NfDeploymentState.Initial

    def transit_state(self, state: NfDeploymentState):
        if (self.status != state):
            self._append_event(self.status, state)
            # self.status = state

    def set_state(self, state: NfDeploymentState):
        if (self.status != state):
            self.status = state

    def _append_event(self, fromState, toState):
        if not hasattr(self, "events"):
            self.events = []
        self.events.append(
            events.NfDeploymentStateChanged(
                NfDeploymentId=self.id, FromState=fromState, ToState=toState))


class NfOCloudVResource(AgRoot, Serializer):
    def __init__(self, id: str, name: str, dmsId: str, description: str = '',
                 descriptorId: str = '', nfDeploymentId: str = '',
                 vresourceType: int = 0,) -> None:
        super().__init__()
        self.id = id
        self.version_number = 0
        self.deploymentManagerId = dmsId
        self.name = name
        self.description = description
        self.descriptorId = descriptorId
        self.nfDeploymentId = nfDeploymentId
        self.vresourceType = vresourceType
        self.status = 0
        self.metadata = []
