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
from o2ims.domain.subscription_obj import Subscription, Message2SMO

from o2common.helper import o2logging
logger = o2logging.get_logger(__name__)

# # Maybe another MQ server
# r = redis.Redis(**config.get_redis_host_and_port())


def notify_change_to_smo(
    cmd: commands.PubMessage2SMO,
    uow: AbstractUnitOfWork,
):
    logger.info('In notify_change_to_smo')
    data = cmd.data
    with uow:
        subs = uow.subscriptions.list()
        for sub in subs:
            sub_data = sub.serialize()
            logger.debug('Subscription: {}'.format(sub_data['subscriptionId']))

            try:
                resource_filter = json.loads(sub_data['filter'])
                if len(resource_filter) > 0:
                    resource = uow.resources.get(data.id)
                    logger.debug(type(resource))
                    if resource:  # TODO deal with resource is empty
                        res_type_id = resource.serialize()['resourceTypeId']
                        resourcetype = uow.resource_types.get(res_type_id)
                        logger.debug(resourcetype.name)
                        if resourcetype.name not in resource_filter:
                            continue
            except json.decoder.JSONDecodeError as err:
                logger.warning(
                    'subscription filter decode json failed: {}'.format(err))

            callback_smo(sub, data)


def callback_smo(sub: Subscription, msg: Message2SMO):
    sub_data = sub.serialize()
    callback_data = json.dumps({
        'consumerSubscriptionId': sub_data['consumerSubscriptionId'],
        'notificationEventType': msg.notificationEventType,
        'objectRef': msg.objectRef,
        'updateTime': msg.updatetime
    })
    logger.info('URL: {}, data: {}'.format(
        sub_data['callback'], callback_data))
    # r.publish(sub_data['subscriptionId'], json.dumps({
    #     'consumerSubscriptionId': sub_data['consumerSubscriptionId'],
    #     'notificationEventType': msg.notificationEventType,
    #     'objectRef': msg.objectRef
    # }))
    # try:
    #     headers = {'User-Agent': 'Mozilla/5.0'}
    #     resp = requests.post(sub_data['callback'], data=callback_data,
    #                          headers=headers)
    #     if resp.status_code == 202 or resp.status_code == 200:
    #         logger.info('Notify to SMO successed')
    #         return
    #     logger.error('Response code is: {}'.format(resp.status_code))
    # except requests.exceptions.HTTPError as err:
    #     logger.error('request smo error: {}'.format(err))
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
