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
from o2common.views.view import gen_filter, check_filter
from o2common.views.pagination_view import Pagination
from o2common.views.route_exception import (
    BadRequestException,
    ConflictException,
    NotFoundException,
)

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
        return first.serialize() if first else None


def resources(resourcePoolId: str, uow: unit_of_work.AbstractUnitOfWork,
              **kwargs):
    with uow:
        first = uow.resource_pools.get(resourcePoolId)
    if first is None:
        raise NotFoundException("ResourcePool {} doesn't exist".format(
            resourcePoolId))
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

    if 'parentId' in kwargs:
        query_kwargs['parentId'] = kwargs['parentId']
    if 'sort' in kwargs:
        query_kwargs['sort'] = kwargs['sort']

    with uow:
        ret = uow.resources.list_with_count(
            resourcePoolId, *args, **query_kwargs)

    return pagination.get_result(ret)


def resource_one(resourceId: str,
                 uow: unit_of_work.AbstractUnitOfWork, resourcePoolId: str):
    with uow:
        resoucePool = uow.resource_pools.get(resourcePoolId)
    if resoucePool is None:
        raise NotFoundException("ResourcePool {} doesn't exist".format(
            resourcePoolId))

    first = uow.resources.get(resourceId)
    if first is None:
        raise NotFoundException("Resource {} doesn't exist".format(
            resourceId))
    return first.serialize()


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
    profiles = config.get_dms_support_profiles()
    if profile not in profiles:
        return ""

    extensions = {
        'profileName': profile
    }
    if ocloud.DeploymentManagerProfileDefault == profile \
            or ocloud.DeploymentManagerProfileSOL018 == profile:
        result['serviceUri'] = \
            profile_data['cluster_api_endpoint']
        extensions['profileData'] = profile_data
    elif ocloud.DeploymentManagerProfileSOL018HelmCLI == profile:
        result['serviceUri'] = \
            profile_data['cluster_api_endpoint']

        helmcli_profile = dict()
        helmcli_profile["helmcli_host_with_port"], helmcli_profile[
            "helmcli_username"], helmcli_profile["helmcli_password"] = \
            config.get_helmcli_access()
        helmcli_profile["helmcli_kubeconfig"] = _gen_kube_config(
            deploymentManagerId, profile_data)
        extensions['profileData'] = helmcli_profile
    else:
        return ""

    result['extensions'] = extensions
    return result


def _gen_kube_config(dmId: str, kubeconfig: dict) -> dict:
    shared_folder = config.get_containers_shared_folder()

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
    kube_config_path = f'{shared_folder}/{kube_config_name}'

    # write down the yaml file of kubectl into tmp folder
    with open('/tmp/' + tmp_file_name, 'w') as file:
        yaml.dump(data, file)

    # generate the kube config file if not exist or update the file if it
    # changes
    if not os.path.exists(kube_config_path) or not \
            filecmp.cmp('/tmp/'+tmp_file_name, kube_config_path):
        shutil.move(os.path.join('/tmp', tmp_file_name),
                    os.path.join(shared_folder, kube_config_name))

    return kube_config_path


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
    filter = subscriptionDto.get('filter', '')
    consumer_subs_id = subscriptionDto.get('consumerSubscriptionId', '')

    _check_subscription_filter(filter)

    sub_uuid = str(uuid.uuid4())
    subscription = Subscription(
        sub_uuid, subscriptionDto['callback'],
        consumer_subs_id, filter)
    with uow:
        args = list()
        args.append(getattr(Subscription, 'callback')
                    == subscriptionDto['callback'])
        args.append(getattr(Subscription, 'filter') == filter)
        args.append(getattr(Subscription,
                    'consumerSubscriptionId') == consumer_subs_id)
        count, _ = uow.subscriptions.list_with_count(*args)
        if count > 0:
            raise ConflictException("The value of parameters is duplicated")
        uow.subscriptions.add(subscription)
        uow.commit()
        first = uow.subscriptions.get(sub_uuid)
        return first.serialize()


def _check_subscription_filter(filter: str):
    if not filter:
        return

    def _sub_filter_checking(sub_filter: str):
        exprs = sub_filter.split(';')
        objectType = False
        objectTypeValue = ''
        for expr in exprs:
            expr_strip = expr.strip(' ()')
            items = expr_strip.split(',')
            if len(items) < 3:
                raise BadRequestException("invalid filter {}".format(expr))
            item_key = items[1].strip()
            if item_key != 'objectType':
                continue
            item_op = items[0].strip()
            if item_op != 'eq':
                raise BadRequestException(
                    "Filter objectType only support 'eq' operation")
            objectType = True
            objectTypeValue = items[2].strip()
        if not objectType:
            # if there has no objectType specific, by default is ResourceInfo
            check_filter(ocloud.Resource, sub_filter)
            # return 'ResourceInfo'
            return
        if objectTypeValue == 'ResourceTypeInfo':
            check_filter(ocloud.ResourceType, sub_filter)
        elif objectTypeValue == 'ResourcePoolInfo':
            check_filter(ocloud.ResourcePool, sub_filter)
        elif objectTypeValue == 'DeploymentManagerInfo':
            check_filter(ocloud.DeploymentManager, sub_filter)
        elif objectTypeValue == 'CloudInfo':
            check_filter(ocloud.Ocloud, sub_filter)
        elif objectTypeValue == 'ResourceInfo':
            check_filter(ocloud.Resource, sub_filter)
        else:
            raise BadRequestException(
                "Filter ObjectType {} not support.".format(items[2]))
        # return objectTypeValue
    filter_strip = filter.strip(' []')
    filter_list = filter_strip.split('|')
    # check_duplication = dict()
    for sub_filter in filter_list:
        _sub_filter_checking(sub_filter)
        # obj_type = _sub_filter_checking(sub_filter)
        # if obj_type not in check_duplication:
        #     check_duplication[obj_type] = 0
        # check_duplication[obj_type] += 1
        # if check_duplication[obj_type] > 1:
        #     raise BadRequestException(
        #         "Filter objectType {} only support one in each."
        #         .format(obj_type))


def subscription_delete(subscriptionId: str,
                        uow: unit_of_work.AbstractUnitOfWork):
    with uow:
        first = uow.subscriptions.get(subscriptionId)
        if not first:
            raise NotFoundException(
                "Subscription {} not found.".format(subscriptionId))
        uow.subscriptions.delete(subscriptionId)
        uow.commit()
    return True
