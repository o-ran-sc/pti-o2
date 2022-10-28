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

from o2ims.domain import ocloud, subscription_obj
from o2ims.domain import resource_type as rt
from o2ims.views import ocloud_view
from o2common.config import config


def setup_ocloud():
    ocloudid1 = str(uuid.uuid4())
    ocloud1 = ocloud.Ocloud(ocloudid1, "ocloud1",
                            config.get_api_url(), "ocloud for unit test", 1)
    return ocloud1


def test_new_ocloud():
    ocloudid1 = str(uuid.uuid4())
    ocloud1 = ocloud.Ocloud(ocloudid1, "ocloud1",
                            config.get_api_url(), "ocloud for unit test", 1)
    assert ocloudid1 is not None and ocloud1.oCloudId == ocloudid1


# def test_add_ocloud_with_dms():
#     ocloud1 = setup_ocloud()
#     dmsid = str(uuid.uuid4())
#     dms = ocloud.DeploymentManager(
#         dmsid, "k8s1", ocloud1.oCloudId, config.get_api_url()+"/k8s1")
#     ocloud1.addDeploymentManager(dms)
#     ocloud1.addDeploymentManager(dms)
#     assert len(ocloud1.deploymentManagers) == 1
#     # repo.update(ocloud1.oCloudId, {
#     #             "deploymentManagers": ocloud1.deploymentManagers})


def test_new_resource_type():
    ocloud1 = setup_ocloud()
    resource_type_id1 = str(uuid.uuid4())
    resource_type1 = ocloud.ResourceType(
        resource_type_id1, "resourcetype1", rt.ResourceTypeEnum.PSERVER,
        ocloud1.oCloudId)
    assert resource_type_id1 is not None and \
        resource_type1.resourceTypeId == resource_type_id1


def test_new_resource_pool():
    ocloud1 = setup_ocloud()
    resource_pool_id1 = str(uuid.uuid4())
    resource_pool1 = ocloud.ResourcePool(
        resource_pool_id1, "resourcepool1", config.get_api_url(),
        ocloud1.oCloudId)
    assert resource_pool_id1 is not None and \
        resource_pool1.resourcePoolId == resource_pool_id1


def test_new_resource():
    resource_id1 = str(uuid.uuid4())
    resource_type_id1 = str(uuid.uuid4())
    resource_pool_id1 = str(uuid.uuid4())
    resource1 = ocloud.Resource(
        resource_id1, resource_type_id1, resource_pool_id1, 'resource1')
    assert resource_id1 is not None and resource1.resourceId == resource_id1


def test_new_deployment_manager():
    ocloud_id1 = str(uuid.uuid4())
    deployment_manager_id1 = str(uuid.uuid4())
    deployment_manager1 = ocloud.DeploymentManager(
        deployment_manager_id1, "k8s1", ocloud_id1,
        config.get_api_url()+"/k8s1")
    assert deployment_manager_id1 is not None and deployment_manager1.\
        deploymentManagerId == deployment_manager_id1


def test_new_subscription():
    subscription_id1 = str(uuid.uuid4())
    subscription1 = subscription_obj.Subscription(
        subscription_id1, "https://callback/uri/write/here")
    assert subscription_id1 is not None and\
        subscription1.subscriptionId == subscription_id1


def test_view_olcouds(mock_uow):
    session, uow = mock_uow

    ocloud1_UUID = str(uuid.uuid4)
    ocloud1 = MagicMock()
    ocloud1.serialize.return_value = {
        'oCloudId': ocloud1_UUID, 'name': 'ocloud1'}
    session.return_value.query.return_value = [ocloud1]

    ocloud_list = ocloud_view.oclouds(uow)
    # assert str(ocloud_list[0].get("oCloudId")) == ocloud1_UUID
    assert len(ocloud_list) == 1


def test_view_olcoud_one(mock_uow):
    session, uow = mock_uow

    ocloud1_UUID = str(uuid.uuid4)
    session.return_value.query.return_value.filter_by.return_value.first.\
        return_value.serialize.return_value = None

    # Query return None
    ocloud_res = ocloud_view.ocloud_one(ocloud1_UUID, uow)
    assert ocloud_res is None

    session.return_value.query.return_value.filter_by.return_value.first.\
        return_value.serialize.return_value = {
            "oCloudId": ocloud1_UUID}

    ocloud_res = ocloud_view.ocloud_one(ocloud1_UUID, uow)
    assert str(ocloud_res.get("oCloudId")) == ocloud1_UUID


def test_view_resource_types(mock_uow):
    session, uow = mock_uow

    resource_type_id1 = str(uuid.uuid4())
    restype1 = MagicMock()
    restype1.serialize.return_value = {
        "resourceTypeId": resource_type_id1}

    order_by = MagicMock()
    order_by.count.return_value = 1
    order_by.limit.return_value.offset.return_value = [restype1]
    session.return_value.query.return_value.filter.return_value.\
        order_by.return_value = order_by

    result = ocloud_view.resource_types(uow)
    assert result['count'] == 1
    ret_list = result['results']
    assert str(ret_list[0].get("resourceTypeId")) == resource_type_id1


def test_view_resource_type_one(mock_uow):
    session, uow = mock_uow

    resource_type_id1 = str(uuid.uuid4())
    session.return_value.query.return_value.filter_by.return_value.first.\
        return_value.serialize.return_value = None

    # Query return None
    resource_type_res = ocloud_view.resource_type_one(
        resource_type_id1, uow)
    assert resource_type_res is None

    session.return_value.query.return_value.filter_by.return_value.first.\
        return_value.serialize.return_value = {
            "resourceTypeId": resource_type_id1}

    resource_type_res = ocloud_view.resource_type_one(resource_type_id1, uow)
    assert str(resource_type_res.get("resourceTypeId")) == resource_type_id1


def test_view_resource_pools(mock_uow):
    session, uow = mock_uow

    resource_pool_id1 = str(uuid.uuid4())
    respool1 = MagicMock()
    respool1.serialize.return_value = {
        "resourcePoolId": resource_pool_id1}

    order_by = MagicMock()
    order_by.count.return_value = 1
    order_by.limit.return_value.offset.return_value = [respool1]
    session.return_value.query.return_value.filter.return_value.\
        order_by.return_value = order_by

    result = ocloud_view.resource_pools(uow)
    assert result['count'] == 1
    ret_list = result['results']
    assert str(ret_list[0].get("resourcePoolId")) == resource_pool_id1


def test_view_resource_pool_one(mock_uow):
    session, uow = mock_uow

    resource_pool_id1 = str(uuid.uuid4())
    session.return_value.query.return_value.filter_by.return_value.first.\
        return_value.serialize.return_value = None

    # Query return None
    resource_pool_res = ocloud_view.resource_pool_one(
        resource_pool_id1, uow)
    assert resource_pool_res is None

    session.return_value.query.return_value.filter_by.return_value.first.\
        return_value.serialize.return_value = {
            "resourcePoolId": resource_pool_id1
        }

    resource_pool_res = ocloud_view.resource_pool_one(resource_pool_id1, uow)
    assert str(resource_pool_res.get("resourcePoolId")) == resource_pool_id1


def test_view_resources(mock_uow):
    session, uow = mock_uow

    resource_id1 = str(uuid.uuid4())
    resource_pool_id1 = str(uuid.uuid4())
    res1 = MagicMock()
    res1.serialize.return_value = {
        "resourceId": resource_id1,
        "resourcePoolId": resource_pool_id1
    }

    order_by = MagicMock()
    order_by.count.return_value = 1
    order_by.limit.return_value.offset.return_value = [res1]
    session.return_value.query.return_value.filter.return_value.\
        order_by.return_value = order_by
    # TODO: workaround for sqlalchemy not mapping with resource object
    setattr(ocloud.Resource, 'resourcePoolId', '')

    result = ocloud_view.resources(resource_pool_id1, uow)
    assert result['count'] == 1
    resource_list = result['results']
    assert str(resource_list[0].get("resourceId")) == resource_id1
    assert str(resource_list[0].get("resourcePoolId")) == resource_pool_id1


def test_view_resource_one(mock_uow):
    session, uow = mock_uow

    resource_id1 = str(uuid.uuid4())
    resource_pool_id1 = str(uuid.uuid4())
    session.return_value.query.return_value.filter_by.return_value.first.\
        return_value.serialize.return_value = None

    # Query return None
    resource_res = ocloud_view.resource_one(resource_id1, uow)
    assert resource_res is None

    session.return_value.query.return_value.filter_by.return_value.first.\
        return_value.serialize.return_value = {
            "resourceId": resource_id1,
            "resourcePoolId": resource_pool_id1
        }

    resource_res = ocloud_view.resource_one(resource_id1, uow)
    assert str(resource_res.get("resourceId")) == resource_id1


def test_view_deployment_managers(mock_uow):
    session, uow = mock_uow

    deployment_manager_id1 = str(uuid.uuid4())
    dm1 = MagicMock()
    dm1.serialize.return_value = {
        "deploymentManagerId": deployment_manager_id1,
    }

    order_by = MagicMock()
    order_by.count.return_value = 1
    order_by.limit.return_value.offset.return_value = [dm1]
    session.return_value.query.return_value.filter.return_value.\
        order_by.return_value = order_by

    result = ocloud_view.deployment_managers(uow)
    assert result['count'] == 1
    ret_list = result['results']
    assert str(ret_list[0].get("deploymentManagerId")
               ) == deployment_manager_id1


def test_view_deployment_manager_one(mock_uow):
    session, uow = mock_uow

    deployment_manager_id1 = str(uuid.uuid4())
    session.return_value.query.return_value.filter_by.return_value.first.\
        return_value.serialize.return_value = None

    # Query return None
    deployment_manager_res = ocloud_view.deployment_manager_one(
        deployment_manager_id1, uow)
    assert deployment_manager_res is None

    dms_endpoint = "http://o2:30205/o2dms/v1/uuid"
    session.return_value.query.return_value.filter_by.return_value.first.\
        return_value.serialize.return_value = {
            "deploymentManagerId": deployment_manager_id1,
            "serviceUri": dms_endpoint,
            "profile": {}
        }

    # profile default
    deployment_manager_res = ocloud_view.deployment_manager_one(
        deployment_manager_id1, uow)
    assert str(deployment_manager_res.get(
        "deploymentManagerId")) == deployment_manager_id1
    assert str(deployment_manager_res.get(
        'serviceUri')) == dms_endpoint
    assert deployment_manager_res.get('profile') is None

    # profile sol018
    profileName = ocloud.DeploymentManagerProfileSOL018
    cluster_endpoint = "https://test_k8s:6443"
    session.return_value.query.return_value.filter_by.return_value.first.\
        return_value.serialize.return_value['profile'] = {
            "cluster_api_endpoint": cluster_endpoint
        }
    deployment_manager_res = ocloud_view.deployment_manager_one(
        deployment_manager_id1, uow, profile=profileName)
    assert str(deployment_manager_res.get(
        'serviceUri')) == cluster_endpoint
    assert str(deployment_manager_res.get(
        "profileName")) == profileName

    # profile wrong name
    profileName = 'wrong_profile'
    session.return_value.query.return_value.filter_by.return_value.first.\
        return_value.serialize.return_value['profile'] = {
            "cluster_api_endpoint": cluster_endpoint
        }
    deployment_manager_res = ocloud_view.deployment_manager_one(
        deployment_manager_id1, uow, profile=profileName)
    assert deployment_manager_res is None


def test_view_subscriptions(mock_uow):
    session, uow = mock_uow

    subscription_id1 = str(uuid.uuid4())
    sub1 = MagicMock()
    sub1.serialize.return_value = {
        "subscriptionId": subscription_id1,
    }

    order_by = MagicMock()
    order_by.count.return_value = 1
    order_by.limit.return_value.offset.return_value = [sub1]
    session.return_value.query.return_value.filter.return_value.\
        order_by.return_value = order_by

    result = ocloud_view.subscriptions(uow)
    assert result['count'] == 1
    ret_list = result['results']
    assert str(ret_list[0].get("subscriptionId")) == subscription_id1


def test_view_subscription_one(mock_uow):
    session, uow = mock_uow

    subscription_id1 = str(uuid.uuid4())
    session.return_value.query.return_value.filter_by.return_value.first.\
        return_value.serialize.return_value = None

    # Query return None
    subscription_res = ocloud_view.subscription_one(
        subscription_id1, uow)
    assert subscription_res is None

    session.return_value.query.return_value.filter_by.return_value.first.\
        return_value.serialize.return_value = {
            "subscriptionId": subscription_id1,
        }

    subscription_res = ocloud_view.subscription_one(
        subscription_id1, uow)
    assert str(subscription_res.get(
        "subscriptionId")) == subscription_id1


def test_flask_get_list(mock_flask_uow):
    session, app = mock_flask_uow
    order_by = MagicMock()
    order_by.count.return_value = 0
    order_by.limit.return_value.offset.return_value = []
    session.return_value.query.return_value.filter.return_value.\
        order_by.return_value = order_by
    apibase = config.get_o2ims_api_base() + '/v1'
    # TODO: workaround for sqlalchemy not mapping with resource object
    setattr(ocloud.Resource, 'resourcePoolId', '')

    with app.test_client() as client:
        # Get list and return empty list
        ##########################
        resp = client.get(apibase+"/resourceTypes")
        assert resp.get_data() == b'[]\n'

        resp = client.get(apibase+"/resourcePools")
        assert resp.get_data() == b'[]\n'

        resource_pool_id1 = str(uuid.uuid4())
        resp = client.get(apibase+"/resourcePools/" +
                          resource_pool_id1+"/resources")
        assert resp.get_data() == b'[]\n'

        resp = client.get(apibase+"/deploymentManagers")
        assert resp.get_data() == b'[]\n'

        resp = client.get(apibase+"/subscriptions")
        assert resp.get_data() == b'[]\n'


def test_flask_get_one(mock_flask_uow):
    session, app = mock_flask_uow

    session.return_value.query.return_value.filter_by.return_value.\
        first.return_value = None
    apibase = config.get_o2ims_api_base() + '/v1'

    with app.test_client() as client:
        # Get one and return 404
        ###########################
        resp = client.get(apibase+"/")
        assert resp.status_code == 404

        resource_type_id1 = str(uuid.uuid4())
        resp = client.get(apibase+"/resourceTypes/"+resource_type_id1)
        assert resp.status_code == 404

        resource_pool_id1 = str(uuid.uuid4())
        resp = client.get(apibase+"/resourcePools/"+resource_pool_id1)
        assert resp.status_code == 404

        resource_id1 = str(uuid.uuid4())
        resp = client.get(apibase+"/resourcePools/" +
                          resource_pool_id1+"/resources/"+resource_id1)
        assert resp.status_code == 404

        deployment_manager_id1 = str(uuid.uuid4())
        resp = client.get(apibase+"/deploymentManagers/" +
                          deployment_manager_id1)
        assert resp.status_code == 404

        subscription_id1 = str(uuid.uuid4())
        resp = client.get(apibase+"/subscriptions/"+subscription_id1)
        assert resp.status_code == 404


def test_flask_post(mock_flask_uow):
    session, app = mock_flask_uow
    apibase = config.get_o2ims_api_base() + '/v1'

    with app.test_client() as client:
        session.return_value.execute.return_value = []

        sub_callback = 'http://subscription/callback/url'
        resp = client.post(apibase+'/subscriptions', json={
            'callback': sub_callback,
            'consumerSubscriptionId': 'consumerSubId1',
            'filter': 'empty'
        })
        assert resp.status_code == 201
        assert 'subscriptionId' in resp.get_json()


def test_flask_delete(mock_flask_uow):
    session, app = mock_flask_uow
    apibase = config.get_o2ims_api_base() + '/v1'

    with app.test_client() as client:
        session.return_value.execute.return_value.first.return_value = {}

        subscription_id1 = str(uuid.uuid4())
        resp = client.delete(apibase+"/subscriptions/"+subscription_id1)
        assert resp.status_code == 204


def test_flask_not_allowed(mock_flask_uow):
    _, app = mock_flask_uow
    apibase = config.get_o2ims_api_base() + '/v1'

    with app.test_client() as client:
        # Testing resource type not support method
        ##########################
        uri = apibase + "/resourceTypes"
        resp = client.post(uri)
        assert resp.status == '405 METHOD NOT ALLOWED'
        resp = client.put(uri)
        assert resp.status == '405 METHOD NOT ALLOWED'
        resp = client.patch(uri)
        assert resp.status == '405 METHOD NOT ALLOWED'
        resp = client.delete(uri)
        assert resp.status == '405 METHOD NOT ALLOWED'

        resource_type_id1 = str(uuid.uuid4())
        uri = apibase + "/resourceTypes/" + resource_type_id1
        resp = client.post(uri)
        assert resp.status == '405 METHOD NOT ALLOWED'
        resp = client.put(uri)
        assert resp.status == '405 METHOD NOT ALLOWED'
        resp = client.patch(uri)
        assert resp.status == '405 METHOD NOT ALLOWED'
        resp = client.delete(uri)
        assert resp.status == '405 METHOD NOT ALLOWED'

        # Testing resource pool not support method
        ##########################
        uri = apibase + "/resourcePools"
        resp = client.post(uri)
        assert resp.status == '405 METHOD NOT ALLOWED'
        resp = client.put(uri)
        assert resp.status == '405 METHOD NOT ALLOWED'
        resp = client.patch(uri)
        assert resp.status == '405 METHOD NOT ALLOWED'
        resp = client.delete(uri)
        assert resp.status == '405 METHOD NOT ALLOWED'

        resource_pool_id1 = str(uuid.uuid4())
        uri = apibase + "/resourcePools/" + resource_pool_id1
        resp = client.post(uri)
        assert resp.status == '405 METHOD NOT ALLOWED'
        resp = client.put(uri)
        assert resp.status == '405 METHOD NOT ALLOWED'
        resp = client.patch(uri)
        assert resp.status == '405 METHOD NOT ALLOWED'
        resp = client.delete(uri)
        assert resp.status == '405 METHOD NOT ALLOWED'

        # Testing resource not support method
        ##########################
        uri = apibase + "/resourcePools/" + resource_pool_id1 + "/resources"
        resp = client.post(uri)
        assert resp.status == '405 METHOD NOT ALLOWED'
        resp = client.put(uri)
        assert resp.status == '405 METHOD NOT ALLOWED'
        resp = client.patch(uri)
        assert resp.status == '405 METHOD NOT ALLOWED'
        resp = client.delete(uri)
        assert resp.status == '405 METHOD NOT ALLOWED'

        resource_id1 = str(uuid.uuid4())
        uri = apibase + "/resourcePools/" + \
            resource_pool_id1 + "/resources/" + resource_id1
        resp = client.post(uri)
        assert resp.status == '405 METHOD NOT ALLOWED'
        resp = client.put(uri)
        assert resp.status == '405 METHOD NOT ALLOWED'
        resp = client.patch(uri)
        assert resp.status == '405 METHOD NOT ALLOWED'
        resp = client.delete(uri)
        assert resp.status == '405 METHOD NOT ALLOWED'

        # Testing deployment managers not support method
        ##########################
        uri = apibase + "/deploymentManagers"
        resp = client.post(uri)
        assert resp.status == '405 METHOD NOT ALLOWED'
        resp = client.put(uri)
        assert resp.status == '405 METHOD NOT ALLOWED'
        resp = client.patch(uri)
        assert resp.status == '405 METHOD NOT ALLOWED'
        resp = client.delete(uri)
        assert resp.status == '405 METHOD NOT ALLOWED'

        deployment_manager_id1 = str(uuid.uuid4())
        uri = apibase + "/deploymentManagers/" + deployment_manager_id1
        resp = client.post(uri)
        assert resp.status == '405 METHOD NOT ALLOWED'
        resp = client.put(uri)
        assert resp.status == '405 METHOD NOT ALLOWED'
        resp = client.patch(uri)
        assert resp.status == '405 METHOD NOT ALLOWED'
        resp = client.delete(uri)
        assert resp.status == '405 METHOD NOT ALLOWED'

        # Testing subscriptions not support method
        ##########################
        uri = apibase + "/subscriptions"
        resp = client.put(uri)
        assert resp.status == '405 METHOD NOT ALLOWED'
        resp = client.patch(uri)
        assert resp.status == '405 METHOD NOT ALLOWED'
        resp = client.delete(uri)
        assert resp.status == '405 METHOD NOT ALLOWED'

        subscription_id1 = str(uuid.uuid4())
        uri = apibase + "/subscriptions/" + subscription_id1
        resp = client.post(uri)
        assert resp.status == '405 METHOD NOT ALLOWED'
        resp = client.put(uri)
        assert resp.status == '405 METHOD NOT ALLOWED'
        resp = client.patch(uri)
        assert resp.status == '405 METHOD NOT ALLOWED'
