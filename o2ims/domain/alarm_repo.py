# Copyright (C) 2022 Wind River Systems, Inc.
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
from o2ims.domain import alarm_obj as obj


class AlarmEventRecordRepository(abc.ABC):
    def __init__(self):
        self.seen = set()  # type: Set[obj.AlarmEventRecord]

    def add(self, alarm_event_record: obj.AlarmEventRecord):
        self._add(alarm_event_record)
        self.seen.add(alarm_event_record)

    def get(self, alarm_event_record_id) -> obj.AlarmEventRecord:
        alarm_event_record = self._get(alarm_event_record_id)
        if alarm_event_record:
            self.seen.add(alarm_event_record)
        return alarm_event_record

    def list(self, *args) -> List[obj.AlarmEventRecord]:
        return self._list(*args)[1]

    def list_with_count(self, *args, **kwargs) -> \
            Tuple[int, List[obj.AlarmEventRecord]]:
        return self._list(*args, **kwargs)

    def update(self, alarm_event_record: obj.AlarmEventRecord):
        self._update(alarm_event_record)

    def delete(self, alarm_event_record_id):
        self._delete(alarm_event_record_id)

    @abc.abstractmethod
    def _add(self, alarm_event_record: obj.AlarmEventRecord):
        raise NotImplementedError

    @abc.abstractmethod
    def _get(self, alarm_event_record_id) -> obj.AlarmEventRecord:
        raise NotImplementedError

    @abc.abstractmethod
    def _list(self, **kwargs) -> Tuple[int, List[obj.AlarmEventRecord]]:
        raise NotImplementedError

    @abc.abstractmethod
    def _update(self, alarm_event_record: obj.AlarmEventRecord):
        raise NotImplementedError

    @abc.abstractmethod
    def _delete(self, alarm_event_record_id):
        raise NotImplementedError


class AlarmDefinitionRepository(abc.ABC):
    def __init__(self):
        self.seen = set()  # type: Set[obj.AlarmDefinition]

    def add(self, definition: obj.AlarmDefinition):
        self._add(definition)
        self.seen.add(definition)

    def get(self, definition_id) -> obj.AlarmDefinition:
        definition = self._get(definition_id)
        if definition:
            self.seen.add(definition)
        return definition

    def list(self) -> List[obj.AlarmDefinition]:
        return self._list()

    def update(self, definition: obj.AlarmDefinition):
        self._update(definition)

    def delete(self, definition_id):
        self._delete(definition_id)

    @abc.abstractmethod
    def _add(self, definition: obj.AlarmDefinition):
        raise NotImplementedError

    @abc.abstractmethod
    def _get(self, definition_id) -> obj.AlarmDefinition:
        raise NotImplementedError

    @abc.abstractmethod
    def _list(self, **kwargs) -> List[obj.AlarmDefinition]:
        raise NotImplementedError

    @abc.abstractmethod
    def _update(self, definition: obj.AlarmDefinition):
        raise NotImplementedError

    @abc.abstractmethod
    def _delete(self, definition_id):
        raise NotImplementedError


class AlarmDictionaryRepository(abc.ABC):
    def __init__(self):
        self.seen = set()  # type: Set[obj.AlarmDictionary]

    def add(self, dictionary: obj.AlarmDictionary):
        self._add(dictionary)
        self.seen.add(dictionary)

    def get(self, dictionary_id) -> obj.AlarmDictionary:
        dictionary = self._get(dictionary_id)
        if dictionary:
            self.seen.add(dictionary)
        return dictionary

    def list(self) -> List[obj.AlarmDictionary]:
        return self._list()

    def update(self, dictionary: obj.AlarmDictionary):
        self._update(dictionary)

    def delete(self, dictionary_id):
        self._delete(dictionary_id)

    @abc.abstractmethod
    def _add(self, dictionary: obj.AlarmDictionary):
        raise NotImplementedError

    @abc.abstractmethod
    def _get(self, dictionary_id) -> obj.AlarmDictionary:
        raise NotImplementedError

    @abc.abstractmethod
    def _list(self, **kwargs) -> List[obj.AlarmDictionary]:
        raise NotImplementedError

    @abc.abstractmethod
    def _delete(self, dictionary_id):
        raise NotImplementedError


class AlarmSubscriptionRepository(abc.ABC):
    def __init__(self):
        self.seen = set()  # type: Set[obj.AlarmSubscription]

    def add(self, subscription: obj.AlarmSubscription):
        self._add(subscription)
        self.seen.add(subscription)

    def get(self, subscription_id) -> obj.AlarmSubscription:
        subscription = self._get(subscription_id)
        if subscription:
            self.seen.add(subscription)
        return subscription

    def list(self, *args) -> List[obj.AlarmSubscription]:
        return self._list(*args)[1]

    def list_with_count(self, *args, **kwargs) -> \
            Tuple[int, List[obj.AlarmSubscription]]:
        return self._list(*args, **kwargs)

    def update(self, subscription: obj.AlarmSubscription):
        self._update(subscription)

    def delete(self, subscription_id):
        self._delete(subscription_id)

    @abc.abstractmethod
    def _add(self, subscription: obj.AlarmSubscription):
        raise NotImplementedError

    @abc.abstractmethod
    def _get(self, subscription_id) -> obj.AlarmSubscription:
        raise NotImplementedError

    @abc.abstractmethod
    def _list(self, **kwargs) -> Tuple[int, List[obj.AlarmSubscription]]:
        raise NotImplementedError

    @abc.abstractmethod
    def _update(self, subscription: obj.AlarmSubscription):
        raise NotImplementedError

    @abc.abstractmethod
    def _delete(self, subscription_id):
        raise NotImplementedError


class AlarmProbableCauseRepository(abc.ABC):
    def __init__(self):
        self.seen = set()  # type: Set[obj.ProbableCause]

    def add(self, probable_cause: obj.ProbableCause):
        self._add(probable_cause)
        self.seen.add(probable_cause)

    def get(self, probable_cause_id) -> obj.ProbableCause:
        probable_cause = self._get(probable_cause_id)
        if probable_cause:
            self.seen.add(probable_cause)
        return probable_cause

    def list(self) -> List[obj.ProbableCause]:
        return self._list()

    def update(self, probable_cause: obj.ProbableCause):
        self._update(probable_cause)

    def delete(self, probable_cause_id):
        self._delete(probable_cause_id)

    @abc.abstractmethod
    def _add(self, probable_cause: obj.ProbableCause):
        raise NotImplementedError

    @abc.abstractmethod
    def _get(self, probable_cause_id) -> obj.ProbableCause:
        raise NotImplementedError

    @abc.abstractmethod
    def _list(self, **kwargs) -> List[obj.ProbableCause]:
        raise NotImplementedError

    @abc.abstractmethod
    def _update(self, probable_cause: obj.ProbableCause):
        raise NotImplementedError

    @abc.abstractmethod
    def _delete(self, probable_cause_id):
        raise NotImplementedError


class AlarmServiceConfigurationRepository(abc.ABC):
    def __init__(self):
        self.seen = set()  # type: Set[obj.AlarmServiceConfiguration]

    def get(self) -> obj.AlarmServiceConfiguration:
        service_config = self._get()
        if service_config:
            self.seen.add(service_config)
        else:
            service_config = self._add_default()
        return service_config

    def update(self, service_config: obj.AlarmServiceConfiguration):
        self._update(service_config)

    @abc.abstractmethod
    def _add_default(self) -> obj.AlarmServiceConfiguration:
        raise NotImplementedError

    @abc.abstractmethod
    def _get(self) -> obj.AlarmServiceConfiguration:
        raise NotImplementedError

    @abc.abstractmethod
    def _update(self, service_config: obj.AlarmServiceConfiguration):
        raise NotImplementedError
