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

from o2ims.domain import resource_type as rt
from o2ims.adapter import ocloud_repository as repository
from o2ims.domain import ocloud, subscription_obj
from o2common.config import config

pytestmark = pytest.mark.usefixtures("mappers")


def setup_ocloud():
    ocloudid1 = str(uuid.uuid4())
    ocloud1 = ocloud.Ocloud(
        ocloudid1, "ocloud1", config.get_api_url(),
        "ocloud 1 for integration test", 1)
    return ocloud1


def setup_ocloud_and_save(sqlite_session_factory):
    session = sqlite_session_factory()
    repo = repository.OcloudSqlAlchemyRepository(session)
    ocloudid1 = str(uuid.uuid4())
    ocloud1 = ocloud.Ocloud(
        ocloudid1, "ocloud1", config.get_api_url(),
        "ocloud for integration test", 1)
    repo.add(ocloud1)
    assert repo.get(ocloudid1) == ocloud1
    session.flush()
    return ocloud1


def test_add_ocloud(sqlite_session_factory):
    session = sqlite_session_factory()
    repo = repository.OcloudSqlAlchemyRepository(session)
    ocloudid1 = str(uuid.uuid4())
    ocloud1 = ocloud.Ocloud(
        ocloudid1, "ocloud1", config.get_api_url(),
        "ocloud for integration test", 1)
    repo.add(ocloud1)
    assert repo.get(ocloudid1) == ocloud1


def test_get_ocloud(sqlite_session_factory):
    ocloud1 = setup_ocloud_and_save(sqlite_session_factory)
    session = sqlite_session_factory()
    repo = repository.OcloudSqlAlchemyRepository(session)
    ocloud2 = repo.get(ocloud1.oCloudId)
    assert ocloud2 != ocloud1 and ocloud2.oCloudId == ocloud1.oCloudId


# def test_add_ocloud_with_dms(sqlite_session_factory):
#     session = sqlite_session_factory()
#     repo = repository.OcloudSqlAlchemyRepository(session)
#     ocloud1 = setup_ocloud()
#     dmsid = str(uuid.uuid4())
#     dms = ocloud.DeploymentManager(
#         dmsid, "k8s1", ocloud1.oCloudId, config.get_api_url()+"/k8s1")
#     ocloud1.addDeploymentManager(dms)
#     repo.add(ocloud1)
#     session.flush()
#     # seperate session to confirm ocloud is updated into repo
#     session2 = sqlite_session_factory()
#     repo2 = repository.OcloudSqlAlchemyRepository(session2)
#     ocloud2 = repo2.get(ocloud1.oCloudId)
#     assert ocloud2 is not None
#     assert ocloud2 != ocloud1 and ocloud2.oCloudId == ocloud1.oCloudId
#     assert len(ocloud2.deploymentManagers) == 1


# def test_update_ocloud_with_dms(sqlite_session_factory):
#     session = sqlite_session_factory()
#     repo = repository.OcloudSqlAlchemyRepository(session)
#     ocloud1 = setup_ocloud()
#     repo.add(ocloud1)
#     session.flush()
#     dmsid = str(uuid.uuid4())
#     dms = ocloud.DeploymentManager(
#         dmsid, "k8s1", ocloud1.oCloudId, config.get_api_url()+"/k8s1")
#     ocloud1.addDeploymentManager(dms)
#     repo.update(ocloud1)
#     # repo.update(ocloud1.oCloudId, {"deploymentManagers":
#     # ocloud1.deploymentManagers})
#     session.flush()

#     # seperate session to confirm ocloud is updated into repo
#     session2 = sqlite_session_factory()
#     repo2 = repository.OcloudSqlAlchemyRepository(session2)
#     ocloud2 = repo2.get(ocloud1.oCloudId)
#     assert ocloud2 is not None
#     assert ocloud2 != ocloud1 and ocloud2.oCloudId == ocloud1.oCloudId
#     assert len(ocloud2.deploymentManagers) == 1


def test_add_resource_type(sqlite_session_factory):
    session = sqlite_session_factory()
    repo = repository.ResouceTypeSqlAlchemyRepository(session)
    ocloud1_id = str(uuid.uuid4())
    resource_type_id1 = str(uuid.uuid4())
    resource_type1 = ocloud.ResourceType(
        resource_type_id1, "resourcetype1", rt.ResourceTypeEnum.PSERVER,
        ocloud1_id)
    repo.add(resource_type1)
    assert repo.get(resource_type_id1) == resource_type1


def test_add_resource_pool(sqlite_session_factory):
    session = sqlite_session_factory()
    repo = repository.ResourcePoolSqlAlchemyRepository(session)
    ocloud1_id = str(uuid.uuid4())
    resource_pool_id1 = str(uuid.uuid4())
    resource_pool1 = ocloud.ResourcePool(
        resource_pool_id1, "resourcepool1", config.get_api_url(),
        ocloud1_id)
    repo.add(resource_pool1)
    assert repo.get(resource_pool_id1) == resource_pool1


def test_add_resource(sqlite_session_factory):
    session = sqlite_session_factory()
    repo = repository.ResourceSqlAlchemyRepository(session)
    resource_id1 = str(uuid.uuid4())
    resource_type_id1 = str(uuid.uuid4())
    resource_pool_id1 = str(uuid.uuid4())
    resource1 = ocloud.Resource(
        resource_id1, resource_type_id1, resource_pool_id1, 'resource1')
    repo.add(resource1)
    assert repo.get(resource_id1) == resource1


def test_add_deployment_manager(sqlite_session_factory):
    session = sqlite_session_factory()
    repo = repository.DeploymentManagerSqlAlchemyRepository(session)
    ocloud_id1 = str(uuid.uuid4())
    deployment_manager_id1 = str(uuid.uuid4())
    deployment_manager1 = ocloud.DeploymentManager(
        deployment_manager_id1, "k8s1", ocloud_id1,
        config.get_api_url()+"/k8s1")
    repo.add(deployment_manager1)
    assert repo.get(deployment_manager_id1) == deployment_manager1


def test_add_subscription(sqlite_session_factory):
    session = sqlite_session_factory()
    repo = repository.SubscriptionSqlAlchemyRepository(session)
    subscription_id1 = str(uuid.uuid4())
    subscription1 = subscription_obj.Subscription(
        subscription_id1, "https://callback/uri/write/here")
    repo.add(subscription1)
    assert repo.get(subscription_id1) == subscription1
