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

from o2common.domain.base import AgRoot


class NfDeploymentDesc(AgRoot):
    def __init__(self, id: str, name: str, dmsId: str, description: str = '',
                 inputParams: str = '', outputParams: str = '',
                 artifacturl: str = '') -> None:
        super().__init__()
        self.id = id
        self.version_number = 0
        self.deploymentManagerId = dmsId
        self.name = name
        self.description = description
        self.inputParams = inputParams
        self.outputParams = outputParams
        self.artifactUrl = artifacturl
        # self.extensions = []


class NfDeployment(AgRoot):
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
        self.status = 0


class NfOCloudVResource(AgRoot):
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
