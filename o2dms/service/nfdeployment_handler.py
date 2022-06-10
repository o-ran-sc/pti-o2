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

# pylint: disable=unused-argument
from __future__ import annotations
import os
import json
import random
import string
import yaml
from datetime import datetime
from helm_sdk import Helm
from typing import Callable
from retry import retry

from o2dms.domain.states import NfDeploymentState
# from o2common.service import messagebus
from o2dms.domain.dms import NfDeployment, NfDeploymentDesc
from o2dms.domain import commands
from o2dms.domain.exceptions import NfdeploymentNotFoundError
from o2dms.domain import events
from o2common.service.unit_of_work import AbstractUnitOfWork
from o2common.config import config
# if TYPE_CHECKING:
#     from . import unit_of_work

from o2common.helper import o2logging
logger = o2logging.get_logger(__name__)
LOCAL_HELM_BIN = config.get_helm_cli()
K8S_KUBECONFIG, K8S_APISERVER, K8S_TOKEN = \
    config.get_k8s_api_endpoint()


def publish_nfdeployment_state_change(
    event: events.NfDeploymentStateChanged,
    publish: Callable,
):
    publish("NfDeploymentStateChanged", event)
    logger.debug(
        "published NfDeploymentStateChanged: {}, state from {} to {}".format(
            event.NfDeploymentId, event.FromState, event.ToState))


def handle_nfdeployment_statechanged(
    cmd: commands.HandleNfDeploymentStateChanged,
    uow: AbstractUnitOfWork
):
    if cmd.FromState == NfDeploymentState.Initial:
        if cmd.ToState == NfDeploymentState.Installing:
            cmd2 = commands.InstallNfDeployment(cmd.NfDeploymentId)
            install_nfdeployment(cmd2, uow)
        elif cmd.ToState == NfDeploymentState.Deleting:
            cmd2 = commands.DeleteNfDeployment(cmd.NfDeploymentId)
            delete_nfdeployment(cmd2, uow)
        else:
            logger.debug("Not insterested state change: {}".format(cmd))
    elif cmd.FromState == NfDeploymentState.Installed \
            or cmd.FromState == NfDeploymentState.Installing \
            or cmd.FromState == NfDeploymentState.Updating \
            or cmd.FromState == NfDeploymentState.Abnormal:

        if cmd.ToState == NfDeploymentState.Uninstalling:
            cmd2 = commands.UninstallNfDeployment(cmd.NfDeploymentId)
            uninstall_nfdeployment(cmd2, uow)
        else:
            logger.debug("Not insterested state change: {}".format(cmd))
    elif cmd.FromState == NfDeploymentState.Abnormal:
        if cmd.ToState == NfDeploymentState.Deleting:
            # cmd2 = commands.UninstallNfDeployment(cmd.NfDeploymentId)
            # uninstall_nfdeployment(cmd2, uow)
            cmd2 = commands.DeleteNfDeployment(cmd.NfDeploymentId)
            delete_nfdeployment(cmd2, uow)
        else:
            logger.debug("Not insterested state change: {}".format(cmd))
    else:
        logger.debug("Not insterested state change: {}".format(cmd))


# retry 10 seconds
@retry(
    (NfdeploymentNotFoundError),
    tries=100,
    delay=2, max_delay=10000, backoff=1)
def _retry_get_nfdeployment(
        cmd: commands.InstallNfDeployment,
        uow: AbstractUnitOfWork):
    nfdeployment: NfDeployment = uow.nfdeployments.get(
        cmd.NfDeploymentId)
    if nfdeployment is None:
        raise NfdeploymentNotFoundError(
            "Cannot find NfDeployment: {}".format(
                cmd.NfDeploymentId))
    return nfdeployment


def install_nfdeployment(
    cmd: commands.InstallNfDeployment,
    uow: AbstractUnitOfWork
):
    logger.info("install with NfDeploymentId: {}".format(
        cmd.NfDeploymentId))
    nfdeployment: NfDeployment = _retry_get_nfdeployment(cmd, uow)
    if nfdeployment is None:
        raise Exception("Cannot find NfDeployment: {}".format(
            cmd.NfDeploymentId))
    # get nfdeploymentdescriptor by descriptorId
    desc: NfDeploymentDesc = uow.nfdeployment_descs.get(
        nfdeployment.descriptorId)
    if desc is None:
        raise Exception(
            "Cannot find NfDeploymentDescriptor:{} for NfDeployment:{}".format(
                nfdeployment.descriptorId, nfdeployment.id
            ))

    nfdeployment.set_state(NfDeploymentState.Installing)

    # Gen kube config file and set the path
    dms = uow.deployment_managers.get(nfdeployment.deploymentManagerId)
    dms_res = dms.serialize()
    p = dms_res.pop("profile", None)
    k8sconf_path = _get_kube_config_path(nfdeployment.deploymentManagerId, p)

    # helm repo add
    repourl = desc.artifactRepoUrl
    helm = Helm(logger, LOCAL_HELM_BIN, environment_variables={})
    repoName = None
    try:
        repolist = helm.repo_list()
        for repo in repolist:
            if repo['url'] == repourl:
                repoName = repo['name']
                break
    except Exception:
        # repoExisted
        repoName = None

    if not repoName:
        repoName = "repo4{}".format(nfdeployment.name)
        logger.debug("Trying to add repo:{}".format(repourl))
        helm.repo_add(repoName, repourl)
    helm.repo_update(None)

    repolist = helm.repo_list()
    logger.debug('repo list:{}'.format(repolist))

    # helm install name chart
    values_file_path = '/tmp/override_{}.yaml'.format(nfdeployment.name)
    if len(desc.inputParams) > 0:
        logger.info("dump override yaml:{}".format(values_file_path))
        values = json.loads(desc.inputParams)
        _create_values_file(values_file_path, values)
    else:
        values_file_path = None

    logger.debug('Try to helm install {}/{} {} -f {}'.format(
        repoName, nfdeployment.name, desc.artifactName, values_file_path))
    tokens = desc.artifactName.split(':')
    chartname = tokens[0]
    myflags = None
    # if (len(tokens) > 1):
    #     myflags = {"name": "version", "value": tokens[1]}
    result = helm.install(
        nfdeployment.name, "{}/{}".format(repoName, chartname), flags=myflags,
        values_file=values_file_path, kubeconfig=k8sconf_path)
    # token=K8S_TOKEN, apiserver=K8S_APISERVER)
    logger.debug('result: {}'.format(result))

    # in case success
    with uow:
        entity: NfDeployment = uow.nfdeployments.get(cmd.NfDeploymentId)
        if entity:
            entity.set_state(NfDeploymentState.Installed)
            entity.transit_state(NfDeploymentState.Installed)
        uow.commit()


def _create_values_file(filePath: str, content: dict):
    with open(filePath, "w", encoding="utf-8") as f:
        yaml.dump(content, f)


def uninstall_nfdeployment(
    cmd: commands.UninstallNfDeployment,
    uow: AbstractUnitOfWork
):
    logger.info("uninstall with NfDeploymentId: {}".format(
        cmd.NfDeploymentId))
    nfdeployment: NfDeployment = _retry_get_nfdeployment(cmd, uow)
    if nfdeployment is None:
        raise Exception("Cannot find NfDeployment: {}".format(
            cmd.NfDeploymentId))
    # get nfdeploymentdescriptor by descriptorId
    desc: NfDeploymentDesc = uow.nfdeployment_descs.get(
        nfdeployment.descriptorId)
    if desc is None:
        raise Exception(
            "Cannot find NfDeploymentDescriptor:{} for NfDeployment:{}".format(
                nfdeployment.descriptorId, nfdeployment.id
            ))

    with uow:
        entity: NfDeployment = uow.nfdeployments.get(cmd.NfDeploymentId)
        if entity:
            entity.set_state(NfDeploymentState.Uninstalling)
        uow.commit()

    # Gen kube config file and set the path
    dms = uow.deployment_managers.get(nfdeployment.deploymentManagerId)
    dms_res = dms.serialize()
    p = dms_res.pop("profile", None)
    k8sconf_path = _get_kube_config_path(nfdeployment.deploymentManagerId, p)

    helm = Helm(logger, LOCAL_HELM_BIN, environment_variables={})

    logger.debug('Try to helm del {}'.format(
        nfdeployment.name))
    myflags = None
    # if (len(tokens) > 1):
    #     myflags = {"name": "version", "value": tokens[1]}
    result = helm.uninstall(
        nfdeployment.name, flags=myflags,
        kubeconfig=k8sconf_path,)
    # token=K8S_TOKEN, apiserver=K8S_APISERVER)
    logger.debug('result: {}'.format(result))

    # in case success

    with uow:
        entity: NfDeployment = uow.nfdeployments.get(cmd.NfDeploymentId)
        if entity:
            entity.set_state(NfDeploymentState.Initial)
            entity.transit_state(NfDeploymentState.Deleting)
        # uow.nfdeployments.update(
        #     cmd.NfDeploymentId, status=NfDeploymentState.Initial)
        uow.commit()


def delete_nfdeployment(
    cmd: commands.UninstallNfDeployment,
    uow: AbstractUnitOfWork
):
    logger.info("delete with NfDeploymentId: {}".format(
        cmd.NfDeploymentId))

    # nfdeployment: NfDeployment = _retry_get_nfdeployment(cmd, uow)
    with uow:
        uow.nfdeployments.delete(cmd.NfDeploymentId)
        uow.commit()


def _get_kube_config_path(dmId: str, kubeconfig: dict) -> dict:

    # TODO: update this kube file for each DMS k8s when it changes.

    link_file_path = '/tmp/kubeconfig_' + dmId
    if os.path.exists(link_file_path) and \
            os.path.exists(os.readlink(link_file_path)):
        return link_file_path

    # Generate a random key for tmp kube config file
    letters = string.ascii_uppercase
    random_key = ''.join(random.choice(letters) for i in range(10))

    # Get datetime of now as tag of the tmp file
    current_time = datetime.now().strftime("%Y%m%d%H%M%S")
    tmp_file_name = random_key + "_" + current_time
    tmp_file_path = '/tmp/kubeconfig_' + tmp_file_name

    data = config.gen_k8s_config_dict(
        kubeconfig.pop('cluster_api_endpoint', None),
        kubeconfig.pop('cluster_ca_cert', None),
        kubeconfig.pop('admin_user', None),
        kubeconfig.pop('admin_client_cert', None),
        kubeconfig.pop('admin_client_key', None),
    )

    # write down the yaml file of kubectl into tmp folder
    with open(tmp_file_path, 'w') as file:
        yaml.dump(data, file)

    # os.symlink(tmp_file_path, link_file_path)
    os.symlink(tmp_file_path, '/tmp/tmp_'+tmp_file_name)
    os.rename('/tmp/tmp_'+tmp_file_name, link_file_path)
    if os.path.realpath(link_file_path) != tmp_file_path:
        # Symlink was updated failed
        logger.error('symlink update failed')

    return link_file_path
