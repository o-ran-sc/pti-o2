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
from o2common.service.client.base_client import BaseClient
from typing import List
# Optional,  Set
from o2ims.domain import stx_object as ocloudModel
from o2common.config import config
from o2ims.domain.resource_type import ResourceTypeEnum

# from dcmanagerclient.api import client
from cgtsclient.client import get_client

from o2common.helper import o2logging
logger = o2logging.get_logger(__name__)


class StxSaOcloudClient(BaseClient):
    def __init__(self, driver=None):
        super().__init__()
        self.driver = driver if driver else StxSaClientImp()

    def _get(self, id) -> ocloudModel.StxGenericModel:
        return self.driver.getInstanceInfo()

    def _list(self, **filters):
        return [self.driver.getInstanceInfo()]


class StxSaResourcePoolClient(BaseClient):
    def __init__(self):
        super().__init__()
        self.driver = StxSaClientImp()

    def _get(self, id) -> ocloudModel.StxGenericModel:
        return self.driver.getInstanceInfo()

    def _list(self, **filters):
        return [self.driver.getInstanceInfo()]


class StxSaDmsClient(BaseClient):
    def __init__(self):
        super().__init__()
        self.driver = StxSaClientImp()

    def _get(self, name) -> ocloudModel.StxGenericModel:
        return self.driver.getK8sDetail(name)

    def _list(self, **filters):
        return self.driver.getK8sList(**filters)


class StxPserverClient(BaseClient):
    def __init__(self):
        super().__init__()
        self.driver = StxSaClientImp()

    def _get(self, id) -> ocloudModel.StxGenericModel:
        return self.driver.getPserver(id)

    def _list(self, **filters) -> List[ocloudModel.StxGenericModel]:
        return self.driver.getPserverList(**filters)


class StxCpuClient(BaseClient):
    def __init__(self):
        super().__init__()
        # self._pserver_id = pserver_id
        self.driver = StxSaClientImp()

    def _get(self, id) -> ocloudModel.StxGenericModel:
        return self.driver.getCpu(id)

    def _list(self, **filters) -> List[ocloudModel.StxGenericModel]:
        return self.driver.getCpuList(**filters)


class StxMemClient(BaseClient):
    def __init__(self):
        super().__init__()
        self.driver = StxSaClientImp()

    def _get(self, id) -> ocloudModel.StxGenericModel:
        return self.driver.getMem(id)

    def _list(self, **filters) -> List[ocloudModel.StxGenericModel]:
        return self.driver.getMemList(**filters)


class StxEthClient(BaseClient):
    def __init__(self):
        super().__init__()
        self.driver = StxSaClientImp()

    def _get(self, id) -> ocloudModel.StxGenericModel:
        return self.driver.getEthernet(id)

    def _list(self, **filters) -> List[ocloudModel.StxGenericModel]:
        return self.driver.getEthernetList(**filters)


class StxIfClient(BaseClient):
    def __init__(self):
        super().__init__()
        self.driver = StxSaClientImp()

    def _get(self, id) -> ocloudModel.StxGenericModel:
        return self.driver.getIf(id)

    def _list(self, **filters) -> List[ocloudModel.StxGenericModel]:
        return self.driver.getIfList(**filters)


class StxIfPortClient(BaseClient):
    def __init__(self):
        super().__init__()
        self.driver = StxSaClientImp()

    def _get(self, id) -> ocloudModel.StxGenericModel:
        return self.driver.getPort(id)

    def _list(self, **filters) -> List[ocloudModel.StxGenericModel]:
        return self.driver.getPortList(**filters)


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
        logger.debug('systems:' + str(systems[0].to_dict()))
        return ocloudModel.StxGenericModel(
            ResourceTypeEnum.OCLOUD, systems[0]) if systems else None

    def getPserverList(self, **filters) -> List[ocloudModel.StxGenericModel]:
        # resourcepoolid = filters.get("resourcepoolid", None)
        hosts = self.stxclient.ihost.list()
        logger.debug('host 1:' + str(hosts[0].to_dict()))
        return [ocloudModel.StxGenericModel(
            ResourceTypeEnum.PSERVER, self._hostconverter(host))
            for host in hosts if host and host.availability == 'available']

    def getPserver(self, id) -> ocloudModel.StxGenericModel:
        host = self.stxclient.ihost.get(id)
        logger.debug('host:' + str(host.to_dict()))
        return ocloudModel.StxGenericModel(
            ResourceTypeEnum.PSERVER, self._hostconverter(host))

    def getK8sList(self, **filters) -> List[ocloudModel.StxGenericModel]:
        k8sclusters = self.stxclient.kube_cluster.list()
        logger.debug('k8sresources[0]:' + str(k8sclusters[0].to_dict()))
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
        logger.debug('k8sresource:' + str(k8scluster.to_dict()))
        return ocloudModel.StxGenericModel(
            ResourceTypeEnum.DMS,
            self._k8sconverter(k8scluster), self._k8shasher(k8scluster))

    def getCpuList(self, **filters) -> List[ocloudModel.StxGenericModel]:
        hostid = filters.get('hostid', None)
        assert (hostid is not None), 'missing hostid to query icpu list'
        cpulist = self.stxclient.icpu.list(hostid)
        return [ocloudModel.StxGenericModel(
            ResourceTypeEnum.PSERVER_CPU,
            self._cpuconverter(cpures)) for cpures in cpulist if cpures]

    def getCpu(self, id) -> ocloudModel.StxGenericModel:
        cpuinfo = self.stxclient.icpu.get(id)
        return ocloudModel.StxGenericModel(
            ResourceTypeEnum.PSERVER_CPU, self._cpuconverter(cpuinfo))

    def getMemList(self, **filters) -> List[ocloudModel.StxGenericModel]:
        hostid = filters.get('hostid', None)
        assert (hostid is not None), 'missing hostid to query imem list'
        memlist = self.stxclient.imemory.list(hostid)
        return [ocloudModel.StxGenericModel(
            ResourceTypeEnum.PSERVER_RAM,
            self._memconverter(memories)) for memories in memlist if memories]

    def getMem(self, id) -> ocloudModel.StxGenericModel:
        meminfo = self.stxclient.imemory.get(id)
        return ocloudModel.StxGenericModel(
            ResourceTypeEnum.PSERVER_RAM, self._memconverter(meminfo))

    def getEthernetList(self, **filters) -> List[ocloudModel.StxGenericModel]:
        hostid = filters.get('hostid', None)
        assert (hostid is not None), 'missing hostid to query port list'
        ethlist = self.stxclient.ethernet_port.list(hostid)
        return [ocloudModel.StxGenericModel(
            ResourceTypeEnum.PSERVER_ETH,
            self._ethconverter(eth)) for eth in ethlist if eth]

    def getEthernet(self, id) -> ocloudModel.StxGenericModel:
        ethinfo = self.stxclient.ethernet_port.get(id)
        return ocloudModel.StxGenericModel(
            ResourceTypeEnum.PSERVER_ETH, self._ethconverter(ethinfo))

    def getIfList(self, **filters) -> List[ocloudModel.StxGenericModel]:
        hostid = filters.get('hostid', None)
        assert (hostid is not None), 'missing hostid to query iinterface list'
        iflist = self.stxclient.iinterface.list(hostid)
        return [ocloudModel.StxGenericModel(
            ResourceTypeEnum.PSERVER_IF,
            self._ifconverter(ifs)) for ifs in iflist if ifs]

    def getIf(self, id) -> ocloudModel.StxGenericModel:
        ifinfo = self.stxclient.iinterface.get(id)
        return ocloudModel.StxGenericModel(
            ResourceTypeEnum.PSERVER_IF, self._ifconverter(ifinfo))

    def getPortList(self, **filters) -> List[ocloudModel.StxGenericModel]:
        ifid = filters.get('interfaceid', None)
        assert (ifid is not None), 'missing interface id to query port list'
        portlist = self.stxclient.iinterface.list_ports(ifid)
        return [ocloudModel.StxGenericModel(
            ResourceTypeEnum.PSERVER_IF_PORT,
            port) for port in portlist if port]

    def getPort(self, id) -> ocloudModel.StxGenericModel:
        portinfo = self.stxclient.port.get(id)
        return ocloudModel.StxGenericModel(
            ResourceTypeEnum.PSERVER_IF_PORT, portinfo)

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

    @ staticmethod
    def _hostconverter(host):
        setattr(host, 'name', host.hostname)
        return host

    @ staticmethod
    def _cpuconverter(cpu):
        setattr(cpu, 'name', cpu.ihost_uuid.split(
            '-', 1)[0] + '-cpu-'+str(cpu.cpu))
        return cpu

    @ staticmethod
    def _memconverter(mem):
        setattr(mem, 'name', mem.ihost_uuid.split('-', 1)[0] +
                '-mem-node-'+str(mem.numa_node))
        return mem

    @ staticmethod
    def _ethconverter(eth):
        setattr(eth, 'name', eth.host_uuid.split('-', 1)[0] + '-'+eth.name)
        setattr(eth, 'updated_at', None)
        setattr(eth, 'created_at', None)
        return eth

    @ staticmethod
    def _ifconverter(ifs):
        setattr(ifs, 'name', ifs.ihost_uuid.split('-', 1)[0] + '-'+ifs.ifname)
        setattr(ifs, 'updated_at', None)
        setattr(ifs, 'created_at', None)
        return ifs

    @ staticmethod
    def _k8sconverter(cluster):
        setattr(cluster, 'name', cluster.cluster_name)
        setattr(cluster, 'uuid',
                uuid.uuid3(uuid.NAMESPACE_URL, cluster.cluster_name))
        setattr(cluster, 'updated_at', None)
        setattr(cluster, 'created_at', None)
        setattr(cluster, 'events', [])
        logger.debug('k8s cluster name/uuid:' +
                     cluster.name + '/' + str(cluster.uuid))
        return cluster

    @ staticmethod
    def _k8shasher(cluster):
        return str(hash((cluster.cluster_name,
                         cluster.cluster_api_endpoint, cluster.admin_user)))
