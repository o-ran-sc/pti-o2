# Copyright (C) 2021-2022 Wind River Systems, Inc.
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

# import redis
# import requests
import json

from o2common.config import conf
from o2common.domain.filter import gen_orm_filter
from o2common.service.unit_of_work import AbstractUnitOfWork
from o2common.adapter.notifications import AbstractNotifications

from o2ims.domain import commands
from o2ims.domain.alarm_obj import AlarmSubscription, AlarmEvent2SMO, \
    AlarmEventRecord

from o2common.helper import o2logging
logger = o2logging.get_logger(__name__)


def notify_alarm_to_smo(
    cmd: commands.PubAlarm2SMO,
    uow: AbstractUnitOfWork,
    notifications: AbstractNotifications,
):
    logger.debug('In notify_alarm_to_smo')
    data = cmd.data
    with uow:
        alarm = uow.alarm_event_records.get(data.id)
        if alarm is None:
            logger.warning('Alarm Event {} does not exists.'.format(data.id))
            return

        subs = uow.alarm_subscriptions.list()
        for sub in subs:
            sub_data = sub.serialize()
            logger.debug('Alarm Subscription: {}'.format(
                sub_data['alarmSubscriptionId']))

            if not sub_data.get('filter', None):
                callback_smo(notifications, sub, data, alarm)
                continue
            try:
                args = gen_orm_filter(AlarmEventRecord, sub_data['filter'])
            except KeyError:
                logger.warning(
                    'Alarm Subscription {} filter {} has wrong attribute '
                    'name or value. Ignore the filter'.format(
                        sub_data['alarmSubscriptionId'],
                        sub_data['filter']))
                callback_smo(notifications, sub, data, alarm)
                continue
            args.append(AlarmEventRecord.alarmEventRecordId == data.id)
            ret = uow.alarm_event_records.list_with_count(*args)
            if ret[0] != 0:
                logger.debug(
                    'Alarm Event {} skip for subscription {} because of '
                    'the filter.'
                    .format(data.id, sub_data['alarmSubscriptionId']))
                continue
            callback_smo(notifications, sub, data, alarm)


def callback_smo(notifications: AbstractNotifications, sub: AlarmSubscription,
                 msg: AlarmEvent2SMO, alarm: AlarmEventRecord):
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
