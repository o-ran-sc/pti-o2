# Copyright (C) 2024-2025 Wind River Systems, Inc.
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
from typing import List, Tuple

from o2ims.domain import performance_obj
from o2ims.domain.performance_repo import MeasurementJobRepository
from o2common.helper import o2logging
logger = o2logging.get_logger(__name__)


class MeasurementJobSqlAlchemyRepository(MeasurementJobRepository):
    def __init__(self, session):
        super().__init__()
        self.session = session

    def _add(self, measurement_job: performance_obj.MeasurementJob):
        self.session.add(measurement_job)

    def _get(self, measurement_job_id) -> performance_obj.MeasurementJob:
        return self.session.query(performance_obj.MeasurementJob).filter_by(
            performanceMeasurementJobId=measurement_job_id).first()

    def _list(self, *args, **kwargs) -> Tuple[
            int, List[performance_obj.MeasurementJob]]:
        size = kwargs.pop('limit') if 'limit' in kwargs else None
        offset = kwargs.pop('start') if 'start' in kwargs else 0

        result = self.session.query(performance_obj.MeasurementJob).filter(
            *args).order_by('performanceMeasurementJobId')
        count = result.count()
        if size is not None and size != -1:
            return (count, result.limit(size).offset(offset))
        return (count, result)

    def _update(self, measurement_job: performance_obj.MeasurementJob):
        self.session.merge(measurement_job)

    def _delete(self, measurement_job_id):
        self.session.query(performance_obj.MeasurementJob).filter_by(
            performanceMeasurementJobId=measurement_job_id).delete()
