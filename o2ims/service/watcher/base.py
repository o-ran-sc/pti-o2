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

from o2ims.service.client.base_client import BaseClient
from o2ims.domain.stx_object import StxGenericModel
from o2ims.adapter.ocloud_repository import OcloudRepository


class InvalidOcloudState(Exception):
    pass


class BaseWatcher(object):
    def __init__(self, client: BaseClient) -> None:
        super().__init__()
        self._client = client

    def probe(self):
        self._probe()

    def _probe(self):
        pass


class OcloudWather(BaseWatcher):
    def __init__(self, ocloud_client: BaseClient,
                 repo: OcloudRepository) -> None:
        super().__init__(ocloud_client)
        self._repo = repo

    def _probe(self):
        ocloudmodel = self._client.get(None)
        if ocloudmodel:
            self._compare_and_update(ocloudmodel)

    def _compare_and_update(self, ocloudmodel: StxGenericModel) -> bool:
        # localmodel = self._repo.get(ocloudmodel.id)
        oclouds = self._repo.list()
        if len(oclouds) > 1:
            raise InvalidOcloudState("More than 1 ocloud is found")
        if len(oclouds) == 0:
            self._repo.add(ocloudmodel)
        else:
            localmodel = oclouds.pop()
            if localmodel.is_outdated(ocloudmodel):
                localmodel.update_by(ocloudmodel)
                self._repo.update(localmodel)


class ResourcePoolWatcher(object):
    def __init__(self) -> None:
        super().__init__()


class ResourceWatcher(object):
    def __init__(self) -> None:
        super().__init__()
