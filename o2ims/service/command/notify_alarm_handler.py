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

import json
# import redis
# import requests
import http.client
from urllib.parse import urlparse

# from o2common.config import config
from o2common.service.unit_of_work import AbstractUnitOfWork
from o2ims.domain import commands
from o2ims.domain.alarm_obj import AlarmSubscription, AlarmEvent2SMO

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
    conn = http.client.HTTPConnection(o.netloc)
    headers = {'Content-type': 'application/json'}
    conn.request('POST', o.path, callback_data, headers)
    resp = conn.getresponse()
    data = resp.read().decode('utf-8')
    # json_data = json.loads(data)
    if resp.status == 202 or resp.status == 200:
        logger.info('Notify to SMO successed, response code {} {}, data {}'.
                    format(resp.status, resp.reason, data))
        return
    logger.error('Response code is: {}'.format(resp.status))
