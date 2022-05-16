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

import string
import random
import yaml
from datetime import datetime

# from sqlalchemy import select
from o2common.service import unit_of_work
# from o2ims.adapter.orm import deploymentmanager
from o2common.helper import o2logging
from o2common.config import config
logger = o2logging.get_logger(__name__)


def deployment_managers(uow: unit_of_work.AbstractUnitOfWork):
    # with uow:
    # res = uow.session.execute(select(deploymentmanager))
    # return [dict(r) for r in res]
    with uow:
        li = uow.deployment_managers.list()
    return [r.serialize() for r in li]


def deployment_manager_one(deploymentManagerId: str,
                           uow: unit_of_work.AbstractUnitOfWork,
                           profile: str = 'params'):
    # with uow:
    #     res = uow.session.execute(select(deploymentmanager).where(
    #         deploymentmanager.c.deploymentManagerId == deploymentManagerId))
    #     first = res.first()
    # return None if first is None else dict(first)
    # with uow:
    # first = uow.deployment_managers.get(deploymentManagerId)
    # return first.serialize() if first is not None else None
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
