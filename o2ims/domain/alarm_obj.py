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

from __future__ import annotations
from enum import Enum
import json
import datetime

from o2common.domain.base import AgRoot, Serializer


class FaultGenericModel(AgRoot):
    def __init__(self, type: str,
                 api_response: dict = None, content_hash=None) -> None:
        super().__init__()
        if api_response:
            self.id = str(api_response.uuid)
            self.name = self.id
            self.type = type
            self.status = api_response.state
            # TODO: time less than second
            self.timestamp = datetime.datetime.strptime(
                api_response.timestamp.split('.')[0], "%Y-%m-%dT%H:%M:%S") \
                if api_response.timestamp else None

            # if hasattr(api_response, 'alarm_id'):
            #     self.alarm_id = api_response.alarm_id
            # elif hasattr(api_response, 'event_log_id'):
            #     self.alarm_id = api_response.event_log_id

            self.hash = content_hash if content_hash \
                else str(hash((self.id, self.timestamp, self.status)))
            self.content = json.dumps(api_response.to_dict())

    def is_outdated(self, newmodel) -> bool:
        # return self.updatetime < newmodel.updatetime
        # logger.warning("hash1: " + self.hash + " vs hash2: " + newmodel.hash)
        return self.hash != newmodel.hash

    def update_by(self, newmodel) -> None:
        if self.id != newmodel.id:
            pass
            # raise MismatchedModel("Mismatched model")
        self.name = newmodel.name
        self.createtime = newmodel.createtime
        self.updatetime = newmodel.updatetime
        self.content = newmodel.content


class PerceivedSeverityEnum(str, Enum):
    CRITICAL = 0
    MAJOR = 1
    MINOR = 2
    WARNING = 3
    INDETERMINATE = 4
    CLEARED = 5


class AlarmEventRecord(AgRoot, Serializer):
    def __init__(self, id: str, res_type_id: str, res_id: str,
                 alarm_def_id: str, probable_cause_id: str,
                 raised_time: str,
                 perc_severity: PerceivedSeverityEnum =
                 PerceivedSeverityEnum.WARNING
                 ) -> None:
        super().__init__()
        self.alarmEventRecordId = id
        self.resourceTypeId = res_type_id
        self.resourceId = res_id
        self.alarmDefinitionId = alarm_def_id
        self.probableCauseId = probable_cause_id
        self.perceivedSeverity = perc_severity
        self.alarmRaisedTime = raised_time
        self.alarmChangedTime = ''
        self.alarmAcknowledgeTime = ''
        self.alarmAcknowledged = False
        self.extensions = []


class ProbableCause(AgRoot, Serializer):
    def __init__(self, id: str, name: str, desc: str = '') -> None:
        super().__init__()
        self.probableCauseId = id
        self.name = name
        self.description = desc


class AlarmLastChangeEnum(str, Enum):
    ADDED = 'ADDED'
    DELETED = 'DELETED'
    MODIFYED = 'MODIFYED'


class ClearingTypeEnum(str, Enum):
    AUTOMATIC = 'AUTOMATIC'
    MANUAL = 'MANUAL'


class AlarmDefinition(AgRoot, Serializer):
    def __init__(self, id: str, name: str, last_change: AlarmLastChangeEnum,
                 desc: str, prop_action: str, clearing_type: ClearingTypeEnum,
                 pk_noti_field: str) -> None:
        super().__init__()
        self.alarmDefinitionId = id
        self.alarmName = name
        self.alarmLastChange = last_change
        self.alarmDescription = desc
        self.proposedRepairActions = prop_action
        self.clearingType = clearing_type
        self.managementInterfaceId = "O2IMS"
        self.pkNotificationField = pk_noti_field
        self.alarmAdditionalFields = ""


class AlarmDictionary(AgRoot, Serializer):
    def __init__(self, id: str) -> None:
        super().__init__()
        self.id = id
        self.alarmDictionaryVersion = ""
        self.alarmDictionarySchemaVersion = ""
        self.entityType = ""
        self.vendor = ""
        self.managementInterfaceId = "O2IMS"
        self.pkNotificationField = ""
        self.alarmDefinition = ""


class AlarmNotificationEventEnum(str, Enum):
    NEW = 0
    CHANGE = 1
    CLEAR = 2
    ACKNOWLEDGE = 3


class AlarmEvent2SMO(Serializer):
    def __init__(self, eventtype: AlarmNotificationEventEnum,
                 id: str, ref: str, updatetime: str) -> None:
        self.notificationEventType = eventtype
        self.objectRef = ref
        self.id = id
        self.updatetime = updatetime


class AlarmSubscription(AgRoot, Serializer):
    def __init__(self, id: str, callback: str, consumersubid: str = '',
                 filter: str = '') -> None:
        super().__init__()
        self.alarmSubscriptionId = id
        self.version_number = 0
        self.callback = callback
        self.consumerSubscriptionId = consumersubid
        self.filter = filter


class AlarmEventNotification(AgRoot, Serializer):
    def __init__(self, alarm: AlarmEventRecord, to_smo: AlarmEvent2SMO,
                 consumersubid: str) -> None:
        super().__init__()
        self.globalCloudId = ''
        self.consumerSubscriptionId = consumersubid
        self._convert_params(alarm, to_smo)

    def _convert_params(self, alarm: AlarmEventRecord, to_smo: AlarmEvent2SMO):
        self.notificationEventType = to_smo.notificationEventType
        self.objectRef = to_smo.objectRef

        self.alarmEventRecordId = alarm.alarmEventRecordId
        self.resourceTypeId = alarm.resourceTypeId
        self.resourceId = alarm.resourceId
        self.alarmDefinitionId = alarm.alarmDefinitionId
        self.probableCauseId = alarm.probableCauseId
        self.perceivedSeverity = alarm.perceivedSeverity
        self.alarmRaisedTime = alarm.alarmRaisedTime
        self.alarmChangedTime = alarm.alarmChangedTime
        self.alarmAcknowledgeTime = alarm.alarmAcknowledgeTime
        self.alarmAcknowledged = alarm.alarmAcknowledged
        self.extensions = []
