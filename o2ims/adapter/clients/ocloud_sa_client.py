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

# client talking to Stx standalone

import uuid
from o2ims.service.client.base_client import BaseClient
from typing import List
# Optional,  Set
from o2ims.domain import stx_object as ocloudModel
from o2ims import config
from o2ims.domain.resource_type import ResourceTypeEnum

# from dcmanagerclient.api import client
from cgtsclient.client import get_client
import logging
logger = logging.getLogger(__name__)


class StxSaOcloudClient(BaseClient):
    def __init__(self, driver=None):
        super().__init__()
        self.driver = driver if driver else StxSaClientImp()

    # def list(self) -> List[ocloudModel.StxGenericModel]:
    #     return self._list()

    # def get(self, id) -> ocloudModel.StxGenericModel:
    #     return self._get(id)

    def _get(self, id) -> ocloudModel.StxGenericModel:
        return self.driver.getInstanceInfo()

    def _list(self):
        return [self.driver.getInstanceInfo()]


class StxSaResourcePoolClient(BaseClient):
    def __init__(self):
        super().__init__()
        self.driver = StxSaClientImp()

    def _get(self, id) -> ocloudModel.StxGenericModel:
        return self.driver.getInstanceInfo()

    def _list(self):
        return [self.driver.getInstanceInfo()]


class StxSaDmsClient(BaseClient):
    def __init__(self):
        super().__init__()
        self.driver = StxSaClientImp()

    def _get(self, name) -> ocloudModel.StxGenericModel:
        return self.driver.getK8sDetail(name)

    def _list(self):
        return self.driver.getK8sList()


class StxPserverClient(BaseClient):
    def __init__(self):
        super().__init__()
        self.driver = StxSaClientImp()

    def _get(self, id) -> ocloudModel.StxGenericModel:
        return self.driver.getPserver(id)

    def _list(self) -> List[ocloudModel.StxGenericModel]:
        return self.driver.getPserverList()


class StxCpuClient(BaseClient):
    def __init__(self, pserver_id):
        super().__init__()
        self._pserver_id = pserver_id
        self.driver = StxSaClientImp()

    def _get(self, id) -> ocloudModel.StxGenericModel:
        return self.driver.getCpu(id)

    def _list(self) -> List[ocloudModel.StxGenericModel]:
        return self.driver.getCpuList(self._pserver_id)

# internal driver which implement client call to Stx Standalone instance


class StxSaClientImp(object):
    def __init__(self, stx_client=None):
        super().__init__()
        self.stxclient = stx_client if stx_client else self.getStxClient()

    def getStxClient(self):
        os_client_args = config.get_stx_access_info()
        config_client = get_client(**os_client_args)
        return config_client

    def getInstanceInfo(self) -> ocloudModel.StxGenericModel:
        systems = self.stxclient.isystem.list()
        logger.debug("systems:" + str(systems[0].to_dict()))
        return ocloudModel.StxGenericModel(
            ResourceTypeEnum.OCLOUD, systems[0]) if systems else None

    def getPserverList(self) -> List[ocloudModel.StxGenericModel]:
        hosts = self.stxclient.ihost.list()
        logger.debug("host 1:" + str(hosts[0].to_dict()))
        return [ocloudModel.StxGenericModel(
            ResourceTypeEnum.PSERVER, self._hostconverter(host))
                for host in hosts if host]

    def getPserver(self, id) -> ocloudModel.StxGenericModel:
        host = self.stxclient.ihost.get(id)
        logger.debug("host:" + str(host.to_dict()))
        return ocloudModel.StxGenericModel(
            ResourceTypeEnum.PSERVER, self._hostconverter(host))

    def getK8sList(self) -> List[ocloudModel.StxGenericModel]:
        k8sclusters = self.stxclient.kube_cluster.list()
        logger.debug("k8sresources[0]:" + str(k8sclusters[0].to_dict()))
        return [ocloudModel.StxGenericModel(
            ResourceTypeEnum.DMS,
            self._k8sconverter(k8sres), self._k8shasher(k8sres))
            for k8sres in k8sclusters if k8sres]

    def getK8sDetail(self, name) -> ocloudModel.StxGenericModel:
        if not name:
            k8sclusters = self.stxclient.kube_cluster.list()
            # logger.debug("k8sresources[0]:" + str(k8sclusters[0].to_dict()))
            k8scluster = k8sclusters.pop()
        else:
            k8scluster = self.stxclient.kube_cluster.get(name)

        if not k8scluster:
            return None
        logger.debug("k8sresource:" + str(k8scluster.to_dict()))
        return ocloudModel.StxGenericModel(
            ResourceTypeEnum.DMS,
            self._k8sconverter(k8scluster), self._k8shasher(k8scluster))

    def getCpuList(self, hostid) -> List[ocloudModel.StxGenericModel]:
        cpulist = self.stxclient.icpu.list(hostid)
        return [ocloudModel.StxGenericModel(
            ResourceTypeEnum.OCLOUD,
            self._cpuconverter(cpures)) for cpures in cpulist if cpures]

    def getCpu(self, id) -> ocloudModel.StxGenericModel:
        cpuinfo = self.stxclient.icpu.get(id)
        return ocloudModel.StxGenericModel(
            ResourceTypeEnum.OCLOUD, self._cpuconverter(cpuinfo))

    def _getIsystems(self):
        return self.stxclient.isystem.list()

    def _getIsystem(self, id=None):
        if id:
            return self.stxclient.isystem.get(id)
        else:
            isystems = self.stxclient.isystem.list()
            if len(isystems) != 1 and not id:
                raise Exception('No system uuid was provided and '
                                'more than one system exists in the account.')
            return isystems[0]

    @staticmethod
    def _hostconverter(host):
        setattr(host, "name", host.hostname)
        return host

    @staticmethod
    def _cpuconverter(cpu):
        setattr(cpu, "name", "core-"+str(cpu.core))
        return cpu

    @staticmethod
    def _k8sconverter(cluster):
        setattr(cluster, "name", cluster.cluster_name)
        setattr(cluster, "uuid",
                uuid.uuid3(uuid.NAMESPACE_URL, cluster.cluster_name))
        setattr(cluster, 'updated_at', None)
        setattr(cluster, 'created_at', None)
        logger.debug("k8s cluster name/uuid:" +
                     cluster.name + "/" + str(cluster.uuid))
        return cluster

    @staticmethod
    def _k8shasher(cluster):
        return str(hash((cluster.cluster_name,
                         cluster.cluster_api_endpoint, cluster.admin_user)))
