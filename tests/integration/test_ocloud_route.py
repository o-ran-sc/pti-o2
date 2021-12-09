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
import pytest

from o2common.config import config
from o2ims.domain import ocloud
from o2ims.domain import resource_type as rt


pytestmark = pytest.mark.usefixtures("mappers")


def setup_ocloud():
    ocloudid1 = str(uuid.uuid4())
    ocloud1 = ocloud.Ocloud(
        ocloudid1, "ocloud1", config.get_api_url(),
        "ocloud 1 for integration test", 1)
    return ocloud1


def test_route_olcouds(sqlite_flask_uow):
    uow, app = sqlite_flask_uow

    with uow:
        ocloud1 = setup_ocloud()
        ocloud1_UUID = ocloud1.oCloudId
        uow.oclouds.add(ocloud1)
        uow.commit()

    with app.test_client() as c:
        apibase = config.get_o2ims_api_base()
        resp = c.get(apibase+"/")
        assert resp.status_code == 200
        assert ocloud1_UUID.encode() in resp.data


def test_route_resource_types(sqlite_flask_uow):
    uow, app = sqlite_flask_uow

    with uow:
        ocloud1_id = str(uuid.uuid4())
        resource_type_id1 = str(uuid.uuid4())
        resource_type1 = ocloud.ResourceType(
            resource_type_id1, "resourcetype1", rt.ResourceTypeEnum.PSERVER,
            ocloud1_id)
        uow.resource_types.add(resource_type1)
        uow.commit()

    with app.test_client() as c:
        apibase = config.get_o2ims_api_base()
        resp = c.get(apibase+"/resourceTypes")
        assert resp.status_code == 200
        assert resource_type_id1.encode() in resp.data

        resp = c.get(apibase+'/resourceTypes/'+resource_type_id1)
        assert resp.status_code == 200
        json_data = resp.get_json()
        assert resource_type_id1 in json_data['resourceTypeId']


def test_route_resource_pools(sqlite_flask_uow):
    uow, app = sqlite_flask_uow

    with uow:
        ocloud1_id = str(uuid.uuid4())
        resource_pool_id1 = str(uuid.uuid4())
        resource_pool1 = ocloud.ResourcePool(
            resource_pool_id1, "resourcepool1", config.get_api_url(),
            ocloud1_id)
        uow.resource_pools.add(resource_pool1)
        uow.commit()

    with app.test_client() as c:
        apibase = config.get_o2ims_api_base()
        resp = c.get(apibase+"/resourcePools")
        assert resp.status_code == 200
        assert resource_pool_id1.encode() in resp.data

        resp = c.get(apibase+'/resourcePools/'+resource_pool_id1)
        assert resp.status_code == 200
        json_data = resp.get_json()
        assert resource_pool_id1 in json_data['resourcePoolId']


def test_route_resources(sqlite_flask_uow):
    uow, app = sqlite_flask_uow

    with uow:
        resource_id1 = str(uuid.uuid4())
        resource_type_id1 = str(uuid.uuid4())
        resource_pool_id1 = str(uuid.uuid4())
        resource1 = ocloud.Resource(
            resource_id1, resource_type_id1, resource_pool_id1, 'resource1')
        uow.resources.add(resource1)
        uow.commit()

    with app.test_client() as c:
        apibase = config.get_o2ims_api_base()
        resp = c.get(apibase+"/resourcePools/"+resource_pool_id1+"/resources")
        assert resp.status_code == 200
        assert resource_id1.encode() in resp.data

        resp = c.get(apibase+"/resourcePools/"+resource_pool_id1 +
                     "/resources/" + resource_id1)
        assert resp.status_code == 200
        json_data = resp.get_json()
        assert resource_pool_id1 in json_data['resourcePoolId']
        assert resource_type_id1 in json_data['resourceTypeId']
        assert resource_id1 in json_data['resourceId']


def test_route_deployment_managers(sqlite_flask_uow):
    uow, app = sqlite_flask_uow

    with uow:
        ocloud_id1 = str(uuid.uuid4())
        deployment_manager_id1 = str(uuid.uuid4())
        deployment_manager1 = ocloud.DeploymentManager(
            deployment_manager_id1, "k8s1", ocloud_id1,
            config.get_api_url()+"/k8s1")
        uow.deployment_managers.add(deployment_manager1)
        uow.commit()

    with app.test_client() as c:
        apibase = config.get_o2ims_api_base()
        resp = c.get(apibase+"/deploymentManagers")
        assert resp.status_code == 200
        assert deployment_manager_id1.encode() in resp.data

        resp = c.get(apibase+'/deploymentManagers/'+deployment_manager_id1)
        assert resp.status_code == 200
        json_data = resp.get_json()
        assert deployment_manager_id1 in json_data['deploymentManagerId']


def test_route_subscriptions(sqlite_flask_uow):
    _, app = sqlite_flask_uow

    with app.test_client() as c:
        apibase = config.get_o2ims_api_base()

        sub_callback = 'http://subscription/callback/url'
        resp = c.post(apibase+'/subscriptions', json={
            'callback': sub_callback,
            'consumerSubscriptionId': 'consumerSubId1',
            'filter': 'empty'
        })
        assert resp.status_code == 201
        json_data = resp.get_json()
        assert 'subscriptionId' in json_data
        subscriptionId1 = json_data['subscriptionId']

        resp = c.get(apibase+'/subscriptions')
        assert resp.status_code == 200
        json_data = resp.get_json()
        assert 1 == len(json_data)

        resp = c.get(apibase+'/subscriptions/'+subscriptionId1)
        assert resp.status_code == 200
        json_data = resp.get_json()
        assert sub_callback in json_data['callback']

        resp = c.delete(apibase+'/subscriptions/'+subscriptionId1)
        assert resp.status_code == 204

        resp = c.get(apibase+'/subscriptions')
        assert resp.status_code == 200
        json_data = resp.get_json()
        assert 0 == len(json_data)
