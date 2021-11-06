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

from o2ims.domain import ocloud
from o2ims import config
import uuid


def setup_ocloud():
    ocloudid1 = str(uuid.uuid4())
    ocloud1 = ocloud.Ocloud(ocloudid1, "ocloud1", config.get_api_url(), "ocloud for unit test", 1)
    return ocloud1

def test_new_ocloud():
    ocloudid1 = str(uuid.uuid4())
    ocloud1 = ocloud.Ocloud(ocloudid1, "ocloud1", config.get_api_url(), "ocloud for unit test", 1)
    assert ocloudid1 is not None and ocloud1.oCloudId == ocloudid1

def test_add_ocloud_with_dms():
    ocloud1 = setup_ocloud()
    dmsid = str(uuid.uuid4())
    dms = ocloud.DeploymentManager(
        dmsid, "k8s1", ocloud1.oCloudId, config.get_api_url()+"/k8s1")
    ocloud1.addDeploymentManager(dms)
    ocloud1.addDeploymentManager(dms)
    assert len(ocloud1.deploymentManagers) == 1
    # repo.update(ocloud1.oCloudId, {"deploymentManagers": ocloud1.deploymentManagers})
