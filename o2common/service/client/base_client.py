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
        pass

    def list(self, **filters):
        return self._list(**filters)

    def get(self, id):
        return self._get(id)

    @abc.abstractmethod
    def _get(self, id):
        raise NotImplementedError

    @abc.abstractmethod
    def _list(self, **filters):
        raise NotImplementedError
