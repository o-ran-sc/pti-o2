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

from __future__ import annotations
from enum import Enum
from typing import List, Dict
import json
from o2common.domain.base import AgRoot, Serializer


class MeasurementJobState(str, Enum):
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    DEPRECATED = "DEPRECATED"


class MeasurementJobStatus(str, Enum):
    RUNNING = "RUNNING"
    FAILED = "FAILED"
    DEGRADED = "DEGRADED"
    IDLE = "IDLE"
    PENDING_DELETE = "PENDING_DELETE"


class MeasuredResource(AgRoot, Serializer):
    def __init__(self, resource_id: str, resource_type_id: str,
                 time_added: List[str] = None,
                 time_deleted: List[str] = None,
                 is_currently_measured: bool = False) -> None:
        super().__init__()
        self.resourceId = resource_id
        self.resourceTypeId = resource_type_id
        self.timeAdded = time_added or []  # List of timestamps
        self.timeDeleted = time_deleted or []  # List of timestamps
        self.isCurrentlyMeasured = is_currently_measured  # Boolean, ReadOnly


class CollectedMeasurement(AgRoot, Serializer):
    def __init__(self, measurement_id: str, resource_type_id: str,
                 performance_measurement_definition_id: str,
                 time_added: List[str],
                 time_deleted: List[str] = None,
                 is_currently_measured: bool = False) -> None:
        super().__init__()
        self.measurementId = measurement_id
        self.resourceTypeId = resource_type_id  # ReadOnly, UUID format
        self.performanceMeasurementDefinitionId = \
            performance_measurement_definition_id  # ReadOnly, UUID format
        self.timeAdded = time_added  # List of timestamps
        self.timeDeleted = time_deleted or []  # List of timestamps
        self.isCurrentlyMeasured = is_currently_measured  # Boolean, ReadOnly


class MeasurementJob(AgRoot, Serializer):
    def __init__(
        self,
        job_id: str,
        consumer_job_id: str,
        state: MeasurementJobState,
        collection_interval: int,
        measurement_criteria: List[Dict[str, str]],
        status: MeasurementJobStatus,
        preinstalled_job: bool,
        resource_criteria: Dict[str, str] = None,
    ) -> None:
        super().__init__()
        self.performanceMeasurementJobId = job_id
        self.consumerPerformanceJobId = consumer_job_id
        self.state = state
        self.collectionInterval = collection_interval
        self._resourceScopeCriteria = json.dumps(resource_criteria) if resource_criteria else '{}'  # noqa: E501
        self._measurementSelectionCriteria = json.dumps(measurement_criteria) if measurement_criteria else '[]'  # noqa: E501
        self.status = status
        self.preinstalledJob = preinstalled_job
        self._qualifiedResourceTypes = '[]'
        self.measuredResources: List[MeasuredResource] = []
        self.collectedMeasurements: List[CollectedMeasurement] = []
        self.extensions = ''

    @property
    def resourceScopeCriteria(self) -> Dict:
        return json.loads(self._resourceScopeCriteria)

    @resourceScopeCriteria.setter
    def resourceScopeCriteria(self, value: Dict):
        self._resourceScopeCriteria = json.dumps(value) if value else '{}'

    @property
    def measurementSelectionCriteria(self) -> List:
        return json.loads(self._measurementSelectionCriteria)

    @measurementSelectionCriteria.setter
    def measurementSelectionCriteria(self, value: List):
        self._measurementSelectionCriteria = \
            json.dumps(value) if value else '[]'

    @property
    def qualifiedResourceTypes(self) -> List:
        return json.loads(self._qualifiedResourceTypes)

    @qualifiedResourceTypes.setter
    def qualifiedResourceTypes(self, value: List):
        self._qualifiedResourceTypes = json.dumps(value) if value else '[]'

    def __composite_values__(self):
        return [
            self.performanceMeasurementJobId,
            self.consumerPerformanceJobId,
            self.state,
            self.collectionInterval,
            self._resourceScopeCriteria,
            self._measurementSelectionCriteria,
            self.status,
            self.preinstalledJob,
            self._qualifiedResourceTypes,
            self.extensions
        ]
