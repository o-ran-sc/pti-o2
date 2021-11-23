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

# pylint: disable=attribute-defined-outside-init
from __future__ import annotations
import abc

from o2ims.domain.ocloud_repo import OcloudRepository,\
    ResourcePoolRepository, ResourceRepository, ResourceTypeRepository,\
    DeploymentManagerRepository
from o2ims.domain.stx_repo import StxObjectRepository


class AbstractUnitOfWork(abc.ABC):
    oclouds: OcloudRepository
    resource_types: ResourceTypeRepository
    resource_pools: ResourcePoolRepository
    resources: ResourceRepository
    deployment_managers: DeploymentManagerRepository
    stxobjects: StxObjectRepository

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.rollback()

    def commit(self):
        self._commit()

    def collect_new_events(self):
        return self._collect_new_events()

    def _collect_new_events(self):
        raise NotImplementedError

    @abc.abstractmethod
    def _commit(self):
        raise NotImplementedError

    @abc.abstractmethod
    def rollback(self):
        raise NotImplementedError
