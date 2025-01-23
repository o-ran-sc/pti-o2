# Copyright (C) 2025 Wind River Systems, Inc.
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

import pytest
from elasticsearch import Elasticsearch

from o2common.config import config
from o2ims.adapter.clients.pm_client import StxPmClientImp
from o2ims.domain import performance_obj as pm_obj


@pytest.fixture
def real_es_client():
    es_config = config.get_es_access_info()
    es_client = Elasticsearch(
        es_config['url'],
        basic_auth=(es_config['username'], es_config['password']),
        verify_certs=False
    )
    yield es_client


@pytest.fixture
def real_pm_client(real_es_client):
    pm_client = StxPmClientImp(real_es_client)
    yield pm_client


def test_get_es_client():
    pm_client = StxPmClientImp()
    assert pm_client.es_client is not None
    assert pm_client.es_client.ping()


def test_get_pm_list(real_pm_client):
    # Test getting PM list without filters
    pm_list = real_pm_client.getPmList()
    assert pm_list is not None
    if len(pm_list) > 0:
        assert isinstance(pm_list[0], pm_obj.PmGenericModel)
        assert pm_list[0].id is not None
        assert pm_list[0].host_name is not None


def test_get_pm_list_with_host_filter(real_pm_client):
    # Test getting PM list with host filter
    pm_list = real_pm_client.getPmList(host_name="controller-0")
    assert pm_list is not None
    if len(pm_list) > 0:
        assert isinstance(pm_list[0], pm_obj.PmGenericModel)
        assert pm_list[0].host_name == "controller-0"


def test_get_pm_list_with_size_filter(real_pm_client):
    # Test getting PM list with size filter
    size = 5
    pm_list = real_pm_client.getPmList(size=size)
    assert pm_list is not None
    assert len(pm_list) <= size


def test_get_pm_info(real_pm_client):
    # First get a list to get a valid ID
    pm_list = real_pm_client.getPmList()
    if len(pm_list) > 0:
        pm_id = pm_list[0].id
        pm_info = real_pm_client.getPmInfo(pm_id)
        assert pm_info is not None
        assert isinstance(pm_info, pm_obj.PmGenericModel)
        assert pm_info.id == pm_id


def test_build_query():
    # Test query building with different filter combinations
    filters = {
        'host_name': 'controller-0',
        'size': 5
    }
    query = StxPmClientImp._build_query(**filters)

    # Verify query structure
    assert query['size'] == 0
    assert 'query' in query
    assert 'bool' in query['query']
    assert 'must' in query['query']['bool']

    # Verify must conditions
    must_conditions = query['query']['bool']['must']
    assert {'term': {'type': 'beats'}} in must_conditions
    assert {'term': {'service.type': 'system'}} in must_conditions
    assert {'term': {'host.name': 'controller-0'}} in must_conditions

    # Verify aggregations
    assert 'aggs' in query
    assert 'unique_datasets' in query['aggs']
    assert query['aggs']['unique_datasets']['terms']['size'] == 5


def test_convert_to_pm_model():
    # Test PM model conversion
    es_hit = {
        '_id': 'test_id',
        '_source': {
            'host': {'name': 'test_host'},
            'event': {'module': 'test_module'},
            'raw_data': {'test': 'data'}
        }
    }

    pm_model = StxPmClientImp._convert_to_pm_model(es_hit)
    assert isinstance(pm_model, pm_obj.PmGenericModel)
    assert pm_model.id == 'test_id'
    assert pm_model.host_name == 'test_host'
    assert pm_model.event_module == 'test_module'
    assert pm_model.raw_data == es_hit['_source']


def test_set_pm_client(real_pm_client):
    # Test setting PM client for different resource pools
    resource_pool_id = 'test_pool'
    real_pm_client.setPmClient(resource_pool_id)
    # Since setPmClient is a placeholder, just verify
    # it doesn't raise an exception
    assert True
