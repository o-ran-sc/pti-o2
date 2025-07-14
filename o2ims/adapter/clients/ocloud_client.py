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

import base64
import uuid
import json
from typing import List
# Optional,  Set

from cgtsclient.client import get_client as get_stx_client
from cgtsclient.exc import EndpointException
from dcmanagerclient.api.client import client as get_dc_client
from kubernetes import client as k8sclient, config as k8sconfig

from o2common.config import config
from o2common.service.client.base_client import BaseClient
from o2ims.domain import stx_object as ocloudModel
from o2ims.domain.resource_type import ResourceTypeEnum

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

    def _list(self, **filters) -> List[ocloudModel.StxGenericModel]:
        return [self.driver.getInstanceInfo()]

    def _set_stx_client(self):
        pass


class StxResourcePoolClient(BaseClient):
    def __init__(self):
        super().__init__()
        self.driver = StxClientImp()

    def _get(self, id) -> ocloudModel.StxGenericModel:
        return self.driver.getResourcePoolDetail(id)

    def _list(self, **filters) -> List[ocloudModel.StxGenericModel]:
        return self.driver.getResourcePoolList(**filters)

    def _set_stx_client(self):
        pass


class StxDmsClient(BaseClient):
    def __init__(self):
        super().__init__()
        self.driver = StxClientImp()

    def _get(self, name) -> ocloudModel.StxGenericModel:
        return self.driver.getK8sDetail(name)

    def _list(self, **filters) -> List[ocloudModel.StxGenericModel]:
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
        if subcloud[0].oam_floating_ip == 'unavailable':
            raise EnvironmentError(f"{subcloud[0].name} was unavailable")
        try:
            # Pass subcloud region name to get_region_name via
            # get_stx_access_info
            region_name = config.get_region_name(subcloud[0].region_name)
            os_client_args = config.get_stx_access_info(
                region_name=region_name,
                subcloud_hostname=subcloud[0].oam_floating_ip)
            config_client = get_stx_client(**os_client_args)
        except EndpointException as e:
            msg = e.format_message()
            if CGTSCLIENT_ENDPOINT_ERROR_MSG in msg:
                region_name = config.get_region_name(subcloud[0].region_name)
                os_client_args = config.get_stx_access_info(
                    region_name=region_name, sub_is_https=True,
                    subcloud_hostname=subcloud[0].oam_floating_ip)
                config_client = get_stx_client(**os_client_args)
            else:
                raise ValueError('Stx endpoint exception: %s' % msg)
        except Exception:
            raise ValueError('cgtsclient get subcloud client failed')

        return config_client

    def getK8sClient(self, k8scluster):
        def _b64_encode_str(msg: str, encode: str = 'utf-8') -> str:
            msg_bytes = msg.encode('utf-8')
            base64_bytes = base64.b64encode(msg_bytes)
            base64_msg = base64_bytes.decode('utf-8')
            return base64_msg

        conf_dict = config.gen_k8s_config_dict(
            k8scluster.cluster_api_endpoint,
            _b64_encode_str(k8scluster.cluster_ca_cert),
            k8scluster.admin_user,
            _b64_encode_str(k8scluster.admin_client_cert),
            _b64_encode_str(k8scluster.admin_client_key),
        )
        k8sconfig.load_kube_config_from_dict(conf_dict)
        v1 = k8sclient.CoreV1Api()
        return v1

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
        self.dcclient = self.getDcmanagerClient()
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
                logger.debug('subcloud system:' + str(systems[0].to_dict()))
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
            ResourceTypeEnum.RESOURCE_POOL,
            self._respoolconverter(systems[0])) if systems else None

    def getPserverList(self, **filters) -> List[ocloudModel.StxGenericModel]:
        hosts = self.stxclient.ihost.list()
        logger.debug('host 1:' + str(hosts[0].to_dict()))
        return [ocloudModel.StxGenericModel(
            ResourceTypeEnum.PSERVER, self._hostconverter(host))
            for host in hosts if host and (host.availability == 'available'
                                           or host.availability == 'online'
                                           or host.availability == 'degraded')]

    def getPserver(self, id) -> ocloudModel.StxGenericModel:
        host = self.stxclient.ihost.get(id)
        logger.debug('host:' + str(host.to_dict()))
        return ocloudModel.StxGenericModel(
            ResourceTypeEnum.PSERVER, self._hostconverter(host))

    def _checkLabelExistOnHost(self, client, label_to_check, host_id,
                               check_value=False) -> bool:
        labels = client.label.list(host_id)
        if check_value:
            return any(label_to_check['key'] == label.label_key and
                       label_to_check['value'] == label.label_value
                       for label in labels)
        else:
            return any(label_to_check['key'] == label.label_key
                       for label in labels)

    def _checkLabelExistOnCluster(self, client, label_to_check,
                                  check_value=False) -> bool:
        hosts = client.ihost.list()
        for host in hosts:
            if self._checkLabelExistOnHost(client, label_to_check,
                                           host.uuid, check_value):
                if check_value:
                    logger.info(
                        f"host {host.hostname} has the label "
                        f"{label_to_check['key']} with value "
                        f"{label_to_check['value']}")
                else:
                    logger.info(
                        f"host {host.hostname} has the label "
                        f"{label_to_check['key']}")
                return True
        return False

    def _getK8sNodes(self, k8sclient):
        return k8sclient.list_node()

    def _getK8sNodeDetail(self, k8sclient, node_name):
        return k8sclient.read_node(name=node_name)

    def _getK8sCapabilities(self, k8s_client):
        k8s_capabilities = {}
        nodes = self._getK8sNodes(k8s_client)
        for node in nodes.items:
            logger.debug(f'k8s node {node.metadata.name} allocatable: '
                         f'{node.status.allocatable}')
            for allocatable in node.status.allocatable:
                if allocatable.startswith('intel.com/pci_sriov_net_'):
                    k8s_capabilities[f'{node.metadata.name}_sriov'] = True
                if allocatable == 'windriver.com/isolcpus':
                    k8s_capabilities[f'{node.metadata.name}_isolcpus'] = True
        return k8s_capabilities

    def _setK8sCapabilities(self, k8scluster, client, k8s_client):
        capabilities = {}
        label_OS_2chk = {'key': 'OS', 'value': 'low_latency'}
        if self._checkLabelExistOnCluster(client, label_OS_2chk, True):
            logger.debug("low latency host inside of the k8s cluster")
            capabilities[label_OS_2chk['key']] = label_OS_2chk['value']

        # Add Kubernetes capabilities
        k8s_capabilities = self._getK8sCapabilities(k8s_client)
        capabilities.update(k8s_capabilities)

        setattr(k8scluster, 'capabilities', json.dumps(capabilities))
        return k8scluster

    def _getK8sCapacity(self, k8s_client):
        k8s_capacity = {}
        nodes = self._getK8sNodes(k8s_client)
        for node in nodes.items:
            logger.debug(f'k8s node {node.metadata.name} capacity: '
                         f'{node.status.capacity}')
            for key, value in node.status.capacity.items():
                k8s_capacity[f'{node.metadata.name}_{key}'] = value
        return k8s_capacity

    def _setK8sCapacity(self, k8scluster, client, k8s_client):
        capacity = {}

        # Add Kubernetes capacity
        k8s_capacity = self._getK8sCapacity(k8s_client)
        capacity.update(k8s_capacity)

        setattr(k8scluster, 'capacity', json.dumps(capacity))
        return k8scluster

    def getLabelList(self, **filters) -> List[ocloudModel.StxGenericModel]:
        hostid = filters.get('hostid', None)
        assert (hostid is not None), 'missing hostid to query label list'
        labels = self.stxclient.label.list(hostid)
        return [ocloudModel.StxGenericModel(
            ResourceTypeEnum.PSERVER_LABEL,
            self._labelconverter(label)) for label in labels if label]

    def getK8sList(self, **filters) -> List[ocloudModel.StxGenericModel]:
        def process_cluster(client, cluster):
            setattr(cluster, 'cloud_name', systems[0].name)
            setattr(cluster, 'cloud_uuid', systems[0].uuid)

            k8s_client = self.getK8sClient(cluster)
            cluster = self._setK8sCapabilities(cluster, client, k8s_client)
            cluster = self._setK8sCapacity(cluster, client, k8s_client)

            logger.debug('k8sresources cluster_api_endpoint: ' +
                         str(cluster.cluster_api_endpoint))
            return ocloudModel.StxGenericModel(ResourceTypeEnum.DMS,
                                               self._k8sconverter(cluster),
                                               self._k8shasher(cluster))

        systems = self.stxclient.isystem.list()
        distributed_cloud_role = systems[0].distributed_cloud_role
        logger.debug((
            f'system controller distributed_cloud_role: '
            f'{distributed_cloud_role}'))

        k8s_list = []

        if distributed_cloud_role is None or distributed_cloud_role != \
                'systemcontroller':
            k8s_list.extend(
                [process_cluster(self.stxclient, k8s)
                 for k8s in self.stxclient.kube_cluster.list() if k8s])
            return k8s_list

        if config.get_system_controller_as_respool():
            k8s_list.extend(
                [process_cluster(self.stxclient, k8s)
                 for k8s in self.stxclient.kube_cluster.list() if k8s])

        subclouds = self.getSubcloudList()
        logger.debug(f'subclouds numbers: {len(subclouds)}')

        for subcloud in subclouds:
            try:
                subcloud_stxclient = self.getSubcloudClient(
                    subcloud.subcloud_id)
                systems = subcloud_stxclient.isystem.list()
                k8sclusters = subcloud_stxclient.kube_cluster.list()
                k8s_list.extend([process_cluster(subcloud_stxclient, k8s)
                                for k8s in k8sclusters if k8s])
            except Exception as ex:
                logger.warning((
                    f'Failed to get cgstclient of subcloud '
                    f'{subcloud.name}: {ex}'))
                continue

        return k8s_list

    def getK8sDetail(self, name) -> ocloudModel.StxGenericModel:
        def process_k8s_cluster(client, k8s_cluster, cloud_name, cloud_uuid):
            setattr(k8s_cluster, 'cloud_name', cloud_name)
            setattr(k8s_cluster, 'cloud_uuid', cloud_uuid)

            k8s_client = self.getK8sClient(k8s_cluster)
            cluster = self._setK8sCapabilities(k8s_cluster, client, k8s_client)
            cluster = self._setK8sCapacity(cluster, client, k8s_client)
            return k8s_cluster

        systems = self.stxclient.isystem.list()
        system_name = systems[0].name
        system_uuid = systems[0].uuid

        if not name:
            k8s_clusters = self.stxclient.kube_cluster.list()
            k8s_cluster = process_k8s_cluster(
                self.stxclient, k8s_clusters.pop(), system_name)
        else:
            sname = name.split('.')
            cloud_name = '.'.join(sname[:-1])
            k8s_name = sname[-1]

            if cloud_name == system_name:
                k8s_cluster = process_k8s_cluster(
                    self.stxclient,
                    self.stxclient.kube_cluster.get(k8s_name), cloud_name,
                    system_uuid)
            else:
                subclouds = self.getSubcloudList()
                subcloud_id = next(
                    sub.subcloud_id for sub in subclouds
                    if sub.name == cloud_name)
                subcloud_stxclient = self.getSubcloudClient(subcloud_id)
                systems = subcloud_stxclient.isystem.list()
                system_uuid = systems[0].uuid
                k8s_cluster = process_k8s_cluster(
                    subcloud_stxclient,
                    subcloud_stxclient.kube_cluster.get(k8s_name), cloud_name,
                    system_uuid)

        if not k8s_cluster:
            return None

        logger.debug(f'k8sresource: {k8s_cluster.to_dict()}')
        return ocloudModel.StxGenericModel(
            ResourceTypeEnum.DMS, self._k8sconverter(k8s_cluster),
            self._k8shasher(k8s_cluster))

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

    @staticmethod
    def _respoolconverter(res_pool):
        setattr(res_pool, 'name', res_pool.region_name)
        return res_pool

    @staticmethod
    def _hostconverter(host):
        selected_keys = [
            "hostname", "personality", "id", "mgmt_ip", "mgmt_mac",
            "software_load", "capabilities",
            "operational", "availability", "administrative",
            "boot_device", "rootfs_device", "install_state", "subfunctions",
            "clock_synchronization", "max_cpu_mhz_allowed"
        ]
        content = host.to_dict()
        filtered = dict(
            filter(lambda item: item[0] in selected_keys, content.items()))
        setattr(host, 'filtered', filtered)
        setattr(host, 'name', host.hostname)
        return host

    @staticmethod
    def _labelconverter(label):
        selected_keys = [
            "uuid", "label_key", "label_value", "host_uuid"
        ]
        content = label.to_dict()
        print(content)
        filtered = dict(
            filter(lambda item: item[0] in selected_keys, content.items()))
        setattr(label, 'filtered', filtered)
        setattr(label, 'name', label.uuid.split(
            '-', 1)[0] + '-label-' + label.label_key)
        setattr(label, 'updated_at', None)
        setattr(label, 'created_at', None)
        return label

    @staticmethod
    def _cpuconverter(cpu):
        selected_keys = [
            "cpu", "core", "thread", "allocated_function", "numa_node",
            "cpu_model", "cpu_family"
        ]
        content = cpu.to_dict()
        filtered = dict(
            filter(lambda item: item[0] in selected_keys, content.items()))
        setattr(cpu, 'filtered', filtered)
        setattr(cpu, 'name', cpu.ihost_uuid.split(
            '-', 1)[0] + '-cpu-'+str(cpu.cpu))
        return cpu

    @staticmethod
    def _memconverter(mem):
        selected_keys = [
            "memtotal_mib", "memavail_mib", "vm_hugepages_use_1G",
            "vm_hugepages_possible_1G", "hugepages_configured",
            "vm_hugepages_avail_1G", "vm_hugepages_nr_1G",
            "vm_hugepages_nr_4K", "vm_hugepages_nr_2M",
            "vm_hugepages_possible_2M", "vm_hugepages_avail_2M",
            "platform_reserved_mib", "numa_node"
        ]
        content = mem.to_dict()
        filtered = dict(
            filter(lambda item: item[0] in selected_keys, content.items()))
        setattr(mem, 'filtered', filtered)
        setattr(mem, 'name', mem.ihost_uuid.split('-', 1)[0] +
                '-mem-node-'+str(mem.numa_node))
        return mem

    @staticmethod
    def _ethconverter(eth):
        selected_keys = [
            "name", "namedisplay", "dev_id", "pdevice", "capabilities",
            "type", "driver", "mac", "numa_node",
            "pciaddr", "pclass", "psvendor", "psdevice",
            "sriov_totalvfs", "sriov_numvfs", "dpdksupport",
            "sriov_vf_driver", "sriov_vf_pdevice_id", "interface_uuid"
        ]
        content = eth.to_dict()
        filtered = dict(
            filter(lambda item: item[0] in selected_keys, content.items()))
        setattr(eth, 'filtered', filtered)
        setattr(eth, 'name', eth.host_uuid.split('-', 1)[0] + '-'+eth.name)
        setattr(eth, 'updated_at', None)
        setattr(eth, 'created_at', None)
        return eth

    @staticmethod
    def _ifconverter(ifs):
        selected_keys = [
            "ifname", "iftype", "imac", "vlan_id", "imtu",
            "ifclass", "uses", "max_tx_rate",
            "sriov_vf_driver", "sriov_numvfs", "ptp_role"
        ]
        content = ifs.to_dict()
        filtered = dict(
            filter(lambda item: item[0] in selected_keys, content.items()))
        setattr(ifs, 'filtered', filtered)
        setattr(ifs, 'name', ifs.ihost_uuid.split('-', 1)[0] + '-'+ifs.ifname)
        setattr(ifs, 'updated_at', None)
        setattr(ifs, 'created_at', None)
        return ifs

    @staticmethod
    def _devconverter(dev):
        selected_keys = [
            "name", "pdevice", "pciaddr", "pvendor_id", "pvendor",
            "pclass_id", "pclass", "psvendor", "psdevice",
            "sriov_totalvfs", "sriov_numvfs", "numa_node"
        ]
        content = dev.to_dict()
        filtered = dict(
            filter(lambda item: item[0] in selected_keys, content.items()))
        setattr(dev, 'filtered', filtered)
        setattr(dev, 'name', dev.host_uuid.split('-', 1)[0] + '-'+dev.name)
        return dev

    @staticmethod
    def _k8sconverter(cluster):
        setattr(cluster, 'name', cluster.cloud_name +
                '.' + cluster.cluster_name)
        setattr(cluster, 'uuid',
                uuid.uuid3(uuid.NAMESPACE_URL, cluster.cloud_uuid))
        setattr(cluster, 'updated_at', None)
        setattr(cluster, 'created_at', None)
        setattr(cluster, 'events', [])
        logger.debug('k8s cluster name/uuid:' +
                     cluster.name + '/' + str(cluster.uuid))
        return cluster

    @staticmethod
    def _k8shasher(cluster):
        return str(hash((cluster.cluster_name, cluster.cloud_name,
                         cluster.cluster_api_endpoint, cluster.admin_user,
                         cluster.capabilities)))
