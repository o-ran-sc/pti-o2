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
                 inputParams: str = '', outputParams: str = '',) -> None:
        super().__init__()
        self.id = id
        self.version_number = 0
        self.dmsId = dmsId
        self.name = name
        self.description = description
        self.inputParams = inputParams
        self.outputParams = outputParams
        self.extensions = []
