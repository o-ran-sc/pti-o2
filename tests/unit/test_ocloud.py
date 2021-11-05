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

from o2ims.domain import ocloud
from o2ims.domain import resource_type as rt
from o2ims import config
from o2ims.views import ocloud_view


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


def test_add_ocloud_with_dms():
    ocloud1 = setup_ocloud()
    dmsid = str(uuid.uuid4())
    dms = ocloud.DeploymentManager(
        dmsid, "k8s1", ocloud1.oCloudId, config.get_api_url()+"/k8s1")
    ocloud1.addDeploymentManager(dms)
    ocloud1.addDeploymentManager(dms)
    assert len(ocloud1.deploymentManagers) == 1
    # repo.update(ocloud1.oCloudId, {
    #             "deploymentManagers": ocloud1.deploymentManagers})


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
        resource_id1, resource_type_id1, resource_pool_id1)
    assert resource_id1 is not None and resource1.resourceId == resource_id1


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
        # uow.session.execute()
        uow.oclouds.add(resource_type1)
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
        uow.oclouds.add(resource_type1)
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
        uow.oclouds.add(resource_pool1)
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
        uow.oclouds.add(resource_pool1)
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
        uow.oclouds.add(resource1)
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
        uow.oclouds.add(resource1)
        uow.commit()

    resource_res = ocloud_view.resource_one(resource_id1, uow)
    assert str(resource_res.get("resourceId")) == resource_id1


def test_flask_get_list(sqlite_flask_uow):
    client = sqlite_flask_uow
    apibase = config.get_o2ims_api_base()

    # Get list and return empty list
    ##########################
    resp = client.get(apibase)
    assert resp.get_data() == b'[]\n'

    resp = client.get(apibase+"/resourceTypes")
    assert resp.get_data() == b'[]\n'

    resp = client.get(apibase+"/resourcePools")
    assert resp.get_data() == b'[]\n'

    resource_pool_id1 = str(uuid.uuid4())
    resp = client.get(apibase+"/resourcePools/"+resource_pool_id1+"/resources")
    assert resp.get_data() == b'[]\n'

    resp = client.get(apibase+"/deploymentManagers")
    assert resp.get_data() == b'[]\n'


def test_flask_get_one(sqlite_flask_uow):
    client = sqlite_flask_uow
    apibase = config.get_o2ims_api_base()

    # Get one and return nothing
    ###########################
    resource_type_id1 = str(uuid.uuid4())
    resp = client.get(apibase+"/resourceTypes/"+resource_type_id1)
    assert resp.get_data() == b''

    resource_pool_id1 = str(uuid.uuid4())
    resp = client.get(apibase+"/resourcePools/"+resource_pool_id1)
    assert resp.get_data() == b''

    resource_id1 = str(uuid.uuid4())
    resp = client.get(apibase+"/resourcePools/" +
                      resource_pool_id1+"/resources/"+resource_id1)
    assert resp.get_data() == b''

    deployment_manager_id1 = str(uuid.uuid4())
    resp = client.get(apibase+"/deploymentManagers/"+deployment_manager_id1)
    assert resp.get_data() == b''


def test_flask_not_allowed(sqlite_flask_uow):
    client = sqlite_flask_uow
    apibase = config.get_o2ims_api_base()

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
