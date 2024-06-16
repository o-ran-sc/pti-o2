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

from o2common.config import config
from o2common.domain.base import AgRoot, Serializer, \
    InfrastructureInventoryObject
# from dataclasses import dataclass
# from datetime import date
# from typing import Optional, List, Set
from .resource_type import ResourceKindEnum, ResourceTypeEnum
from .alarm_obj import AlarmDictionary


DeploymentManagerProfileDefault = 'native_k8sapi'
DeploymentManagerProfileSOL018 = 'sol018'
DeploymentManagerProfileSOL018HelmCLI = 'sol018_helmcli'


class DeploymentManager(InfrastructureInventoryObject, AgRoot, Serializer):
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

        if 'capabilities' in d and d['capabilities'] != '':
            d['capabilities'] = json.loads(d['capabilities'])
        if 'capacity' in d and d['capacity'] != '':
            d['capacity'] = json.loads(d['capacity'])
        return d

    def get_notification_dict(self):
        return self.get_fields_as_dict(
            ['deploymentManagerId', 'name', 'oCloudId', 'serviceUri',
             'description'])


class ResourcePool(InfrastructureInventoryObject, AgRoot, Serializer):
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

    def get_notification_dict(self):
        return self.get_fields_as_dict(
            ['resourcePoolId', 'oCloudId', 'globalLocationId', 'name',
             'description'])


class ResourceType(InfrastructureInventoryObject, AgRoot, Serializer):
    def __init__(self, typeid: str, name: str, typeEnum: ResourceTypeEnum,
                 vendor: str = '', model: str = '',
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
        self.alarmDictionary = None
        self.resourceKind = ResourceKindEnum.UNDEFINED
        self.resourceClass = ResourceTypeEnum.UNDEFINED
        self.extensions = []

        self.version_number = 0

    def serialize(self):
        d = Serializer.serialize(self)
        if 'alarmDictionary' in d and \
                type(d['alarmDictionary']) is AlarmDictionary:
            d['alarmDictionary'] = d['alarmDictionary'].serialize()
        return d

    def get_notification_dict(self):
        return self.get_fields_as_dict(
            ['resourceTypeId', 'name', 'description', 'vendor', 'model',
             'version'])


class Resource(InfrastructureInventoryObject, AgRoot, Serializer):
    def __init__(self, resourceId: str, resourceTypeId: str,
                 resourcePoolId: str, parentId: str = '',
                 gAssetId: str = '', elements: str = '',
                 description: str = '', extensions: str = '') -> None:
        super().__init__()
        self.resourceId = resourceId
        self.description = description
        self.resourceTypeId = resourceTypeId
        self.globalAssetId = gAssetId
        self.resourcePoolId = resourcePoolId
        self.elements = elements
        self.extensions = extensions

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

    def get_notification_dict(self):
        return self.get_fields_as_dict(
            ['resourceId', 'resourceTypeId', 'resourcePoolId', 'globalAssetId',
             'description'])


class Ocloud(InfrastructureInventoryObject, AgRoot, Serializer):
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

    def get_notification_dict(self):
        return self.get_fields_as_dict(
            ['oCloudId', 'globalcloudId', 'globalCloudId', 'name',
             'description', 'serviceUri'])
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
