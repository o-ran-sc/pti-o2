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
from o2ims.domain import ocloud


class OcloudRepository(abc.ABC):
    def __init__(self):
        self.seen = set()  # type: Set[ocloud.Ocloud]

    def add(self, ocloud: ocloud.Ocloud):
        self._add(ocloud)
        self.seen.add(ocloud)

    def get(self, ocloud_id) -> ocloud.Ocloud:
        ocloud = self._get(ocloud_id)
        if ocloud:
            self.seen.add(ocloud)
        return ocloud

    def list(self) -> List[ocloud.Ocloud]:
        return self._list()

    def update(self, ocloud: ocloud.Ocloud):
        self._update(ocloud)
        self.seen.add(ocloud)

    # def update_fields(self, ocloudid: str, updatefields: dict):
    #     self._update(ocloudid, updatefields)

    @abc.abstractmethod
    def _add(self, ocloud: ocloud.Ocloud):
        raise NotImplementedError

    @abc.abstractmethod
    def _get(self, ocloud_id) -> ocloud.Ocloud:
        raise NotImplementedError

    @abc.abstractmethod
    def _update(self, ocloud: ocloud.Ocloud):
        raise NotImplementedError


class ResourceTypeRepository(abc.ABC):
    def __init__(self):
        self.seen = set()  # type: Set[ocloud.ResourceType]

    def add(self, resource_type: ocloud.ResourceType):
        self._add(resource_type)
        self.seen.add(resource_type)

    def get(self, resource_type_id) -> ocloud.ResourceType:
        resource_type = self._get(resource_type_id)
        if resource_type:
            self.seen.add(resource_type)
        return resource_type

    def list(self) -> List[ocloud.ResourceType]:
        return self._list()

    def update(self, resource_type: ocloud.ResourceType):
        self._update(resource_type)
        self.seen.add(resource_type)

    @abc.abstractmethod
    def _add(self, resource_type: ocloud.ResourceType):
        raise NotImplementedError

    @abc.abstractmethod
    def _get(self, resource_type_id) -> ocloud.ResourceType:
        raise NotImplementedError

    @abc.abstractmethod
    def _update(self, resource_type: ocloud.ResourceType):
        raise NotImplementedError


class ResourcePoolRepository(abc.ABC):
    def __init__(self):
        self.seen = set()  # type: Set[ocloud.ResourcePool]

    def add(self, resource_pool: ocloud.ResourcePool):
        self._add(resource_pool)
        self.seen.add(resource_pool)

    def get(self, resource_pool_id) -> ocloud.ResourcePool:
        resource_pool = self._get(resource_pool_id)
        if resource_pool:
            self.seen.add(resource_pool)
        return resource_pool

    def list(self) -> List[ocloud.ResourcePool]:
        return self._list()

    def update(self, resource_pool: ocloud.ResourcePool):
        self._update(resource_pool)
        self.seen.add(resource_pool)

    @abc.abstractmethod
    def _add(self, resource_pool: ocloud.ResourcePool):
        raise NotImplementedError

    @abc.abstractmethod
    def _get(self, resource_pool_id) -> ocloud.ResourcePool:
        raise NotImplementedError

    @abc.abstractmethod
    def _update(self, resource_pool: ocloud.ResourcePool):
        raise NotImplementedError


class ResourceRepository(abc.ABC):
    def __init__(self):
        self.seen = set()  # type: Set[ocloud.Resource]

    def add(self, resource: ocloud.Resource):
        self._add(resource)
        self.seen.add(resource)

    def get(self, resource_id) -> ocloud.Resource:
        resource = self._get(resource_id)
        if resource:
            self.seen.add(resource)
        return resource

    def list(self, resourcepool_id) -> List[ocloud.Resource]:
        return self._list(resourcepool_id)

    def update(self, resource: ocloud.Resource):
        self._update(resource)
        self.seen.add(resource)

    @abc.abstractmethod
    def _add(self, resource: ocloud.Resource):
        raise NotImplementedError

    @abc.abstractmethod
    def _get(self, resource_id) -> ocloud.Resource:
        raise NotImplementedError

    @abc.abstractmethod
    def _update(self, resource: ocloud.Resource):
        raise NotImplementedError


class DeploymentManagerRepository(abc.ABC):
    def __init__(self):
        self.seen = set()  # type: Set[ocloud.DeploymentManager]

    def add(self, deployment_manager: ocloud.DeploymentManager):
        self._add(deployment_manager)
        self.seen.add(deployment_manager)

    def get(self, deployment_manager_id) -> ocloud.DeploymentManager:
        deployment_manager = self._get(deployment_manager_id)
        if deployment_manager:
            self.seen.add(deployment_manager)
        return deployment_manager

    def list(self) -> List[ocloud.DeploymentManager]:
        return self._list()

    def update(self, deployment_manager: ocloud.DeploymentManager):
        self._update(deployment_manager)

    @abc.abstractmethod
    def _add(self, deployment_manager: ocloud.DeploymentManager):
        raise NotImplementedError

    @abc.abstractmethod
    def _get(self, deployment_manager_id) -> ocloud.DeploymentManager:
        raise NotImplementedError

    @abc.abstractmethod
    def _update(self, deployment_manager: ocloud.DeploymentManager):
        raise NotImplementedError
