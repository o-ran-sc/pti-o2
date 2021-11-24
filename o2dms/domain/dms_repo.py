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

import abc
from typing import List, Set
from o2dms.domain import dms


class NfDeploymentDescRepository(abc.ABC):
    def __init__(self):
        self.seen = set()  # type: Set[dms.NfDeploymentDesc]

    def add(self, nfdeployment_descriptor: dms.NfDeploymentDesc):
        self._add(nfdeployment_descriptor)
        self.seen.add(nfdeployment_descriptor)

    def get(self, nfdeployment_descriptor_id) -> dms.NfDeploymentDesc:
        nfdeployment_descriptor = self._get(nfdeployment_descriptor_id)
        if nfdeployment_descriptor:
            self.seen.add(nfdeployment_descriptor)
        return nfdeployment_descriptor

    def list(self) -> List[dms.NfDeploymentDesc]:
        return self._list()

    def update(self, id, **kwargs):
        self._update(id, **kwargs)

    def delete(self, nfdeployment_descriptor_id):
        self._delete(nfdeployment_descriptor_id)

    @abc.abstractmethod
    def _add(self, nfdeployment_descriptor: dms.NfDeploymentDesc):
        raise NotImplementedError

    @abc.abstractmethod
    def _get(self, nfdeployment_descriptor_id) -> dms.NfDeploymentDesc:
        raise NotImplementedError

    @abc.abstractmethod
    def _update(self, nfdeployment_descriptor: dms.NfDeploymentDesc):
        raise NotImplementedError

    @abc.abstractmethod
    def _delete(self, nfdeployment_descriptor_id):
        raise NotImplementedError
