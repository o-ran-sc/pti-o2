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
import yaml
import random
import string
from datetime import datetime

from o2common.service import unit_of_work
from o2ims.views.ocloud_dto import SubscriptionDTO
from o2ims.domain.subscription_obj import Subscription

from o2common.helper import o2logging
from o2common.config import config
logger = o2logging.get_logger(__name__)


def oclouds(uow: unit_of_work.AbstractUnitOfWork):
    with uow:
        li = uow.oclouds.list()
    return [r.serialize() for r in li]


def ocloud_one(ocloudid: str, uow: unit_of_work.AbstractUnitOfWork):
    with uow:
        first = uow.oclouds.get(ocloudid)
        return first.serialize() if first is not None else None


def resource_types(uow: unit_of_work.AbstractUnitOfWork):
    with uow:
        li = uow.resource_types.list()
    return [r.serialize() for r in li]


def resource_type_one(resourceTypeId: str,
                      uow: unit_of_work.AbstractUnitOfWork):
    with uow:
        first = uow.resource_types.get(resourceTypeId)
        return first.serialize() if first is not None else None


def resource_pools(uow: unit_of_work.AbstractUnitOfWork):
    with uow:
        li = uow.resource_pools.list()
    return [r.serialize() for r in li]


def resource_pool_one(resourcePoolId: str,
                      uow: unit_of_work.AbstractUnitOfWork):
    with uow:
        first = uow.resource_pools.get(resourcePoolId)
        return first.serialize() if first is not None else None


def resources(resourcePoolId: str, uow: unit_of_work.AbstractUnitOfWork,
              **kwargs):

    filter_kwargs = {}  # filter key should be the same with database name
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
        filter_kwargs['resourceTypeId'] = restype_id

        #     li = uow.resources.list(resourcePoolId)
        # return [r.serialize() for r in li if r.resourceTypeId == restype_id]
    if 'parentId' in kwargs:
        filter_kwargs['parentId'] = kwargs['parentId']

    with uow:
        li = uow.resources.list(resourcePoolId, **filter_kwargs)
    return [r.serialize() for r in li]


def resource_one(resourceId: str, uow: unit_of_work.AbstractUnitOfWork):
    with uow:
        first = uow.resources.get(resourceId)
        return first.serialize() if first is not None else None


def deployment_managers(uow: unit_of_work.AbstractUnitOfWork):
    with uow:
        li = uow.deployment_managers.list()
    return [r.serialize() for r in li]


def deployment_manager_one(deploymentManagerId: str,
                           uow: unit_of_work.AbstractUnitOfWork,
                           profile: str = 'params'):
    with uow:
        first = uow.deployment_managers.get(deploymentManagerId)
        if first is None:
            return first
        result = first.serialize()

    if "params" == profile:
        pass
    elif "file" == profile and result.hasattr("profile"):
        p = result.pop("profile", None)
        result["profile"] = _gen_kube_config(deploymentManagerId, p)
    else:
        result.pop("profile", None)

    return result


def _gen_kube_config(dmId: str, kubeconfig: dict) -> dict:

    # KUBECONFIG environment variable
    # reference:
    # https://kubernetes.io/docs/tasks/access-application-cluster/configure-access-multiple-clusters/
    data = {
        'apiVersion': 'v1',
        'clusters': [
            {
                'cluster': {
                    'server':
                    kubeconfig.pop('cluster_api_endpoint', None),
                    'certificate-authority-data':
                    kubeconfig.pop('cluster_ca_cert', None),
                },
                'name': 'inf-cluster'
            }],
        'contexts': [
            {
                'context': {
                    'cluster': 'inf-cluster',
                    'user': 'kubernetes-admin'
                },
                'name': 'kubernetes-admin@inf-cluster'
            }
        ],
        'current-context': 'kubernetes-admin@inf-cluster',
        'kind': 'Config',
        'preferences': {},
        'users': [
            {
                'name': kubeconfig.pop('admin_user', None),
                'user': {
                    'client-certificate-data':
                    kubeconfig.pop('admin_client_cert', None),
                    'client-key-data':
                    kubeconfig.pop('admin_client_key', None),
                }
            }]
    }

    # Generate a random key for tmp kube config file
    letters = string.ascii_uppercase
    random_key = ''.join(random.choice(letters) for i in range(10))

    # Get datetime of now as tag of the tmp file
    current_time = datetime.now().strftime("%Y%m%d%H%M%S")
    tmp_file_name = random_key + "_" + current_time

    # write down the yaml file of kubectl into tmp folder
    with open('/tmp/kubeconfig_' + tmp_file_name, 'w') as file:
        yaml.dump(data, file)

    kubeconfig["kube_config_file"] = config.get_api_url() + \
        config.get_o2dms_api_base() + "/" + dmId + "/download/" + tmp_file_name

    return kubeconfig


def subscriptions(uow: unit_of_work.AbstractUnitOfWork):
    with uow:
        li = uow.subscriptions.list()
    return [r.serialize() for r in li]


def subscription_one(subscriptionId: str,
                     uow: unit_of_work.AbstractUnitOfWork):
    with uow:
        first = uow.subscriptions.get(subscriptionId)
        return first.serialize() if first is not None else None


def subscription_create(subscriptionDto: SubscriptionDTO.subscription,
                        uow: unit_of_work.AbstractUnitOfWork):

    sub_uuid = str(uuid.uuid4())
    subscription = Subscription(
        sub_uuid, subscriptionDto['callback'],
        subscriptionDto['consumerSubscriptionId'],
        subscriptionDto['filter'])
    with uow:
        uow.subscriptions.add(subscription)
        uow.commit()
    return {"subscriptionId": sub_uuid}


def subscription_delete(subscriptionId: str,
                        uow: unit_of_work.AbstractUnitOfWork):
    with uow:
        uow.subscriptions.delete(subscriptionId)
        uow.commit()
    return True
