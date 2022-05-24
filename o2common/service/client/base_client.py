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
# from typing import Optional, List, Set
# from typing import List


class BaseClient(abc.ABC):
    def __init__(self):
        self._pool_id = None

    def list(self, **filters):
        return self._list(**filters)

    def get(self, id):
        return self._get(id)

    def set_pool_driver(self, pool_id):
        self._pool_id = pool_id
        self._set_stx_client()

    @abc.abstractmethod
    def _get(self, id):
        raise NotImplementedError

    @abc.abstractmethod
    def _list(self, **filters):
        raise NotImplementedError

    @abc.abstractmethod
    def _set_stx_client(self):
        raise NotImplementedError
