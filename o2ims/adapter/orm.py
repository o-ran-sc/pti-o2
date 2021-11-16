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

from sqlalchemy import (
    Table,
    MetaData,
    Column,
    # Integer,
    String,
    # Date,
    ForeignKey,
    # engine,
    # event,
)

from sqlalchemy.orm import mapper, relationship

from o2ims.domain import ocloud as ocloudModel

from o2common.helper import logger
logger = logger.get_logger(__name__)

metadata = MetaData()

ocloud = Table(
    "ocloud",
    metadata,
    Column("oCloudId", String(255), primary_key=True),
    Column("globalcloudId", String(255)),
    Column("name", String(255)),
    Column("description", String(255)),
    Column("infrastructureManagementServiceEndpoint", String(255))
    # Column("extensions", String(1024))
)

resourcetype = Table(
    "resourcetype",
    metadata,
    Column("resourceTypeId", String(255), primary_key=True),
    Column("oCloudId", ForeignKey("ocloud.oCloudId")),
    Column("name", String(255)),
    Column("vendor", String(255)),
    Column("model", String(255)),
    Column("version", String(255)),
    Column("description", String(255)),
    # Column("extensions", String(1024))
)

resourcepool = Table(
    "resourcepool",
    metadata,
    Column("resourcePoolId", String(255), primary_key=True),
    Column("oCloudId", ForeignKey("ocloud.oCloudId")),
    Column("globalLocationId", String(255)),
    Column("name", String(255)),
    Column("location", String(255)),
    Column("description", String(255)),
    # Column("resources", String(1024))
    # Column("extensions", String(1024))
)

resource = Table(
    "resource",
    metadata,
    Column("resourceId", String(255), primary_key=True),
    Column("resourceTypeId", ForeignKey("resourcetype.resourceTypeId")),
    Column("resourcePoolId", ForeignKey("resourcepool.resourcePoolId")),
    # Column("oCloudId", ForeignKey("ocloud.oCloudId")),
    Column("parentId", String(255)),
    Column("description", String(255)),
    # Column("elements", String(255))
    # Column("extensions", String(1024))
)

deploymentmanager = Table(
    "deploymentmanager",
    metadata,
    Column("deploymentManagerId", String(255), primary_key=True),
    Column("oCloudId", ForeignKey("ocloud.oCloudId")),
    Column("name", String(255)),
    Column("description", String(255)),
    Column("deploymentManagementServiceEndpoint", String(255)),
    Column("supportedLocations", String(255)),
    Column("capabilities", String(255)),
    Column("capacity", String(255)),
    # Column("extensions", String(1024))
)

subscription = Table(
    "subscription",
    metadata,
    Column("subscriptionId", String(255), primary_key=True),
    Column("callback", String(255)),
    Column("consumerSubscriptionId", String(255)),
    Column("filter", String(255)),
)


def start_o2ims_mappers(engine=None):
    logger.info("Starting O2 IMS mappers")

    dm_mapper = mapper(ocloudModel.DeploymentManager, deploymentmanager)
    resourcepool_mapper = mapper(ocloudModel.ResourcePool, resourcepool)
    resourcetype_mapper = mapper(ocloudModel.ResourceType, resourcetype)
    mapper(
        ocloudModel.Ocloud,
        ocloud,
        properties={
            "deploymentManagers": relationship(dm_mapper),
            "resourceTypes": relationship(resourcetype_mapper),
            "resourcePools": relationship(resourcepool_mapper)
        })
    mapper(
        ocloudModel.Resource,
        resource,
        properties={
            "resourceTypes": relationship(resourcetype_mapper),
            "resourcePools": relationship(resourcepool_mapper)
        }
    )
    mapper(ocloudModel.Subscription, subscription)

    if engine is not None:
        metadata.create_all(engine)
