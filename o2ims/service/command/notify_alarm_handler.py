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

import json
# import redis
# import requests
from urllib.parse import urlparse

# from o2common.config import config
from o2common.service.unit_of_work import AbstractUnitOfWork
from o2ims.domain import commands
from o2ims.domain.alarm_obj import AlarmSubscription, AlarmEvent2SMO
import ssl
from o2common.service.command.handler import get_https_conn_default
from o2common.service.command.handler import get_http_conn
from o2common.service.command.handler import get_https_conn_selfsigned
from o2common.service.command.handler import post_data
from o2common.helper import o2logging
logger = o2logging.get_logger(__name__)


def notify_alarm_to_smo(
    cmd: commands.PubAlarm2SMO,
    uow: AbstractUnitOfWork,
):
    logger.info('In notify_alarm_to_smo')
    data = cmd.data
    with uow:
        subs = uow.alarm_subscriptions.list()
        for sub in subs:
            sub_data = sub.serialize()
            logger.debug('Alarm Subscription: {}'.format(
                sub_data['alarmSubscriptionId']))

            callback_smo(sub, data)


def callback_smo(sub: AlarmSubscription, msg: AlarmEvent2SMO):
    sub_data = sub.serialize()
    callback_data = json.dumps({
        'consumerSubscriptionId': sub_data['consumerSubscriptionId'],
        'notificationEventType': msg.notificationEventType,
        'objectRef': msg.objectRef,
        'updateTime': msg.updatetime
    })
    logger.info('URL: {}, data: {}'.format(
        sub_data['callback'], callback_data))
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
        logger.info(
            'Notify alarm post data with trusted ca failed: {}'.format(e))
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
