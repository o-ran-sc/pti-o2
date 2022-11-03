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

from __future__ import annotations
import json

from o2common.domain.base import AgRoot, Serializer
from o2common.config import config, conf as CONF
# from dataclasses import dataclass
# from datetime import date
# from typing import Optional, List, Set
from .resource_type import ResourceKindEnum, ResourceTypeEnum


DeploymentManagerProfileDefault = 'native_k8sapi'
DeploymentManagerProfileSOL018 = 'sol018'
DeploymentManagerProfileSOL018HelmCLI = 'sol018_helmcli'


class DeploymentManager(AgRoot, Serializer):
    def __init__(self, id: str, name: str, ocloudid: str,
                 dmsendpoint: str, description: str = '',
                 supportedLocations: str = '', capabilities: str = '',
                 capacity: str = '', profile: str = '') -> None:
        super().__init__()
        self.deploymentManagerId = id
        self.name = name
        self.description = description
        self.oCloudId = ocloudid
        self.serviceUri = dmsendpoint
        self.supportedLocations = supportedLocations
        self.capabilities = capabilities
        self.capacity = capacity
        self.profile = profile
        self.extensions = []

        self.version_number = 0

    def serialize(self):
        d = Serializer.serialize(self)

        if 'profile' in d and d['profile'] != '':
            d['profile'] = json.loads(d['profile'])
        d['profileSupportList'] = [
            DeploymentManagerProfileDefault,
        ]
        profiles = config.get_dms_support_profiles()
        for profile in profiles:
            if profile == DeploymentManagerProfileSOL018:
                d['profileSupportList'].append(profile)
            elif profile == DeploymentManagerProfileSOL018HelmCLI:
                d['profileSupportList'].append(profile)

        return d


class ResourcePool(AgRoot, Serializer):
    def __init__(self, id: str, name: str, location: str,
                 ocloudid: str, gLocationId: str = '',
                 description: str = '') -> None:
        super().__init__()
        self.resourcePoolId = id
        self.globalLocationId = gLocationId
        self.name = name
        self.description = description
        self.oCloudId = ocloudid
        self.location = location
        self.resources = ''
        self.extensions = []

        self.version_number = 0


class ResourceType(AgRoot, Serializer):
    def __init__(self, typeid: str, name: str, typeEnum: ResourceTypeEnum,
                 ocloudid: str, vendor: str = '', model: str = '',
                 version: str = '',
                 description: str = '') -> None:
        super().__init__()
        self.resourceTypeId = typeid
        self.resourceTypeEnum = typeEnum
        self.name = name
        self.description = description
        self.vendor = vendor
        self.model = model
        self.version = version
        self.alarmDictionary = {}
        self.resourceKind = ResourceKindEnum.UNDEFINED
        self.resourceClass = ResourceTypeEnum.UNDEFINED
        self.extensions = []

        self.version_number = 0

    def serialize(self):
        d = Serializer.serialize(self)

        d["alarmDictionary"] = CONF.alarm_dictionaries.get(
            d['name']).serialize()
        return d


class Resource(AgRoot, Serializer):
    def __init__(self, resourceId: str, resourceTypeId: str,
                 resourcePoolId: str, name: str, parentId: str = '',
                 gAssetId: str = '', elements: str = '',
                 description: str = '') -> None:
        super().__init__()
        self.resourceId = resourceId
        self.description = description
        self.resourceTypeId = resourceTypeId
        self.globalAssetId = gAssetId
        self.resourcePoolId = resourcePoolId
        self.elements = elements
        self.extensions = []

        self.name = name
        self.parentId = parentId
        self.children = []

        self.version_number = 0

    def set_children(self, children: list):
        self.children = children

    def set_resource_type_name(self, resource_type_name: str):
        self.resourceTypeName = resource_type_name

    def serialize(self):
        d = Serializer.serialize(self)

        if 'elements' in d and d['elements'] != '':
            d['elements'] = json.loads(d['elements'])

        if not hasattr(self, 'children') or len(self.children) == 0:
            return d
        else:
            d['children'] = []

        for child in self.children:
            d['children'].append(child.serialize())
        return d


class Ocloud(AgRoot, Serializer):
    def __init__(self, ocloudid: str, name: str, imsendpoint: str,
                 globalcloudId: str = '',
                 description: str = '', version_number: int = 0) -> None:
        super().__init__()
        self.oCloudId = ocloudid
        self.globalCloudId = globalcloudId
        self.name = name
        self.description = description
        self.serviceUri = imsendpoint
        self.resourceTypes = []
        self.resourcePools = []
        self.deploymentManagers = []
        self.smoRegistrationService = ''
        self.extensions = []

        self.version_number = version_number

    # def addDeploymentManager(self,
    #                          deploymentManager: DeploymentManager):

    #     deploymentManager.oCloudId = self.oCloudId
    #     old = filter(
    #         lambda x: x.deploymentManagerId ==
    #         deploymentManager.deploymentManagerId,
    #         self.deploymentManagers)
    #     for o in old or []:
    #         self.deploymentManagers.remove(o)
    #     self.deploymentManagers.append(deploymentManager)
