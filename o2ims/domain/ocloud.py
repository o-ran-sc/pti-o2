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
# from dataclasses import dataclass
# from datetime import date
# from typing import Optional, List, Set
from .resource_type import ResourceTypeEnum
# from uuid import UUID



class Subscription:
    def __init__(self, id: str, callback: str, consumersubid: list=[],
                 filter: list=[]) -> None:
        self.subscriptionId = id
        self.callback = callback
        self.consumerSubscriptionId = consumersubid
        self.filter = filter
        

class DeploymentManager:
    def __init__(self, id: str, name: str, ocloudid: str,
                 dmsendpoint: str, description: str='', 
                 supportedLocations: str='', capabilities: str='',
                 capacity: str='') -> None:
        self.deploymentManagerId = id
        self.oCloudId = ocloudid
        self.name = name
        self.description = description
        self.deploymentManagementServiceEndpoint = dmsendpoint
        self.supportedLocations = supportedLocations
        self.capabilities = capabilities
        self.capacity = capacity
        self.extensions = []


class ResourcePool:
    def __init__(self, id: str, name: str, location: str,
                 ocloudid: str, gLocationId: str='',
                 description: str='') -> None:
        self.resourcePoolId = id
        self.oCloudId = ocloudid
        self.globalLocationId = gLocationId
        self.name = name
        self.location = location
        self.description = description
        self.extensions = []


class ResourceType:
    def __init__(self, typeid: str, name: str, typeEnum: ResourceTypeEnum,
                 ocloudid: str, vender: str='', model: str='', version: str='',
                 description: str='') -> None:
        self.resourceTypeId = typeid
        self.oCloudId = ocloudid
        self.resourceTypeEnum = typeEnum.value
        self.name = name
        self.vender = vender
        self.model = model
        self.version = version
        self.description = description
        self.extensions = []


class Resource:
    def __init__(self, resourceId: str, resourceTypeId: str,
                 resourcePoolId: str, oCloudId: str='',
                 parentId: str='', elements: list=[],
                 description: str='') -> None:
        self.resourceId = resourceId
        self.oCloudId = oCloudId
        self.resourceTypeId = resourceTypeId
        self.resourcePoolId = resourcePoolId
        self.parentId = parentId
        self.elements = elements
        self.description = description
        self.extensions = []


class Ocloud:
    def __init__(self, ocloudid: str, name: str, imsendpoint: str,
                 globalcloudId: str = '',
                 description: str = '', version_number: int = 0) -> None:

        self.oCloudId = ocloudid
        self.globalcloudId = globalcloudId
        self.version_number = version_number
        self.name = name
        self.description = description
        self.infrastructureManagementServiceEndpoint = imsendpoint
        self.resourcePools = []
        self.deploymentManagers = []
        self.resourceTypes = []
        self.extensions = []
        self.events = []

    def addDeploymentManager(self,
                             deploymentManager: DeploymentManager):

        deploymentManager.oCloudId = self.oCloudId
        old = filter(
            lambda x: x.deploymentManagerId ==
            deploymentManager.deploymentManagerId,
            self.deploymentManagers)
        for o in old or []:
            self.deploymentManagers.remove(o)
        self.deploymentManagers.append(deploymentManager)
