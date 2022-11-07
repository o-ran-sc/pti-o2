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

import filecmp
import os.path
import uuid
import yaml
from datetime import datetime
import shutil

from o2common.service import unit_of_work
from o2common.config import config
from o2common.views.pagination_view import Pagination
from o2common.views.view import gen_filter
from o2ims.domain import ocloud
from o2ims.views.ocloud_dto import SubscriptionDTO
from o2ims.domain.subscription_obj import Subscription

from o2common.helper import o2logging
logger = o2logging.get_logger(__name__)


def oclouds(uow: unit_of_work.AbstractUnitOfWork):
    with uow:
        li = uow.oclouds.list()
    return [r.serialize() for r in li]


def ocloud_one(ocloudid: str, uow: unit_of_work.AbstractUnitOfWork):
    with uow:
        first = uow.oclouds.get(ocloudid)
        return first.serialize() if first is not None else None


def resource_types(uow: unit_of_work.AbstractUnitOfWork, **kwargs):
    pagination = Pagination(**kwargs)
    query_kwargs = pagination.get_pagination()
    args = gen_filter(ocloud.ResourceType,
                      kwargs['filter']) if 'filter' in kwargs else []
    with uow:
        li = uow.resource_types.list_with_count(*args, **query_kwargs)
    return pagination.get_result(li)


def resource_type_one(resourceTypeId: str,
                      uow: unit_of_work.AbstractUnitOfWork):
    with uow:
        first = uow.resource_types.get(resourceTypeId)
        return first.serialize() if first is not None else None


def resource_pools(uow: unit_of_work.AbstractUnitOfWork, **kwargs):
    pagination = Pagination(**kwargs)
    query_kwargs = pagination.get_pagination()
    args = gen_filter(ocloud.ResourcePool,
                      kwargs['filter']) if 'filter' in kwargs else []
    with uow:
        li = uow.resource_pools.list_with_count(*args, **query_kwargs)
    return pagination.get_result(li)


def resource_pool_one(resourcePoolId: str,
                      uow: unit_of_work.AbstractUnitOfWork):
    with uow:
        first = uow.resource_pools.get(resourcePoolId)
        return first.serialize() if first is not None else None


def resources(resourcePoolId: str, uow: unit_of_work.AbstractUnitOfWork,
              **kwargs):
    pagination = Pagination(**kwargs)
    # filter key should be the same with database name
    query_kwargs = pagination.get_pagination()
    if 'resourceTypeName' in kwargs:
        resource_type_name = kwargs['resourceTypeName']
        with uow:
            # res_types = uow.resource_types.list()
            # restype_ids = [
            #     restype.resourceTypeId for restype in res_types
            #     if resourceTypeName == restype.name]
            # restype_id = '' if len(restype_ids) == 0 else restype_ids[0]
            res_type = uow.resource_types.get_by_name(resource_type_name)
            restype_id = '' if res_type is None else res_type.resourceTypeId
        query_kwargs['resourceTypeId'] = restype_id
    args = gen_filter(
        ocloud.Resource, kwargs['filter']) if 'filter' in kwargs else []
    args.append(ocloud.Resource.resourcePoolId == resourcePoolId)
    # args.append(ocloud.Resource.parentId == None)

    if 'parentId' in kwargs:
        query_kwargs['parentId'] = kwargs['parentId']
    if 'sort' in kwargs:
        query_kwargs['sort'] = kwargs['sort']

    with uow:
        ret = uow.resources.list_with_count(
            resourcePoolId, *args, **query_kwargs)

    return pagination.get_result(ret)


def resource_one(resourceId: str, uow: unit_of_work.AbstractUnitOfWork):
    with uow:
        first = uow.resources.get(resourceId)
        return first.serialize() if first is not None else None


def deployment_managers(uow: unit_of_work.AbstractUnitOfWork, **kwargs):
    pagination = Pagination(**kwargs)
    query_kwargs = pagination.get_pagination()
    args = gen_filter(ocloud.DeploymentManager,
                      kwargs['filter']) if 'filter' in kwargs else []
    with uow:
        li = uow.deployment_managers.list_with_count(*args, **query_kwargs)
    return pagination.get_result(li)


def deployment_manager_one(deploymentManagerId: str,
                           uow: unit_of_work.AbstractUnitOfWork,
                           profile: str =
                           ocloud.DeploymentManagerProfileDefault):
    profile = profile.lower()
    with uow:
        first = uow.deployment_managers.get(deploymentManagerId)
        if first is None:
            return first
        result = first.serialize()
        if result is None:
            return None

    profile_data = result.pop("profile", None)
    result['profileName'] = profile
    profiles = config.get_dms_support_profiles()
    if profile not in profiles:
        return ""

    if ocloud.DeploymentManagerProfileDefault == profile \
            or ocloud.DeploymentManagerProfileSOL018 == profile:
        result['serviceUri'] = \
            profile_data['cluster_api_endpoint']
        result['profileData'] = profile_data
    elif ocloud.DeploymentManagerProfileSOL018HelmCLI == profile:
        result['serviceUri'] = \
            profile_data['cluster_api_endpoint']

        helmcli_profile = dict()
        helmcli_profile["helmcli_host_with_port"], helmcli_profile[
            "helmcli_username"], helmcli_profile["helmcli_password"] = \
            config.get_helmcli_access()
        helmcli_profile["helmcli_kubeconfig"] = _gen_kube_config(
            deploymentManagerId, profile_data)
        result['profileData'] = helmcli_profile
    else:
        return ""

    return result


def _gen_kube_config(dmId: str, kubeconfig: dict) -> dict:

    data = config.gen_k8s_config_dict(
        kubeconfig.pop('cluster_api_endpoint', None),
        kubeconfig.pop('cluster_ca_cert', None),
        kubeconfig.pop('admin_user', None),
        kubeconfig.pop('admin_client_cert', None),
        kubeconfig.pop('admin_client_key', None),
    )

    # Generate a random key for tmp kube config file
    # letters = string.ascii_uppercase
    # random_key = ''.join(random.choice(letters) for i in range(10))
    name_key = dmId[:8]

    # Get datetime of now as tag of the tmp file
    current_time = datetime.now().strftime("%Y%m%d%H%M%S")
    tmp_file_name = 'kubeconfig_' + name_key + "_" + current_time
    kube_config_name = 'kubeconfig_' + name_key + '.config'

    # write down the yaml file of kubectl into tmp folder
    with open('/tmp/' + tmp_file_name, 'w') as file:
        yaml.dump(data, file)

    # generate the kube config file if not exist or update the file if it
    # changes
    if not os.path.exists('/configs/' + kube_config_name) or not \
            filecmp.cmp('/tmp/'+tmp_file_name, '/configs/'+kube_config_name):
        shutil.move(os.path.join('/tmp', tmp_file_name),
                    os.path.join('/configs', kube_config_name))

    return '/configs/'+kube_config_name


def subscriptions(uow: unit_of_work.AbstractUnitOfWork, **kwargs):
    pagination = Pagination(**kwargs)
    query_kwargs = pagination.get_pagination()
    args = gen_filter(Subscription,
                      kwargs['filter']) if 'filter' in kwargs else []
    with uow:
        li = uow.subscriptions.list_with_count(*args, **query_kwargs)
    return pagination.get_result(li)


def subscription_one(subscriptionId: str,
                     uow: unit_of_work.AbstractUnitOfWork):
    with uow:
        first = uow.subscriptions.get(subscriptionId)
        return first.serialize() if first is not None else None


def subscription_create(subscriptionDto: SubscriptionDTO.subscription_create,
                        uow: unit_of_work.AbstractUnitOfWork):

    sub_uuid = str(uuid.uuid4())
    subscription = Subscription(
        sub_uuid, subscriptionDto['callback'],
        subscriptionDto['consumerSubscriptionId'],
        subscriptionDto['filter'])
    with uow:
        uow.subscriptions.add(subscription)
        uow.commit()
        first = uow.subscriptions.get(sub_uuid)
        return first.serialize()


def subscription_delete(subscriptionId: str,
                        uow: unit_of_work.AbstractUnitOfWork):
    with uow:
        uow.subscriptions.delete(subscriptionId)
        uow.commit()
    return True
