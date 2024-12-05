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

from flask_restx import fields

from o2common.views.flask_restx_fields import Json2Dict
from o2ims.views.api_ns import api_ims_monitoring as api_monitoring_v1


class MonitoringApiV1DTO:

    api_version = api_monitoring_v1.model(
        'MonitoringV1ApiVersionStructure',
        {
            'version': fields.String(
                required=True,
                example='1.0.0',
                description='Identifies a supported version.'
            )
        },
        mask='{version,}'
    )

    api_version_info_get = api_monitoring_v1.model(
        "MonitoringV1APIVersion",
        {
            'uriPrefix': fields.String(
                required=True,
                example='https://128.224.115.36:30205/' +
                'o2ims-infrastructureMonitoring/v1',
                description='Specifies the URI prefix for the API'),
            'apiVersions': fields.List(
                fields.Nested(api_version),
                example=[{'version': '1.0.0'}],
                description='Version(s) supported for the API ' +
                'signaled by the uriPrefix attribute.'),
        },
        mask='{uriPrefix,apiVersions}'
    )


class AlarmDTO:

    alarm_event_record_get = api_monitoring_v1.model(
        "AlarmGetDto",
        {
            'alarmEventRecordId': fields.String(
                required=True,
                example='97cc2b01-0e71-4a93-a911-2e87f04d996f',
                description='The identifier for the AlarmEventRecord Object.'),
            'resourceTypeId': fields.String(
                example='60cba7be-e2cd-3b8c-a7ff-16e0f10573f9',
                description='A reference to the type of resource which ' +
                'caused the alarm.'),
            'resourceTypeID': fields.String(
                attribute='resourceTypeId',
                example='60cba7be-e2cd-3b8c-a7ff-16e0f10573f9',
                description='A reference to the type of resource which ' +
                'caused the alarm.(Specification)'),
            'resourceId': fields.String(
                example='5b3a2da8-17da-466c-b5f7-972590c7baf2',
                description='A reference to the resource instance which ' +
                'caused the alarm.'),
            'resourceID': fields.String(
                attribute='resourceId',
                example='5b3a2da8-17da-466c-b5f7-972590c7baf2',
                description='A reference to the resource instance which ' +
                'caused the alarm.(Specification)'),
            'alarmDefinitionId': fields.String(
                example='1197f463-b3d4-3aa3-9c14-faa493baa069',
                description='A reference to the Alarm Definition record ' +
                'in the Alarm Dictionary associated with the referenced ' +
                'Resource Type.'),
            'alarmDefinitionID': fields.String(
                attribute='alarmDefinitionId',
                example='1197f463-b3d4-3aa3-9c14-faa493baa069',
                description='A reference to the Alarm Definition record ' +
                'in the Alarm Dictionary associated with the referenced ' +
                'Resource Type.(Specification)'),
            'probableCauseId': fields.String(
                example='f52054c9-6f3c-39a0-aab8-e00e01d8c4d3',
                description='A reference to the ProbableCause of the Alarm.'),
            'probableCauseID': fields.String(
                attribute='probableCauseId',
                example='f52054c9-6f3c-39a0-aab8-e00e01d8c4d3',
                description='A reference to the ProbableCause of the ' +
                'Alarm.(Specification)'),
            'alarmRaisedTime': fields.String(
                example='2022-12-22 09:42:53',
                description='Date/Time stamp value when the ' +
                'AlarmEventRecord has been created.'),
            'alarmChangedTime': fields.String(
                example='',
                description='Date/Time stamp value when any value of ' +
                'the AlarmEventRecord has been modified.'),
            'alarmAcknowledgeTime': fields.String(
                example='',
                description='Date/Time stamp value when the alarm ' +
                'condition is acknowledged.'),
            'alarmAcknowledged': fields.Boolean(
                example=False,
                description='Boolean value indicating of a management ' +
                'system has acknowledged the alarm.'),
            'perceivedSeverity': fields.String(
                example='1',
                description='One of the following values: \n ' +
                '0 for "CRITICAL" \n' +
                '1 for "MAJOR" \n' +
                '2 for "MINOR" \n' +
                '3 for "WARNING" \n' +
                '4 for "INDETERMINATE" \n' +
                '5 for "CLEARED"'),
            'extensions': Json2Dict(attribute='extensions')
        }
        # mask='{alarmEventRecordId,resourceTypeID,resourceID,' +
        # 'alarmDefinitionID,probableCauseID,' +
        # 'alarmRaisedTime,perceivedSeverity,alarmChangedTime,' +
        # 'alarmAcknowledgeTime,alarmAcknowledged,extensions}'
    )

    alarm_event_record_patch = api_monitoring_v1.model(
        "AlarmPatchDto",
        {
            'alarmAcknowledged': fields.Boolean(
                example=True,
                description='Boolean value indication of a management ' +
                'system has acknowledged the alarm.'),
            'perceivedSeverity': fields.String(
                example='5',
                description='indicate that the alarm record is requested ' +
                'to be cleared. Only the value "5" for "CLEARED" is ' +
                'permitted in a request message content. ')
        },
        mask='{alarmAcknowledged,}'
    )


class SubscriptionDTO:

    subscription_get = api_monitoring_v1.model(
        "AlarmSubscriptionGetDto",
        {
            'alarmSubscriptionId': fields.String(
                required=True,
                example='e320da6d-27a8-4948-8b52-3bf3355b45f3',
                description='Identifier for the Alarm Subscription.'),
            'callback': fields.String(
                example='https://128.224.115.15:1081/smo/v1/' +
                'o2ims_alarm_observer',
                description='The fully qualified URI to a consumer ' +
                'procedure which can process a Post of the ' +
                'InventoryEventNotification.'),
            'consumerSubscriptionId': fields.String(
                example='3F20D850-AF4F-A84F-FB5A-0AD585410361',
                description='Identifier for the consumer of events sent ' +
                'due to the Subscription.'),
            'filter': fields.String(
                example='',
                description='Criteria for events which do not need to be ' +
                'reported or will be filtered by the subscription ' +
                'notification service. Therefore, if a filter is not ' +
                'provided then all events are reported.'),
        },
        mask='{alarmSubscriptionId,callback}'
    )

    subscription_create = api_monitoring_v1.model(
        "AlarmSubscriptionCreateDto",
        {
            'callback': fields.String(
                required=True,
                example='https://128.224.115.15:1081/smo/v1/' +
                'o2ims_alarm_observer',
                description='The fully qualified URI to a consumer ' +
                'procedure which can process a Post of the ' +
                'InventoryEventNotification.'),
            'consumerSubscriptionId': fields.String(
                example='3F20D850-AF4F-A84F-FB5A-0AD585410361',
                description='Identifier for the consumer of events sent ' +
                'due to the Subscription.'),
            'filter': fields.String(
                example='',
                description='Criteria for events which do not need to be ' +
                'reported or will be filtered by the subscription ' +
                'notification service. Therefore, if a filter is not ' +
                'provided then all events are reported.'),
        }
    )


class AlarmServiceConfigurationDTO:

    alarm_service_configuration_get = api_monitoring_v1.model(
        "AlarmServiceConfigurationDto",
        {
            'retentionPeriod': fields.Integer(
                required=True,
                example=14,
                description='Number of days for alarm history to be retained.'
                ),
            'extensions': Json2Dict(attribute='extensions')
        }
    )

    alarm_service_configuration_expect = api_monitoring_v1.model(
        "AlarmServiceConfigurationDto",
        {
            'retentionPeriod': fields.Integer(
                required=True,
                example=14,
                description='Number of days for alarm history to be retained.'
                )
        }
    )
