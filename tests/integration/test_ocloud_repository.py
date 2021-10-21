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

import pytest
from o2ims.adapter import ocloud_repository as repository
from o2ims.domain import ocloud
from o2ims import config
import uuid

pytestmark = pytest.mark.usefixtures("mappers")


def setup_ocloud():
    ocloudid1 = str(uuid.uuid4())
    ocloud1 = ocloud.Ocloud(ocloudid1, "ocloud1", config.get_api_url(), "ocloud 1 for integration test", 1)
    return ocloud1

def setup_ocloud_and_save(sqlite_session_factory):
    session = sqlite_session_factory()
    repo = repository.OcloudSqlAlchemyRepository(session)
    ocloudid1 = str(uuid.uuid4())
    ocloud1 = ocloud.Ocloud(ocloudid1, "ocloud1", config.get_api_url(), "ocloud for integration test", 1)
    repo.add(ocloud1)
    assert repo.get(ocloudid1) == ocloud1
    session.flush()
    return ocloud1

def test_add_ocloud(sqlite_session_factory):
    session = sqlite_session_factory()
    repo = repository.OcloudSqlAlchemyRepository(session)
    ocloudid1 = str(uuid.uuid4())
    ocloud1 = ocloud.Ocloud(ocloudid1, "ocloud1", config.get_api_url(), "ocloud for integration test", 1)
    repo.add(ocloud1)
    assert repo.get(ocloudid1) == ocloud1

def test_get_ocloud(sqlite_session_factory):
    ocloud1 = setup_ocloud_and_save(sqlite_session_factory)
    session = sqlite_session_factory()
    repo = repository.OcloudSqlAlchemyRepository(session)
    ocloud2 = repo.get(ocloud1.oCloudId)
    assert ocloud2 != ocloud1 and ocloud2.oCloudId == ocloud1.oCloudId

def test_add_ocloud_with_dms(sqlite_session_factory):
    session = sqlite_session_factory()
    repo = repository.OcloudSqlAlchemyRepository(session)
    ocloud1 = setup_ocloud()
    dmsid = str(uuid.uuid4())
    dms = ocloud.DeploymentManager(
        dmsid, "k8s1", ocloud1.oCloudId, config.get_api_url()+"/k8s1")
    ocloud1.addDeploymentManager(dms)
    repo.add(ocloud1)
    session.flush()
    # seperate session to confirm ocloud is updated into repo
    session2 = sqlite_session_factory()
    repo2 = repository.OcloudSqlAlchemyRepository(session2)
    ocloud2 = repo2.get(ocloud1.oCloudId)
    assert ocloud2 is not None
    assert ocloud2 != ocloud1 and ocloud2.oCloudId == ocloud1.oCloudId
    assert len(ocloud2.deploymentManagers) == 1


def test_update_ocloud_with_dms(sqlite_session_factory):
    session = sqlite_session_factory()
    repo = repository.OcloudSqlAlchemyRepository(session)
    ocloud1 = setup_ocloud()
    repo.add(ocloud1)
    session.flush()
    dmsid = str(uuid.uuid4())
    dms = ocloud.DeploymentManager(
        dmsid, "k8s1", ocloud1.oCloudId, config.get_api_url()+"/k8s1")
    ocloud1.addDeploymentManager(dms)
    repo.update(ocloud1)
    # repo.update(ocloud1.oCloudId, {"deploymentManagers": ocloud1.deploymentManagers})
    session.flush()

    # seperate session to confirm ocloud is updated into repo
    session2 = sqlite_session_factory()
    repo2 = repository.OcloudSqlAlchemyRepository(session2)
    ocloud2 = repo2.get(ocloud1.oCloudId)
    assert ocloud2 is not None
    assert ocloud2 != ocloud1 and ocloud2.oCloudId == ocloud1.oCloudId
    assert len(ocloud2.deploymentManagers) == 1
