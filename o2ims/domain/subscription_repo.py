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
from typing import List, Set, Tuple
from o2ims.domain import subscription_obj as subobj


class SubscriptionRepository(abc.ABC):
    def __init__(self):
        self.seen = set()  # type: Set[subobj.Subscription]

    def add(self, subscription: subobj.Subscription):
        self._add(subscription)
        self.seen.add(subscription)

    def get(self, subscription_id) -> subobj.Subscription:
        subscription = self._get(subscription_id)
        if subscription:
            self.seen.add(subscription)
        return subscription

    def list(self, **kwargs) -> List[subobj.Subscription]:
        return self._list(*[], **kwargs)[1]

    def list_with_count(self, *args, **kwargs) -> \
            Tuple[int, List[subobj.Subscription]]:
        return self._list(*args, **kwargs)

    def update(self, subscription: subobj.Subscription):
        self._update(subscription)

    def delete(self, subscription_id):
        self._delete(subscription_id)

    @abc.abstractmethod
    def _add(self, subscription: subobj.Subscription):
        raise NotImplementedError

    @abc.abstractmethod
    def _get(self, subscription_id) -> subobj.Subscription:
        raise NotImplementedError

    @abc.abstractmethod
    def _update(self, subscription: subobj.Subscription):
        raise NotImplementedError

    @abc.abstractmethod
    def _list(self, **kwargs) -> Tuple[int, List[subobj.Subscription]]:
        raise NotImplementedError

    @abc.abstractmethod
    def _delete(self, subscription_id):
        raise NotImplementedError
