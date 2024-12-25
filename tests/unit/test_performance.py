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

import uuid
import pytest
from unittest.mock import MagicMock

from o2common.config import config

from o2ims.domain.resource_type import ResourceTypeEnum
from o2ims.domain import performance_obj as po
from o2ims.domain import commands
from o2ims.views import performance_view
from o2ims.service.watcher.alarm_watcher import AlarmWatcher


@pytest.fixture
def sample_measurement_job():
    return po.MeasurementJob(
        job_id=str(uuid.uuid4()),
        consumer_job_id=str(uuid.uuid4()),
        state=po.MeasurementJobState.ACTIVE,
        collection_interval=300,
        measurement_criteria=[{"metric": "cpu_usage"}],
        status=po.MeasurementJobStatus.RUNNING,
        preinstalled_job=False,
        resource_criteria={"resourceType": "compute_node"}
    )


def test_view_measurement_jobs(mock_uow, sample_measurement_job):
    session, uow = mock_uow

    # Mock the response for the measurement jobs
    measurement_job1 = MagicMock()
    measurement_job1.serialize.return_value = sample_measurement_job

    order_by = MagicMock()
    order_by.count.return_value = 1
    order_by.limit.return_value.offset.return_value = [measurement_job1]
    session.return_value.query.return_value.filter.return_value.\
        order_by.return_value = order_by

    # Call the view function
    result = performance_view.measurement_jobs(uow)

    assert result['count'] == 1
    ret_list = result['results']
    assert str(ret_list[0].performanceMeasurementJobId) == \
        sample_measurement_job.performanceMeasurementJobId


def test_view_measurement_job_one(mock_uow, sample_measurement_job):
    session, uow = mock_uow
    # Mock None response for a single measurement job
    session.return_value.query.return_value.filter_by.return_value.first.\
        return_value.serialize.return_value = None

    # Query return None
    result = performance_view.measurement_job_one(
        sample_measurement_job.performanceMeasurementJobId, uow)
    assert result is None

    # Mock the response for a single measurement job
    session.return_value.query.return_value.filter_by.return_value.first.\
        return_value.serialize.return_value = sample_measurement_job

    # Call the view function
    result = performance_view.measurement_job_one(
        sample_measurement_job.performanceMeasurementJobId, uow)

    assert str(result.performanceMeasurementJobId) == \
        sample_measurement_job.performanceMeasurementJobId


def test_flask_get_list(mock_flask_uow):
    session, app = mock_flask_uow
    order_by = MagicMock()
    order_by.count.return_value = 0
    order_by.limit.return_value.offset.return_value = []
    session.return_value.query.return_value.filter.return_value.\
        order_by.return_value = order_by
    apibase = config.get_o2ims_performance_api_base() + '/v1'

    with app.test_client() as client:
        # Get list and return empty list
        ##########################
        resp = client.get(apibase+"/measurementJobs")
        assert resp.get_data() == b'[]\n'


def test_flask_get_one(mock_flask_uow, sample_measurement_job):
    session, app = mock_flask_uow

    session.return_value.query.return_value.filter_by.return_value.\
        first.return_value = sample_measurement_job
    apibase = config.get_o2ims_performance_api_base() + '/v1'

    with app.test_client() as client:
        # Get one and return 200
        ###########################
        resp = client.get(apibase+"/measurementJobs/" +
                          sample_measurement_job.performanceMeasurementJobId)
        assert resp.status_code == 200
        assert resp.json['performanceMeasurementJobId'] == \
            sample_measurement_job.performanceMeasurementJobId


def test_flask_get_one_not_found(mock_flask_uow):
    session, app = mock_flask_uow

    session.return_value.query.return_value.filter_by.return_value.\
        first.return_value = None
    apibase = config.get_o2ims_performance_api_base() + '/v1'

    with app.test_client() as client:
        # Get one and return 404
        ###########################
        measurement_job_id1 = str(uuid.uuid4())
        resp = client.get(apibase+"/measurementJobs/"+measurement_job_id1)
        assert resp.status_code == 404


def test_flask_not_allowed_methods(mock_flask_uow):
    _, app = mock_flask_uow
    apibase = config.get_o2ims_performance_api_base() + '/v1'

    with app.test_client() as client:
        # Testing measurement jobs not support method
        ##########################
        uri = apibase + "/measurementJobs"
        resp = client.post(uri)
        assert resp.status == '405 METHOD NOT ALLOWED'
        resp = client.put(uri)
        assert resp.status == '405 METHOD NOT ALLOWED'
        resp = client.patch(uri)
        assert resp.status == '405 METHOD NOT ALLOWED'
        resp = client.delete(uri)
        assert resp.status == '405 METHOD NOT ALLOWED'