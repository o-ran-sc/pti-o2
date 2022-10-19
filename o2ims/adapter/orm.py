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

# from typing_extensions import Required
from retry import retry
from sqlalchemy import (
    Table,
    MetaData,
    Column,
    Integer,
    String,
    Text,
    Enum,
    # Date,
    DateTime,
    ForeignKey,
    # Boolean,
    # engine,
    # event,
    exc,
)

from sqlalchemy.orm import mapper, relationship
# from sqlalchemy.sql.sqltypes import Integer

from o2ims.domain import ocloud as ocloudModel
from o2ims.domain import subscription_obj as subModel
from o2ims.domain import configuration_obj as confModel
from o2ims.domain import alarm_obj as alarmModel
from o2ims.domain.resource_type import ResourceTypeEnum
# from o2ims.domain.alarm_obj import AlarmLastChangeEnum, PerceivedSeverityEnum

from o2common.helper import o2logging
logger = o2logging.get_logger(__name__)

metadata = MetaData()

ocloud = Table(
    "ocloud",
    metadata,
    Column("updatetime", DateTime),
    Column("createtime", DateTime),
    Column("hash", String(255)),
    Column("version_number", Integer),

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
    Column("updatetime", DateTime),
    Column("createtime", DateTime),
    Column("hash", String(255)),

    Column("resourceTypeId", String(255), primary_key=True),
    Column("resourceTypeEnum", Enum(
        ResourceTypeEnum, native_enum=False), nullable=False),
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
    Column("updatetime", DateTime),
    Column("createtime", DateTime),
    Column("hash", String(255)),
    Column("version_number", Integer),

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
    Column("updatetime", DateTime),
    Column("createtime", DateTime),
    Column("hash", String(255)),
    Column("version_number", Integer),

    Column("resourceId", String(255), primary_key=True),
    Column("resourceTypeId", ForeignKey("resourcetype.resourceTypeId")),
    Column("resourcePoolId", ForeignKey("resourcepool.resourcePoolId")),
    Column("name", String(255)),
    # Column("globalAssetId", String(255)),
    Column("parentId", String(255)),
    Column("description", String(255)),
    Column("elements", Text())
    # Column("extensions", String(1024))
)

deploymentmanager = Table(
    "deploymentmanager",
    metadata,
    Column("updatetime", DateTime),
    Column("createtime", DateTime),
    Column("hash", String(255)),
    Column("version_number", Integer),

    Column("deploymentManagerId", String(255), primary_key=True),
    Column("oCloudId", ForeignKey("ocloud.oCloudId")),
    Column("name", String(255)),
    Column("description", String(255)),
    Column("deploymentManagementServiceEndpoint", String(255)),
    Column("supportedLocations", String(255)),
    Column("capabilities", String(255)),
    Column("capacity", String(255)),
    Column("profile", Text())
    # Column("extensions", String(1024))
)

subscription = Table(
    "subscription",
    metadata,
    Column("updatetime", DateTime),
    Column("createtime", DateTime),
    Column("hash", String(255)),
    Column("version_number", Integer),

    Column("subscriptionId", String(255), primary_key=True),
    Column("callback", String(255)),
    Column("consumerSubscriptionId", String(255)),
    Column("filter", String(255)),
)

configuration = Table(
    "configuration",
    metadata,
    Column("updatetime", DateTime),
    Column("createtime", DateTime),

    Column("configurationId", String(255), primary_key=True),
    Column("conftype", String(255)),
    Column("callback", String(255)),
    Column("status", String(255)),
    Column("comments", String(255)),
)

alarm_definition = Table(
    "alarmDefinition",
    metadata,
    Column("updatetime", DateTime),
    Column("createtime", DateTime),

    Column("alarmDefinitionId", String(255), primary_key=True),
    Column("alarmName", String(255), unique=True),
    Column("alarmLastChange", String(255)),
    Column("alarmDescription", String(255)),
    Column("proposeRepairActions", String(255)),
    Column("clearingType", String(255)),
    Column("managementInterfaceId", String(255)),
    Column("pkNotificationField", String(255))
)

alarm_event_record = Table(
    "alarmEventRecord",
    metadata,
    Column("updatetime", DateTime),
    Column("createtime", DateTime),
    Column("hash", String(255)),

    Column("alarmEventRecordId", String(255), primary_key=True),
    Column("resourceTypeId", ForeignKey("resourcetype.resourceTypeId")),
    Column("resourceId", ForeignKey("resource.resourceId")),
    Column("alarmDefinitionId", ForeignKey(
        "alarmDefinition.alarmDefinitionId")),
    Column("probableCauseId", String(255)),
    Column("perceivedSeverity", Integer),
    Column("alarmRaisedTime", String(255)),
    Column("alarmChangedTime", String(255)),
    Column("alarmAcknowledgeTime", String(255)),
    Column("alarmAcknowledged", String(255)),
)

alarm_probable_cause = Table(
    "probableCause",
    metadata,
    Column("updatetime", DateTime),
    Column("createtime", DateTime),
    Column("hash", String(255)),

    Column("probableCauseId", String(255), primary_key=True),
    Column("name", String(255)),
    Column("description", String(255)),
)

alarm_subscription = Table(
    "alarmSubscription",
    metadata,
    Column("updatetime", DateTime),
    Column("createtime", DateTime),

    Column("alarmSubscriptionId", String(255), primary_key=True),
    Column("callback", String(255)),
    Column("consumerSubscriptionId", String(255)),
    Column("filter", String(255)),
)


@retry((exc.IntegrityError), tries=3, delay=2)
def wait_for_metadata_ready(engine):
    # wait for mapper ready
    metadata.create_all(engine, checkfirst=True)
    logger.info("metadata is ready")


def start_o2ims_mappers(engine=None):
    logger.info("Starting O2 IMS mappers")

    # IMS Infrastructure Inventory Mappering
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
    mapper(subModel.Subscription, subscription)
    mapper(confModel.Configuration, configuration)

    # IMS Infrastruture Monitoring Mappering
    mapper(alarmModel.AlarmEventRecord, alarm_event_record)
    mapper(alarmModel.AlarmDefinition, alarm_definition)
    mapper(alarmModel.ProbableCause, alarm_probable_cause)
    mapper(alarmModel.AlarmSubscription, alarm_subscription)

    if engine is not None:
        wait_for_metadata_ready(engine)
