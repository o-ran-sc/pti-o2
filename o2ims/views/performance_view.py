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

from o2common.service import unit_of_work
from o2common.views.view import gen_filter
from o2common.views.pagination_view import Pagination
from o2ims.domain.performance_obj import MeasurementJob

from o2common.helper import o2logging
logger = o2logging.get_logger(__name__)


def measurement_jobs(uow: unit_of_work.AbstractUnitOfWork, **kwargs):
    """Get list of measurement jobs with pagination support"""
    pagination = Pagination(**kwargs)
    query_kwargs = pagination.get_pagination()
    args = gen_filter(MeasurementJob,
                      kwargs['filter']) if 'filter' in kwargs else []

    with uow:
        li = uow.measurement_jobs.list_with_count(*args, **query_kwargs)
    return pagination.get_result(li)


def measurement_job_one(measurementJobId: str,
                        uow: unit_of_work.AbstractUnitOfWork):
    """Get a single measurement job by ID"""
    with uow:
        first = uow.measurement_jobs.get(measurementJobId)
        return first.serialize() if first is not None else None
