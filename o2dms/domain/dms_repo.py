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


class NfDeploymentRepository(abc.ABC):
    def __init__(self):
        self.seen = set()  # type: Set[dms.NfDeployment]

    def add(self, nfdeployment: dms.NfDeployment):
        self._add(nfdeployment)
        self.seen.add(nfdeployment)

    def get(self, nfdeployment_id) -> dms.NfDeployment:
        nfdeployment = self._get(nfdeployment_id)
        if nfdeployment:
            self.seen.add(nfdeployment)
        return nfdeployment

    def list(self) -> List[dms.NfDeployment]:
        return self._list()

    def update(self, id, **kwargs):
        self._update(id, **kwargs)

    def delete(self, nfdeployment_id):
        self._delete(nfdeployment_id)

    def count(self, **kwargs):
        return self._count(**kwargs)

    @abc.abstractmethod
    def _add(self, nfdeployment: dms.NfDeployment):
        raise NotImplementedError

    @abc.abstractmethod
    def _get(self, nfdeployment_id) -> dms.NfDeployment:
        raise NotImplementedError

    @abc.abstractmethod
    def _update(self,  id, **kwargs):
        raise NotImplementedError

    @abc.abstractmethod
    def _delete(self, nfdeployment_id):
        raise NotImplementedError

    @abc.abstractmethod
    def _count(self, **kwargs):
        raise NotImplementedError


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

    def count(self, **kwargs):
        return self._count(**kwargs)

    @abc.abstractmethod
    def _add(self, nfdeployment_descriptor: dms.NfDeploymentDesc):
        raise NotImplementedError

    @abc.abstractmethod
    def _get(self, nfdeployment_descriptor_id) -> dms.NfDeploymentDesc:
        raise NotImplementedError

    @abc.abstractmethod
    def _update(self,  id, **kwargs):
        raise NotImplementedError

    @abc.abstractmethod
    def _delete(self, nfdeployment_descriptor_id):
        raise NotImplementedError

    @abc.abstractmethod
    def _count(self, **kwargs):
        raise NotImplementedError


class NfOCloudVResourceRepository(abc.ABC):
    def __init__(self):
        self.seen = set()  # type: Set[dms.NfOCloudVResource]

    def add(self, nfocloudvres: dms.NfOCloudVResource):
        self._add(nfocloudvres)
        self.seen.add(nfocloudvres)

    def get(self, nfocloudvres_id) -> dms.NfOCloudVResource:
        nfocloudvres = self._get(nfocloudvres_id)
        if nfocloudvres:
            self.seen.add(nfocloudvres)
        return nfocloudvres

    def list(self) -> List[dms.NfOCloudVResource]:
        return self._list()

    def update(self, nfocloudvres_id, **kwargs):
        self._update(nfocloudvres_id, **kwargs)

    def delete(self, nfocloudvres_id):
        self._delete(nfocloudvres_id)

    @abc.abstractmethod
    def _add(self, nfocloudvres: dms.NfOCloudVResource):
        raise NotImplementedError

    @abc.abstractmethod
    def _get(self, nfocloudvres_id) -> dms.NfOCloudVResource:
        raise NotImplementedError

    @abc.abstractmethod
    def _update(self,  nfocloudvres_id, **kwargs):
        raise NotImplementedError

    @abc.abstractmethod
    def _delete(self, nfocloudvres_id):
        raise NotImplementedError
