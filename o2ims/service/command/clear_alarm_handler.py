# Copyright (C) 2024 Wind River Systems, Inc.
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

import json

from o2common.adapter.notifications import AbstractNotifications
from o2common.config import conf
from o2common.domain.filter import gen_orm_filter
from o2common.helper import o2logging
from o2common.service.unit_of_work import AbstractUnitOfWork
from o2ims.adapter.clients.fault_client import StxAlarmClient
from o2ims.domain import commands, alarm_obj
logger = o2logging.get_logger(__name__)


def clear_alarm_event(
    cmd: commands.PubAlarm2SMO,
    uow: AbstractUnitOfWork,
    notifications: AbstractNotifications,
):
    """
    Clears an alarm event and notifies relevant subscribers.

    This method performs the following steps:
    1. Retrieves data from the command object and initializes the fault client.
    2. Uses the Unit of Work pattern to find and delete the corresponding
       alarm event record.
    3. Updates the alarm event record's hash, extensions, changed time,
       and perceived severity.
    4. Commits the changes to the database.
    5. Finds and processes all alarm subscriptions, deciding whether to
       send notifications based on subscription filters.

    Parameters:
    - cmd (commands.PubAlarm2SMO): Command object containing the alarm
      event data.
    - uow (AbstractUnitOfWork): Unit of Work object for managing
      database transactions.
    - notifications (AbstractNotifications): Abstract notifications
      object for sending notifications.

    Exceptions:
    - Any exceptions that might occur during database operations or
      notification sending.
    """
    fault_client = StxAlarmClient(uow)
    data = cmd.data
    with uow:
        alarm_event_record = uow.alarm_event_records.get(data.id)
        alarm = fault_client.delete(alarm_event_record.alarmEventRecordId)
        alarm_event_record.hash = alarm.hash
        alarm_event_record.extensions = json.dumps(alarm.filtered)
        alarm_event_record.alarmClearedTime = alarm.updatetime.\
            strftime("%Y-%m-%dT%H:%M:%S")
        alarm_event_record.perceivedSeverity = \
            alarm_obj.PerceivedSeverityEnum.CLEARED

        uow.alarm_event_records.update(alarm_event_record)

        uow.commit()

        alarm = uow.alarm_event_records.get(data.id)
        subs = uow.alarm_subscriptions.list()
        for sub in subs:
            sub_data = sub.serialize()
            logger.debug('Alarm Subscription: {}'.format(
                sub_data['alarmSubscriptionId']))

            if not sub_data.get('filter', None):
                callback_smo(notifications, sub, data, alarm)
                continue
            try:
                args = gen_orm_filter(alarm_obj.AlarmEventRecord,
                                      sub_data['filter'])
            except KeyError:
                logger.warning(
                    'Alarm Subscription {} filter {} has wrong attribute '
                    'name or value. Ignore the filter'.format(
                        sub_data['alarmSubscriptionId'],
                        sub_data['filter']))
                callback_smo(notifications, sub, data, alarm)
                continue
            args.append(alarm_obj.AlarmEventRecord.
                        alarmEventRecordId == data.id)
            count, _ = uow.alarm_event_records.list_with_count(*args)
            if count != 0:
                logger.debug(
                    'Alarm Event {} skip for subscription {} because of '
                    'the filter.'
                    .format(data.id, sub_data['alarmSubscriptionId']))
                continue
            callback_smo(notifications, sub, data, alarm)


def callback_smo(notifications: AbstractNotifications,
                 sub: alarm_obj.AlarmSubscription,
                 msg: alarm_obj.AlarmEvent2SMO,
                 alarm: alarm_obj.AlarmEventRecord):
    sub_data = sub.serialize()
    alarm_data = alarm.serialize()
    callback = {
        'globalCloudID': conf.DEFAULT.ocloud_global_id,
        'consumerSubscriptionId': sub_data['consumerSubscriptionId'],
        'notificationEventType': msg.notificationEventType,
        'objectRef': msg.objectRef,
        'alarmEventRecordId': alarm_data['alarmEventRecordId'],
        'resourceTypeID': alarm_data['resourceTypeId'],
        'resourceID': alarm_data['resourceId'],
        'alarmDefinitionID': alarm_data['alarmDefinitionId'],
        'probableCauseID': alarm_data['probableCauseId'],
        'alarmRaisedTime': alarm_data['alarmRaisedTime'],
        'alarmChangedTime': alarm_data['alarmChangedTime'],
        'alarmAcknowledgeTime': alarm_data['alarmAcknowledgeTime'],
        'alarmAcknowledged': alarm_data['alarmAcknowledged'],
        'perceivedSeverity': alarm_data['perceivedSeverity'],
        'extensions': json.loads(alarm_data['extensions'])
    }
    logger.info('callback URL: {}'.format(sub_data['callback']))
    logger.debug('callback data: {}'.format(json.dumps(callback)))

    return notifications.send(sub_data['callback'], callback)
