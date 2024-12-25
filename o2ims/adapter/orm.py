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
    Boolean,
    # engine,
    # event,
    exc,
)

from sqlalchemy.orm import mapper, relationship, backref
# from sqlalchemy.sql.sqltypes import Integer

from o2ims.domain import ocloud as ocloudModel
from o2ims.domain import subscription_obj as subModel
from o2ims.domain import alarm_obj as alarmModel
from o2ims.domain.resource_type import ResourceTypeEnum, ResourceKindEnum
# from o2ims.domain.alarm_obj import AlarmLastChangeEnum, PerceivedSeverityEnum
from o2ims.domain import performance_obj as perfModel

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
    Column("globalCloudId", String(255)),
    Column("name", String(255)),
    Column("description", String(255)),
    Column("serviceUri", String(255)),
    Column("smoRegistrationService", String(255))
    # Column("extensions", String(1024))
)

resourcetype = Table(
    "resourceType",
    metadata,
    Column("updatetime", DateTime),
    Column("createtime", DateTime),
    Column("hash", String(255)),
    Column("version_number", Integer),

    Column("resourceTypeId", String(255), primary_key=True),
    Column("resourceTypeEnum", Enum(
        ResourceTypeEnum, native_enum=False), nullable=False),
    Column("name", String(255)),
    Column("description", String(255)),
    Column("vendor", String(255)),
    Column("model", String(255)),
    Column("version", String(255)),
    Column("resourceKind", Enum(ResourceKindEnum)),
    Column("resourceClass", Enum(ResourceTypeEnum)),
    # Column("extensions", String(1024))

    Column("alarmDictionaryId", ForeignKey("alarmDictionary.id"))
)

resourcepool = Table(
    "resourcePool",
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
    Column("resourceTypeId", ForeignKey("resourceType.resourceTypeId")),
    Column("resourcePoolId", ForeignKey("resourcePool.resourcePoolId")),
    Column("globalAssetId", String(255)),
    Column("parentId", String(255)),
    Column("description", String()),
    Column("elements", Text()),
    Column("extensions", String())
)

deploymentmanager = Table(
    "deploymentManager",
    metadata,
    Column("updatetime", DateTime),
    Column("createtime", DateTime),
    Column("hash", String(255)),
    Column("version_number", Integer),

    Column("deploymentManagerId", String(255), primary_key=True),
    Column("oCloudId", ForeignKey("ocloud.oCloudId")),
    Column("name", String(255)),
    Column("description", String(255)),
    Column("serviceUri", String(255)),
    Column("supportedLocations", String(255)),
    Column("capabilities", Text),
    Column("capacity", Text),
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

alarm_definition = Table(
    "alarmDefinition",
    metadata,
    Column("updatetime", DateTime),
    Column("createtime", DateTime),

    Column("alarmDefinitionId", String(255), primary_key=True),
    Column("alarmName", String(255), unique=True),
    Column("alarmLastChange", String(255)),
    Column("alarmChangeType", String(255)),
    Column("alarmDescription", String(255)),
    Column("proposedRepairActions", String(1024)),
    Column("clearingType", String(255)),
    Column("managementInterfaceId", String(255)),
    Column("pkNotificationField", String(255))
)

alarm_dictionary = Table(
    "alarmDictionary",
    metadata,
    Column("updatetime", DateTime),
    Column("createtime", DateTime),

    Column("id", String(255), primary_key=True),
    Column("entityType", String(255), unique=True),
    Column("alarmDictionaryVersion", String(255)),
    Column("alarmDictionarySchemaVersion", String(255)),
    Column("vendor", String(255)),
    Column("managementInterfaceId", String(255)),
    Column("pkNotificationField", String(255))

    # Column("resourceTypeId", ForeignKey("resourceType.resourceTypeId"))
)

association_table1 = Table(
    'associationAlarmDictAndAlarmDef',
    metadata,
    Column("alarmDictionaryId", ForeignKey(
        'alarmDictionary.id', ondelete='cascade')),
    Column("alarmDefinitionId", ForeignKey(
        'alarmDefinition.alarmDefinitionId'))
)

alarm_event_record = Table(
    "alarmEventRecord",
    metadata,
    Column("updatetime", DateTime),
    Column("createtime", DateTime),
    Column("hash", String(255)),

    Column("alarmEventRecordId", String(255), primary_key=True),
    Column("resourceTypeId", ForeignKey("resourceType.resourceTypeId")),
    Column("resourceId", ForeignKey("resource.resourceId")),
    Column("alarmDefinitionId", ForeignKey(
        "alarmDefinition.alarmDefinitionId")),
    Column("probableCauseId", String(255)),
    Column("perceivedSeverity", Integer),
    Column("alarmRaisedTime", String(255)),
    Column("alarmChangedTime", String(255)),
    Column("alarmAcknowledgeTime", String(255)),
    Column("alarmAcknowledged", String(255)),
    Column("extensions", String())
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

alarm_service_configuration = Table(
    "alarmServiceConfiguration",
    metadata,
    Column("updatetime", DateTime),
    Column("createtime", DateTime),

    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("retentionPeriod", Integer, default=15)
)

measurement_job = Table(
    "measurementJob",
    metadata,
    Column("updatetime", DateTime),
    Column("createtime", DateTime),
    Column("hash", String(255)),
    Column("version_number", Integer),

    Column("performanceMeasurementJobId", String(255), primary_key=True),
    Column("consumerPerformanceJobId", String(255)),
    Column("state", String(255)),  # MeasurementJobState enum
    Column("collectionInterval", Integer),
    Column("resourceScopeCriteria", Text),  # JSON stored as text
    Column("measurementSelectionCriteria", Text),  # JSON stored as text
    Column("status", String(255)),  # MeasurementJobStatus enum
    Column("preinstalledJob", Boolean),
    Column("qualifiedResourceTypes", Text),  # JSON array stored as text
    Column("extensions", Text)  # JSON stored as text
)

measured_resource = Table(
    "measuredResource",
    metadata,
    Column("updatetime", DateTime),
    Column("createtime", DateTime),
    Column("hash", String(255)),
    Column("version_number", Integer),

    Column("id", String(255), primary_key=True),
    Column("resourceId", String(255)),
    Column("resourceTypeId", String(255)),
    Column("measurementJobId", ForeignKey(
        "measurementJob.performanceMeasurementJobId"))
)

collected_measurement = Table(
    "collectedMeasurement",
    metadata,
    Column("updatetime", DateTime),
    Column("createtime", DateTime),
    Column("hash", String(255)),
    Column("version_number", Integer),

    Column("id", String(255), primary_key=True),
    Column("measurementId", String(255)),
    Column("measurementJobId", ForeignKey(
        "measurementJob.performanceMeasurementJobId"))
)


@retry((exc.IntegrityError), tries=3, delay=2)
def wait_for_metadata_ready(engine):
    # wait for mapper ready
    metadata.create_all(engine, checkfirst=True)
    logger.info("metadata is ready")


def start_o2ims_mappers(engine=None):
    logger.info("Starting O2 IMS mappers")

    # IMS Infrastruture Monitoring Mappering
    mapper(alarmModel.AlarmServiceConfiguration, alarm_service_configuration)
    mapper(alarmModel.AlarmEventRecord, alarm_event_record)
    alarmdefinition_mapper = mapper(
        alarmModel.AlarmDefinition, alarm_definition)
    mapper(alarmModel.ProbableCause, alarm_probable_cause)
    mapper(alarmModel.AlarmSubscription, alarm_subscription)
    alarm_dictionary_mapper = mapper(
        alarmModel.AlarmDictionary, alarm_dictionary,
        properties={
            "alarmDefinition": relationship(alarmdefinition_mapper,
                                            cascade='all,delete-orphan',
                                            secondary=association_table1,
                                            single_parent=True,
                                            backref='alarmDictionaries')
        }
    )

    # IMS Infrastructure Inventory Mappering
    dm_mapper = mapper(ocloudModel.DeploymentManager, deploymentmanager)
    resourcepool_mapper = mapper(ocloudModel.ResourcePool, resourcepool)
    resourcetype_mapper = mapper(
        ocloudModel.ResourceType, resourcetype,
        properties={
            #     "alarmDictionary": relationship(alarmModel.AlarmDictionary,
            #                                     uselist=False)
            "alarmDictionary": relationship(alarm_dictionary_mapper,
                                            backref=backref(
                                                'resourceType', uselist=False))

        }
    )
    mapper(
        ocloudModel.Ocloud,
        ocloud,
        properties={
            "deploymentManagers": relationship(dm_mapper),
            # "resourceTypes": relationship(resourcetype_mapper),
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

    # Performance Monitoring Mappering
    measured_resource_mapper = mapper(
        perfModel.MeasuredResource,
        measured_resource
    )

    collected_measurement_mapper = mapper(
        perfModel.CollectedMeasurement,
        collected_measurement
    )

    mapper(
        perfModel.MeasurementJob,
        measurement_job,
        properties={
            "measuredResources": relationship(
                measured_resource_mapper,
                cascade="all, delete-orphan"
            ),
            "collectedMeasurements": relationship(
                collected_measurement_mapper,
                cascade="all, delete-orphan"
            )
        }
    )

    if engine is not None:
        wait_for_metadata_ready(engine)
