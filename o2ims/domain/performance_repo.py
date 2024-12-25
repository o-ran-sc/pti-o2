# Copyright (C) 2024 Wind River Systems, Inc.
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
from o2ims.domain import performance_obj as obj


class MeasurementJobRepository(abc.ABC):
    def __init__(self):
        self.seen = set()  # type: Set[obj.MeasurementJob]

    def add(self, measurement_job: obj.MeasurementJob):
        self._add(measurement_job)
        self.seen.add(measurement_job)

    def get(self, measurement_job_id) -> obj.MeasurementJob:
        measurement_job = self._get(measurement_job_id)
        if measurement_job:
            self.seen.add(measurement_job)
        return measurement_job

    def list(self, *args) -> List[obj.MeasurementJob]:
        return self._list(*args)[1]

    def list_with_count(self, *args, **kwargs) -> \
            Tuple[int, List[obj.MeasurementJob]]:
        return self._list(*args, **kwargs)

    def update(self, measurement_job: obj.MeasurementJob):
        self._update(measurement_job)

    def delete(self, measurement_job_id):
        self._delete(measurement_job_id)

    @abc.abstractmethod
    def _add(self, measurement_job: obj.MeasurementJob):
        raise NotImplementedError

    @abc.abstractmethod
    def _get(self, measurement_job_id) -> obj.MeasurementJob:
        raise NotImplementedError

    @abc.abstractmethod
    def _list(self, **kwargs) -> Tuple[int, List[obj.MeasurementJob]]:
        raise NotImplementedError

    @abc.abstractmethod
    def _update(self, measurement_job: obj.MeasurementJob):
        raise NotImplementedError

    @abc.abstractmethod
    def _delete(self, measurement_job_id):
        raise NotImplementedError 