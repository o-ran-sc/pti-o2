# Copyright (C) 2022 Wind River Systems, Inc.
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
from cgtsclient.client import get_client as get_stx_client
from cgtsclient.exc import EndpointException
from dcmanagerclient.api.client import client as get_dc_client

from o2common.helper import o2logging
logger = o2logging.get_logger(__name__)


CGTSCLIENT_ENDPOINT_ERROR_MSG = \
    'Must provide Keystone credentials or user-defined endpoint and token'


class StxOcloudClient(BaseClient):
    def __init__(self, driver=None):
        super().__init__()
        self.driver = driver if driver else StxClientImp()

    def _get(self, id) -> ocloudModel.StxGenericModel:
        return self.driver.getInstanceInfo()

    def _list(self, **filters):
        return [self.driver.getInstanceInfo()]

    def _set_stx_client(self):
        pass


class StxResourcePoolClient(BaseClient):
    def __init__(self):
        super().__init__()
        self.driver = StxClientImp()

    def _get(self, id) -> ocloudModel.StxGenericModel:
        return self.driver.getResourcePoolDetail(id)

    def _list(self, **filters):
        return self.driver.getResourcePoolList(**filters)

    def _set_stx_client(self):
        pass


class StxDmsClient(BaseClient):
    def __init__(self):
        super().__init__()
        self.driver = StxClientImp()

    def _get(self, name) -> ocloudModel.StxGenericModel:
        return self.driver.getK8sDetail(name)

    def _list(self, **filters):
        return self.driver.getK8sList(**filters)

    def _set_stx_client(self):
        pass


class StxPserverClient(BaseClient):
    def __init__(self):
        super().__init__()
        self.driver = StxClientImp()

    def _get(self, id) -> ocloudModel.StxGenericModel:
        return self.driver.getPserver(id)

    def _list(self, **filters) -> List[ocloudModel.StxGenericModel]:
        filters['resourcepoolid']
        return self.driver.getPserverList(**filters)

    def _set_stx_client(self):
        self.driver.setStxClient(self._pool_id)


class StxCpuClient(BaseClient):
    def __init__(self):
        super().__init__()
        # self._pserver_id = pserver_id
        self.driver = StxClientImp()

    def _get(self, id) -> ocloudModel.StxGenericModel:
        return self.driver.getCpu(id)

    def _list(self, **filters) -> List[ocloudModel.StxGenericModel]:
        return self.driver.getCpuList(**filters)

    def _set_stx_client(self):
        self.driver.setStxClient(self._pool_id)


class StxMemClient(BaseClient):
    def __init__(self):
        super().__init__()
        self.driver = StxClientImp()

    def _get(self, id) -> ocloudModel.StxGenericModel:
        return self.driver.getMem(id)

    def _list(self, **filters) -> List[ocloudModel.StxGenericModel]:
        return self.driver.getMemList(**filters)

    def _set_stx_client(self):
        self.driver.setStxClient(self._pool_id)


class StxEthClient(BaseClient):
    def __init__(self):
        super().__init__()
        self.driver = StxClientImp()

    def _get(self, id) -> ocloudModel.StxGenericModel:
        return self.driver.getEthernet(id)

    def _list(self, **filters) -> List[ocloudModel.StxGenericModel]:
        return self.driver.getEthernetList(**filters)

    def _set_stx_client(self):
        self.driver.setStxClient(self._pool_id)


class StxIfClient(BaseClient):
    def __init__(self):
        super().__init__()
        self.driver = StxClientImp()

    def _get(self, id) -> ocloudModel.StxGenericModel:
        return self.driver.getIf(id)

    def _list(self, **filters) -> List[ocloudModel.StxGenericModel]:
        return self.driver.getIfList(**filters)

    def _set_stx_client(self):
        self.driver.setStxClient(self._pool_id)


class StxIfPortClient(BaseClient):
    def __init__(self):
        super().__init__()
        self.driver = StxClientImp()

    def _get(self, id) -> ocloudModel.StxGenericModel:
        return self.driver.getPort(id)

    def _list(self, **filters) -> List[ocloudModel.StxGenericModel]:
        return self.driver.getPortList(**filters)

    def _set_stx_client(self):
        self.driver.setStxClient(self._pool_id)


class StxDevClient(BaseClient):
    def __init__(self):
        super().__init__()
        self.driver = StxClientImp()

    def _get(self, id) -> ocloudModel.StxGenericModel:
        return self.driver.getDevice(id)

    def _list(self, **filters) -> List[ocloudModel.StxGenericModel]:
        return self.driver.getDeviceList(**filters)

    def _set_stx_client(self):
        self.driver.setStxClient(self._pool_id)


class StxAccClient(BaseClient):
    def __init__(self):
        super().__init__()
        self.driver = StxClientImp()

    def _get(self, id) -> ocloudModel.StxGenericModel:
        return self.driver.getAccelerator(id)

    def _list(self, **filters) -> List[ocloudModel.StxGenericModel]:
        return self.driver.getAcceleratorList(**filters)

    def _set_stx_client(self):
        self.driver.setStxClient(self._pool_id)


# internal driver which implement client call to Stx Standalone and DC instance
class StxClientImp(object):
    def __init__(self, stx_client=None, dc_client=None):
        super().__init__()
        self.stxclient = stx_client if stx_client else self.getStxClient()
        self.dcclient = dc_client if dc_client else self.getDcmanagerClient()
        # if subcloud_id is not None:
        # self.stxclient = self.getSubcloudClient(subcloud_id)

    def getStxClient(self):
        os_client_args = config.get_stx_access_info()
        config_client = get_stx_client(**os_client_args)
        return config_client

    def getDcmanagerClient(self):
        os_client_args = config.get_dc_access_info()
        config_client = get_dc_client(**os_client_args)
        return config_client

    def getSubcloudClient(self, subcloud_id):
        subcloud = self.dcclient.subcloud_manager.\
            subcloud_additional_details(subcloud_id)
        logger.debug('subcloud name: %s, oam_floating_ip: %s' %
                     (subcloud[0].name, subcloud[0].oam_floating_ip))
        try:
            os_client_args = config.get_stx_access_info(
                region_name=subcloud[0].name,
                subcloud_hostname=subcloud[0].oam_floating_ip)
            logger.info(os_client_args)
            config_client = get_stx_client(**os_client_args)
        except EndpointException as e:
            msg = e.format_message()
            if CGTSCLIENT_ENDPOINT_ERROR_MSG in msg:
                os_client_args = config.get_stx_access_info(
                    region_name=subcloud[0].name, sub_is_https=True,
                    subcloud_hostname=subcloud[0].oam_floating_ip)
                logger.info(os_client_args)
                config_client = get_stx_client(**os_client_args)
            else:
                raise ValueError('Stx endpoint exception: %s' % msg)
        except Exception:
            raise ValueError('cgtsclient get subcloud client failed')

        return config_client

    def setStxClient(self, resource_pool_id):
        systems = self.stxclient.isystem.list()
        if resource_pool_id == systems[0].uuid:
            logger.debug('Stx Client not change: %s' % resource_pool_id)
            return

        subclouds = self.getSubcloudList()
        for subcloud in subclouds:
            subcloud_stxclient = self.getSubcloudClient(subcloud.subcloud_id)
            systems = subcloud_stxclient.isystem.list()
            # logger.debug('subcloud %s id: %s' %
            #  (systems[0].name, systems[0].uuid))
            # logger.debug('subcloud: %s' % (systems[0].to_dict()))
            if resource_pool_id == systems[0].uuid:
                self.stxclient = subcloud_stxclient

    def getInstanceInfo(self) -> ocloudModel.StxGenericModel:
        systems = self.stxclient.isystem.list()
        logger.debug('systems:' + str(systems[0].to_dict()))
        # logger.debug('systems[0] uuid: ' + str(systems[0].uuid))
        return ocloudModel.StxGenericModel(
            ResourceTypeEnum.OCLOUD, systems[0]) if systems else None

    def getSubcloudList(self):
        subs = self.dcclient.subcloud_manager.list_subclouds()
        known_subs = [sub for sub in subs if sub.sync_status != 'unknown']
        return known_subs

    def getResourcePoolList(self, **filters) -> List[
            ocloudModel.StxGenericModel]:
        systems = self.stxclient.isystem.list()
        logger.debug('system controller distributed_cloud_role:' +
                     str(systems[0].distributed_cloud_role))

        if systems[0].distributed_cloud_role is None or \
                systems[0].distributed_cloud_role != 'systemcontroller':
            return [ocloudModel.StxGenericModel(
                ResourceTypeEnum.RESOURCE_POOL,
                self._respoolconverter(systems[0]))]

        pools = []
        if config.get_system_controller_as_respool():
            pools.append(systems[0])

        subclouds = self.getSubcloudList()
        logger.debug('subclouds numbers: %s' % len(subclouds))
        for subcloud in subclouds:
            try:
                subcloud_stxclient = self.getSubcloudClient(
                    subcloud.subcloud_id)
                systems = subcloud_stxclient.isystem.list()
                logger.debug('systems:' + str(systems[0].to_dict()))
                pools.append(systems[0])
            except Exception as ex:
                logger.warning('Failed get cgstclient of subcloud %s: %s' %
                               (subcloud.name, ex))
                continue

        return [ocloudModel.StxGenericModel(
            ResourceTypeEnum.RESOURCE_POOL,
                self._respoolconverter(
                    respool)) for respool in pools if respool]

    def getResourcePoolDetail(self, id):
        self.setStxClient(id)
        systems = self.stxclient.isystem.list()
        logger.debug('systems:' + str(systems[0].to_dict()))
        return ocloudModel.StxGenericModel(
            ResourceTypeEnum.RESOURCE_POOL, systems[0]) if systems else None

    def getPserverList(self, **filters) -> List[ocloudModel.StxGenericModel]:
        hosts = self.stxclient.ihost.list()
        logger.debug('host 1:' + str(hosts[0].to_dict()))
        return [ocloudModel.StxGenericModel(
            ResourceTypeEnum.PSERVER, self._hostconverter(host))
            for host in hosts if host and (host.availability == 'available'
                                           or host.availability == 'degraded')]

    def getPserver(self, id) -> ocloudModel.StxGenericModel:
        host = self.stxclient.ihost.get(id)
        logger.debug('host:' + str(host.to_dict()))
        return ocloudModel.StxGenericModel(
            ResourceTypeEnum.PSERVER, self._hostconverter(host))

    def getK8sList(self, **filters) -> List[ocloudModel.StxGenericModel]:
        systems = self.stxclient.isystem.list()
        logger.debug('system controller distributed_cloud_role:' +
                     str(systems[0].distributed_cloud_role))

        if systems[0].distributed_cloud_role is None or \
                systems[0].distributed_cloud_role != 'systemcontroller':
            k8sclusters = self.stxclient.kube_cluster.list()
            setattr(k8sclusters[0], 'cloud_name', systems[0].name)
            logger.debug('k8sresources[0]:' + str(k8sclusters[0].to_dict()))
            # logger.debug('k8sresources[0] cluster_api_endpoint: ' +
            #  str(k8sclusters[0].cluster_api_endpoint))
            return [ocloudModel.StxGenericModel(
                ResourceTypeEnum.DMS,
                self._k8sconverter(k8sres), self._k8shasher(k8sres))
                for k8sres in k8sclusters if k8sres]

        k8s_list = []
        if config.get_system_controller_as_respool():
            k8sclusters = self.stxclient.kube_cluster.list()
            setattr(k8sclusters[0], 'cloud_name', systems[0].name)
            logger.debug('k8sresources[0]:' + str(k8sclusters[0].to_dict()))
            # logger.debug('k8sresources[0] cluster_api_endpoint: ' +
            #  str(k8sclusters[0].cluster_api_endpoint))
            k8s_list.append(k8sclusters[0])

        subclouds = self.getSubcloudList()
        logger.debug('subclouds numbers: %s' % len(subclouds))
        for subcloud in subclouds:
            try:
                subcloud_stxclient = self.getSubcloudClient(
                    subcloud.subcloud_id)
                systems = subcloud_stxclient.isystem.list()
                k8sclusters = subcloud_stxclient.kube_cluster.list()
                setattr(k8sclusters[0], 'cloud_name', systems[0].name)
                logger.debug('k8sresources[0]:' +
                             str(k8sclusters[0].to_dict()))
                # logger.debug('k8sresources[0] cluster_api_endpoint: ' +
                #  str(k8sclusters[0].cluster_api_endpoint))
                k8s_list.append(k8sclusters[0])
            except Exception as ex:
                logger.warning('Failed get cgstclient of subcloud %s: %s' %
                               (subcloud.name, ex))
                continue

        return [ocloudModel.StxGenericModel(ResourceTypeEnum.DMS,
                self._k8sconverter(k8sres), self._k8shasher(k8sres))
                for k8sres in k8s_list if k8sres]

    def getK8sDetail(self, name) -> ocloudModel.StxGenericModel:
        systems = self.stxclient.isystem.list()
        if not name:
            k8sclusters = self.stxclient.kube_cluster.list()
            # logger.debug("k8sresources[0]:" + str(k8sclusters[0].to_dict()))
            setattr(k8sclusters[0], 'cloud_name', systems[0].name)
            k8scluster = k8sclusters.pop()
        else:
            sname = name.split('.')
            cloud_name = '.'.join(sname[:-1])
            k8s_name = sname[-1]
            if cloud_name == systems[0].name:
                k8scluster = self.stxclient.kube_cluster.get(k8s_name)
                setattr(k8scluster, 'cloud_name', cloud_name)
            else:
                subclouds = self.getSubcloudList()
                subcloud_id = [
                    sub.subcloud_id for sub in subclouds
                    if sub.name == cloud_name][0]
                subcloud_stxclient = self.getSubcloudClient(subcloud_id)
                k8scluster = subcloud_stxclient.kube_cluster.get(k8s_name)
                setattr(k8scluster, 'cloud_name', cloud_name)
                # logger.debug('k8sresources[0]:' +
                #  str(k8sclusters[0].to_dict()))
                # logger.debug('k8sresources[0] cluster_api_endpoint: ' +
                #  str(k8sclusters[0].cluster_api_endpoint))

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

    def getDeviceList(self, **filters) -> List[ocloudModel.StxGenericModel]:
        hostid = filters.get('hostid', None)
        assert (hostid is not None), 'missing hostid to query pci device list'
        pci_dev_list = self.stxclient.pci_device.list(hostid)
        return [ocloudModel.StxGenericModel(
            ResourceTypeEnum.PSERVER_PCI_DEV,
            self._devconverter(pci_dev))
            for pci_dev in pci_dev_list if pci_dev]

    def getDevice(self, id) -> ocloudModel.StxGenericModel:
        pciinfo = self.stxclient.pci_device.get(id)
        return ocloudModel.StxGenericModel(
            ResourceTypeEnum.PSERVER_PCI_DEV, self._devconverter(pciinfo))

    def getAcceleratorList(self, **filters) -> \
            List[ocloudModel.StxGenericModel]:
        hostid = filters.get('hostid', None)
        assert (hostid is not None), 'missing hostid to query accelerator list'
        pci_dev_list = self.stxclient.pci_device.list(hostid)
        acc_list = []
        for pci_dev in pci_dev_list:
            if pci_dev.pvendor_id in ['8086']:
                if pci_dev.pdevice_id in ['0d5c', '0d5d']:
                    logger.info('Accelerator vendor ID: {}, device ID: {}'.
                                format(pci_dev.pvendor_id, pci_dev.pdevice_id))
                    acc_list.append(ocloudModel.StxGenericModel(
                        ResourceTypeEnum.PSERVER_ACC,
                        self._devconverter(pci_dev)))
        return acc_list

    def getAccelerator(self, id) -> ocloudModel.StxGenericModel:
        pciinfo = self.stxclient.pci_device.get(id)
        return ocloudModel.StxGenericModel(
            ResourceTypeEnum.PSERVER_ACC, self._devconverter(pciinfo))

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
    def _respoolconverter(res_pool):
        setattr(res_pool, 'name', res_pool.region_name)
        return res_pool

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
    def _devconverter(dev):
        setattr(dev, 'name', dev.host_uuid.split('-', 1)[0] + '-'+dev.name)
        return dev

    @ staticmethod
    def _k8sconverter(cluster):
        setattr(cluster, 'name', cluster.cloud_name +
                '.' + cluster.cluster_name)
        setattr(cluster, 'uuid',
                uuid.uuid3(uuid.NAMESPACE_URL, cluster.name))
        setattr(cluster, 'updated_at', None)
        setattr(cluster, 'created_at', None)
        setattr(cluster, 'events', [])
        logger.debug('k8s cluster name/uuid:' +
                     cluster.name + '/' + str(cluster.uuid))
        return cluster

    @ staticmethod
    def _k8shasher(cluster):
        return str(hash((cluster.cluster_name, cluster.cloud_name,
                         cluster.cluster_api_endpoint, cluster.admin_user)))
