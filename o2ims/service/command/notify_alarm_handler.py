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
import ssl
import json
from urllib.parse import urlparse

from o2common.config import conf
from o2common.domain.filter import gen_orm_filter
from o2common.service.unit_of_work import AbstractUnitOfWork
from o2common.service.command.handler import get_https_conn_default
from o2common.service.command.handler import get_http_conn
from o2common.service.command.handler import get_https_conn_selfsigned
from o2common.service.command.handler import post_data

from o2ims.domain import commands
from o2ims.domain.alarm_obj import AlarmSubscription, AlarmEvent2SMO, \
    AlarmEventRecord

from o2common.helper import o2logging
logger = o2logging.get_logger(__name__)


def notify_alarm_to_smo(
    cmd: commands.PubAlarm2SMO,
    uow: AbstractUnitOfWork,
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
                callback_smo(sub, data, alarm)
                continue
            try:
                args = gen_orm_filter(AlarmEventRecord, sub_data['filter'])
            except KeyError:
                logger.warning(
                    'Alarm Subscription {} filter {} has wrong attribute '
                    'name or value. Ignore the filter'.format(
                        sub_data['alarmSubscriptionId'],
                        sub_data['filter']))
                callback_smo(sub, data, alarm)
                continue
            args.append(AlarmEventRecord.alarmEventRecordId == data.id)
            ret = uow.alarm_event_records.list_with_count(*args)
            if ret[0] != 0:
                logger.debug(
                    'Alarm Event {} skip for subscription {} because of '
                    'the filter.'
                    .format(data.id, sub_data['alarmSubscriptionId']))
                continue
            callback_smo(sub, data, alarm)


def callback_smo(sub: AlarmSubscription, msg: AlarmEvent2SMO,
                 alarm: AlarmEventRecord):
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
    # logger.warning(callback)
    callback_data = json.dumps(callback)
    logger.info('URL: {}'.format(sub_data['callback']))
    logger.debug('callback data: {}'.format(callback_data))

    o = urlparse(sub_data['callback'])
    if o.scheme == 'https':
        conn = get_https_conn_default(o.netloc)
    else:
        conn = get_http_conn(o.netloc)
    try:
        rst, status = post_data(conn, o.path, callback_data)
        if rst is True:
            logger.info(
                'Notify alarm to SMO successed with status: {}'.format(status))
            return
        logger.error('Notify alarm Response code is: {}'.format(status))
    except ssl.SSLCertVerificationError as e:
        logger.debug(
            'Notify alarm try to post data with trusted ca \
                failed: {}'.format(e))
        if 'self signed' in str(e):
            conn = get_https_conn_selfsigned(o.netloc)
            try:
                return post_data(conn, o.path, callback_data)
            except Exception as e:
                logger.info(
                    'Notify alarm with self-signed ca failed: {}'.format(e))
                # TODO: write the status to extension db table.
                return False
        return False
    except Exception as e:
        logger.critical('Notify alarm except: {}'.format(e))
        return False
