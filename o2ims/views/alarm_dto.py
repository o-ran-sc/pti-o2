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

from o2ims.views.api_ns import api_ims_monitoring as api_monitoring_v1


class AlarmDTO:

    alarm_event_record_get = api_monitoring_v1.model(
        "AlarmGetDto",
        {
            'alarmEventRecordId': fields.String(
                required=True,
                description='Alarm Event Record ID'),
            'resourceTypeId': fields.String,
            'resourceTypeID': fields.String(attribute='resourceTypeId'),
            'resourceId': fields.String,
            'resourceID': fields.String(attribute='resourceId'),
            'alarmDefinitionId': fields.String,
            'alarmDefinitionID': fields.String(attribute='alarmDefinitionId'),
            'probableCauseId': fields.String,
            'probableCauseID': fields.String(attribute='probableCauseId'),
            'alarmRaisedTime': fields.String,
            'alarmChangedTime': fields.String,
            'alarmAcknowledgeTime': fields.String,
            'alarmAcknowledged': fields.Boolean,
            'perceivedSeverity': fields.String,
            'extensions': fields.Raw(attribute='extensions'),
        }
        # mask='{alarmEventRecordId,resourceTypeID,resourceID,' +
        # 'alarmDefinitionID,probableCauseID,' +
        # 'alarmRaisedTime,perceivedSeverity,alarmChangedTime,' +
        # 'alarmAcknowledgeTime,alarmAcknowledged,extensions}'
    )


class SubscriptionDTO:

    subscription_get = api_monitoring_v1.model(
        "AlarmSubscriptionGetDto",
        {
            'alarmSubscriptionId': fields.String(
                required=True,
                description='Alarm Subscription ID'),
            'callback': fields.String,
            'consumerSubscriptionId': fields.String,
            'filter': fields.String,
        },
        mask='{alarmSubscriptionId,callback}'
    )

    subscription_create = api_monitoring_v1.model(
        "AlarmSubscriptionCreateDto",
        {
            'callback': fields.String(
                required=True,
                description='Alarm Subscription callback address'),
            'consumerSubscriptionId': fields.String,
            'filter': fields.String,
        }
    )
