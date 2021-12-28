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
from o2ims.domain import configuration_obj as obj


class ConfigurationRepository(abc.ABC):
    def __init__(self):
        self.seen = set()  # type: Set[obj.Configuration]

    def add(self, configuration: obj.Configuration):
        self._add(configuration)
        self.seen.add(configuration)

    def get(self, configuration_id) -> obj.Configuration:
        configuration = self._get(configuration_id)
        if configuration:
            self.seen.add(configuration)
        return configuration

    def list(self) -> List[obj.Configuration]:
        return self._list()

    def update(self, configuration: obj.Configuration):
        self._update(configuration)

    def delete(self, configuration_id):
        self._delete(configuration_id)

    @abc.abstractmethod
    def _add(self, configuration: obj.Configuration):
        raise NotImplementedError

    @abc.abstractmethod
    def _get(self, configuration_id) -> obj.Configuration:
        raise NotImplementedError

    @abc.abstractmethod
    def _update(self, configuration: obj.Configuration):
        raise NotImplementedError

    @abc.abstractmethod
    def _delete(self, configuration_id):
        raise NotImplementedError
