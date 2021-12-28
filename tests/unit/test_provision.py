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

import uuid
from unittest.mock import MagicMock

from o2ims.domain import configuration_obj
from o2ims.views import provision_view
from o2common.config import config


def test_new_smo_endpoint():
    configuration_id1 = str(uuid.uuid4())
    configuration1 = configuration_obj.Configuration(
        configuration_id1, "https://callback/uri/write/here",
        "SMO")
    assert configuration_id1 is not None and\
        configuration1.configurationId == configuration_id1


def test_view_smo_endpoint(mock_uow):
    session, uow = mock_uow

    configuration_id1 = str(uuid.uuid4())
    conf1 = MagicMock()
    conf1.serialize_smo.return_value = {
        "configurationId": configuration_id1,
    }
    session.return_value.query.return_value = [conf1]

    configuration_list = provision_view.configurations(uow)
    assert str(configuration_list[0].get(
        "configurationId")) == configuration_id1


def test_view_smo_endpoint_one(mock_uow):
    session, uow = mock_uow

    configuration_id1 = str(uuid.uuid4())
    session.return_value.query.return_value.filter_by.return_value.first.\
        return_value.serialize_smo.return_value = None

    # Query return None
    configuration_res = provision_view.configuration_one(
        configuration_id1, uow)
    assert configuration_res is None

    session.return_value.query.return_value.filter_by.return_value.first.\
        return_value.serialize_smo.return_value = {
            "configurationId": configuration_id1,
        }

    configuration_res = provision_view.configuration_one(
        configuration_id1, uow)
    assert str(configuration_res.get(
        "configurationId")) == configuration_id1


def test_flask_get_list(mock_flask_uow):
    session, app = mock_flask_uow
    session.query.return_value = []
    apibase = config.get_provision_api_base()

    with app.test_client() as client:
        # Get list and return empty list
        ##########################
        resp = client.get(apibase+"/smo-endpoint")
        assert resp.get_data() == b'[]\n'


def test_flask_get_one(mock_flask_uow):
    session, app = mock_flask_uow

    session.return_value.query.return_value.filter_by.return_value.\
        first.return_value = None
    apibase = config.get_provision_api_base()

    with app.test_client() as client:
        # Get one and return 404
        ###########################
        configuration_id1 = str(uuid.uuid4())
        resp = client.get(apibase+"/smo-endpoint/"+configuration_id1)
        assert resp.status_code == 404


def test_flask_post(mock_flask_uow):
    session, app = mock_flask_uow
    apibase = config.get_provision_api_base()

    with app.test_client() as client:
        session.return_value.execute.return_value = []

        conf_callback = 'http://registration/callback/url'
        resp = client.post(apibase+'/smo-endpoint', json={
            'endpoint': conf_callback
        })
        assert resp.status_code == 201
        assert 'configurationId' in resp.get_json()


def test_flask_delete(mock_flask_uow):
    session, app = mock_flask_uow
    apibase = config.get_provision_api_base()

    with app.test_client() as client:
        session.return_value.execute.return_value.first.return_value = {}

        configuration_id1 = str(uuid.uuid4())
        resp = client.delete(apibase+"/smo-endpoint/"+configuration_id1)
        assert resp.status_code == 204


def test_flask_not_allowed(mock_flask_uow):
    _, app = mock_flask_uow
    apibase = config.get_provision_api_base()

    with app.test_client() as client:

        # Testing SMO endpoint not support method
        ##########################
        uri = apibase + "/smo-endpoint"
        resp = client.put(uri)
        assert resp.status == '405 METHOD NOT ALLOWED'
        resp = client.patch(uri)
        assert resp.status == '405 METHOD NOT ALLOWED'
        resp = client.delete(uri)
        assert resp.status == '405 METHOD NOT ALLOWED'

        configuration_id1 = str(uuid.uuid4())
        uri = apibase + "/smo-endpoint/" + configuration_id1
        resp = client.post(uri)
        assert resp.status == '405 METHOD NOT ALLOWED'
        resp = client.put(uri)
        assert resp.status == '405 METHOD NOT ALLOWED'
        resp = client.patch(uri)
        assert resp.status == '405 METHOD NOT ALLOWED'
