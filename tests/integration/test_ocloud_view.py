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
from o2ims.views import ocloud_view
from o2ims.domain import ocloud
from o2ims.domain import resource_type as rt


pytestmark = pytest.mark.usefixtures("mappers")


def setup_ocloud():
    ocloudid1 = str(uuid.uuid4())
    ocloud1 = ocloud.Ocloud(
        ocloudid1, "ocloud1", config.get_api_url(),
        "ocloud 1 for integration test", 1)
    return ocloud1


def test_view_olcouds(sqlite_uow):
    ocloud1 = setup_ocloud()
    ocloud1_UUID = ocloud1.oCloudId
    with sqlite_uow as uow:
        uow.oclouds.add(ocloud1)
        uow.commit()

    ocloud_list = ocloud_view.oclouds(uow)
    assert str(ocloud_list[0].get("oCloudId")) == ocloud1_UUID


def test_view_olcoud_one(sqlite_uow):
    ocloud1 = setup_ocloud()
    ocloud1_UUID = ocloud1.oCloudId

    # Query return None
    ocloud_res = ocloud_view.ocloud_one(ocloud1_UUID, sqlite_uow)
    assert ocloud_res is None

    with sqlite_uow as uow:
        uow.oclouds.add(ocloud1)
        # INSERT INTO ocloud (oCloudId, name) VALUES (ocloud1_UUID, 'ocloud1')
        uow.commit()
    ocloud_res = ocloud_view.ocloud_one(ocloud1_UUID, uow)
    assert str(ocloud_res.get("oCloudId")) == ocloud1_UUID


def test_view_resource_types(sqlite_uow):
    ocloud1 = setup_ocloud()
    resource_type_id1 = str(uuid.uuid4())
    resource_type1 = ocloud.ResourceType(
        resource_type_id1, "resourcetype1", rt.ResourceTypeEnum.PSERVER,
        ocloud1.oCloudId)
    with sqlite_uow as uow:
        uow.resource_types.add(resource_type1)
        uow.commit()

    resource_type_list = ocloud_view.resource_types(uow)
    assert str(resource_type_list[0].get(
        "resourceTypeId")) == resource_type_id1


def test_view_resource_type_one(sqlite_uow):
    ocloud1 = setup_ocloud()
    resource_type_id1 = str(uuid.uuid4())
    resource_type1 = ocloud.ResourceType(
        resource_type_id1, "resourcetype1", rt.ResourceTypeEnum.PSERVER,
        ocloud1.oCloudId)

    # Query return None
    resource_type_res = ocloud_view.resource_type_one(
        resource_type_id1, sqlite_uow)
    assert resource_type_res is None

    with sqlite_uow as uow:
        uow.resource_types.add(resource_type1)
        uow.commit()
    resource_type_res = ocloud_view.resource_type_one(resource_type_id1, uow)
    assert str(resource_type_res.get("resourceTypeId")) == resource_type_id1


def test_view_resource_pools(sqlite_uow):
    ocloud1 = setup_ocloud()
    resource_pool_id1 = str(uuid.uuid4())
    resource_pool1 = ocloud.ResourcePool(
        resource_pool_id1, "resourcepool1", config.get_api_url(),
        ocloud1.oCloudId)
    with sqlite_uow as uow:
        uow.resource_pools.add(resource_pool1)
        uow.commit()

    resource_pool_list = ocloud_view.resource_pools(uow)
    assert str(resource_pool_list[0].get(
        "resourcePoolId")) == resource_pool_id1


def test_view_resource_pool_one(sqlite_uow):
    ocloud1 = setup_ocloud()
    resource_pool_id1 = str(uuid.uuid4())
    resource_pool1 = ocloud.ResourcePool(
        resource_pool_id1, "resourcepool1", config.get_api_url(),
        ocloud1.oCloudId)

    # Query return None
    resource_pool_res = ocloud_view.resource_pool_one(
        resource_pool_id1, sqlite_uow)
    assert resource_pool_res is None

    with sqlite_uow as uow:
        uow.resource_pools.add(resource_pool1)
        uow.commit()
    resource_pool_res = ocloud_view.resource_pool_one(resource_pool_id1, uow)
    assert str(resource_pool_res.get("resourcePoolId")) == resource_pool_id1


def test_view_resources(sqlite_uow):
    resource_id1 = str(uuid.uuid4())
    resource_type_id1 = str(uuid.uuid4())
    resource_pool_id1 = str(uuid.uuid4())
    resource1 = ocloud.Resource(
        resource_id1, resource_type_id1, resource_pool_id1)
    with sqlite_uow as uow:
        uow.resources.add(resource1)
        uow.commit()

    resource_list = ocloud_view.resources(resource_pool_id1, uow)
    assert str(resource_list[0].get("resourceId")) == resource_id1


def test_view_resource_one(sqlite_uow):
    resource_id1 = str(uuid.uuid4())
    resource_type_id1 = str(uuid.uuid4())
    resource_pool_id1 = str(uuid.uuid4())
    resource1 = ocloud.Resource(
        resource_id1, resource_type_id1, resource_pool_id1)

    # Query return None
    resource_res = ocloud_view.resource_one(resource_id1, sqlite_uow)
    assert resource_res is None

    with sqlite_uow as uow:
        uow.resources.add(resource1)
        uow.commit()

    resource_res = ocloud_view.resource_one(resource_id1, uow)
    assert str(resource_res.get("resourceId")) == resource_id1


def test_view_deployment_managers(sqlite_uow):
    ocloud_id1 = str(uuid.uuid4())
    deployment_manager_id1 = str(uuid.uuid4())
    deployment_manager1 = ocloud.DeploymentManager(
        deployment_manager_id1, "k8s1", ocloud_id1,
        config.get_api_url()+"/k8s1")
    with sqlite_uow as uow:
        uow.deployment_managers.add(deployment_manager1)
        uow.commit()

    deployment_manager_list = ocloud_view.deployment_managers(uow)
    assert str(deployment_manager_list[0].get(
        "deploymentManagerId")) == deployment_manager_id1


def test_view_deployment_manager_one(sqlite_uow):
    ocloud_id1 = str(uuid.uuid4())
    deployment_manager_id1 = str(uuid.uuid4())
    deployment_manager1 = ocloud.DeploymentManager(
        deployment_manager_id1, "k8s1", ocloud_id1,
        config.get_api_url()+"/k8s1")

    # Query return None
    deployment_manager_res = ocloud_view.deployment_manager_one(
        deployment_manager_id1, sqlite_uow)
    assert deployment_manager_res is None

    with sqlite_uow as uow:
        uow.deployment_managers.add(deployment_manager1)
        uow.commit()

    deployment_manager_res = ocloud_view.deployment_manager_one(
        deployment_manager_id1, sqlite_uow)
    assert str(deployment_manager_res.get(
        "deploymentManagerId")) == deployment_manager_id1


def test_view_subscriptions(sqlite_uow):

    subscription_id1 = str(uuid.uuid4())
    subscription1 = ocloud.Subscription(
        subscription_id1, "https://callback/uri/write/here")
    with sqlite_uow as uow:
        uow.subscriptions.add(subscription1)
        uow.commit()

    subscription_list = ocloud_view.subscriptions(uow)
    assert str(subscription_list[0].get(
        "subscriptionId")) == subscription_id1


def test_view_subscription_one(sqlite_uow):

    subscription_id1 = str(uuid.uuid4())
    subscription1 = ocloud.Subscription(
        subscription_id1, "https://callback/uri/write/here")

    # Query return None
    subscription_res = ocloud_view.subscription_one(
        subscription_id1, sqlite_uow)
    assert subscription_res is None

    with sqlite_uow as uow:
        uow.subscriptions.add(subscription1)
        uow.commit()

    subscription_res = ocloud_view.subscription_one(
        subscription_id1, sqlite_uow)
    assert str(subscription_res.get(
        "subscriptionId")) == subscription_id1


def test_view_subscription_delete(sqlite_uow):

    subscription_id1 = str(uuid.uuid4())
    subscription1 = ocloud.Subscription(
        subscription_id1, "https://callback/uri/write/here")

    with sqlite_uow as uow:
        uow.subscriptions.add(subscription1)
        uow.commit()

    subscription_res = ocloud_view.subscription_one(
        subscription_id1, sqlite_uow)
    assert str(subscription_res.get(
        "subscriptionId")) == subscription_id1

    with sqlite_uow as uow:
        uow.subscriptions.delete(subscription_id1)
        uow.commit()

    subscription_res = ocloud_view.subscription_one(
        subscription_id1, sqlite_uow)
    assert subscription_res is None
