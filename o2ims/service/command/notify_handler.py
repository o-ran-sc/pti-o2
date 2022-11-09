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
import ssl
from urllib.parse import urlparse

# from o2common.config import config
from o2common.domain.filter import gen_orm_filter
from o2common.service.unit_of_work import AbstractUnitOfWork
from o2common.service.command.handler import get_https_conn_default
from o2common.service.command.handler import get_http_conn
from o2common.service.command.handler import get_https_conn_selfsigned
from o2common.service.command.handler import post_data

from o2ims.domain import commands, ocloud
from o2ims.domain.subscription_obj import Subscription, Message2SMO

from o2common.helper import o2logging
logger = o2logging.get_logger(__name__)


# # Maybe another MQ server
# r = redis.Redis(**config.get_redis_host_and_port())


def notify_change_to_smo(
    cmd: commands.PubMessage2SMO,
    uow: AbstractUnitOfWork,
):
    logger.debug('In notify_change_to_smo')
    data = cmd.data
    with uow:
        subs = uow.subscriptions.list()
        for sub in subs:
            sub_data = sub.serialize()
            logger.debug('Subscription: {}'.format(sub_data['subscriptionId']))
            resource = uow.resources.get(data.id)
            if resource is None:
                logger.debug('Resource {} does not exists.'.format(data.id))
                continue
            res_pool_id = resource.serialize()['resourcePoolId']
            logger.debug('res pool id is {}'.format(res_pool_id))
            if sub_data['filter'] is not None or sub_data['filter'] != '':
                try:
                    args = gen_orm_filter(ocloud.Resource, sub_data['filter'])
                except KeyError:
                    logger.error(
                        'Subscription {} filter {} has wrong attribute name '
                        'or value. Ignore the filter.'.format(
                            sub_data['subscriptionId'], sub_data['filter']))
                    callback_smo(sub, data)
                    continue
                args.append(ocloud.Resource.resourceId == data.id)
                ret = uow.resources.list_with_count(res_pool_id, *args)
                if ret[0] != 0:
                    logger.debug(
                        'Resource {} skip for subscription {} because of the '
                        'filter.'
                        .format(data.id, sub_data['subscriptionId']))
                    continue

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
    if o.scheme == 'https':
        conn = get_https_conn_default(o.netloc)
    else:
        conn = get_http_conn(o.netloc)
    try:
        rst, status = post_data(conn, o.path, callback_data)
        if rst is True:
            logger.info(
                'Notify to SMO successed with status: {}'.format(status))
            return
        logger.error('Notify Response code is: {}'.format(status))
    except ssl.SSLCertVerificationError as e:
        logger.debug(
            'Notify try to post data with trusted ca failed: {}'.format(e))
        if 'self signed' in str(e):
            conn = get_https_conn_selfsigned(o.netloc)
            try:
                return post_data(conn, o.path, callback_data)
            except Exception as e:
                logger.info(
                    'Notify post data with self-signed ca \
                    failed: {}'.format(e))
                # TODO: write the status to extension db table.
                return False
        return False
    except Exception as e:
        logger.critical('Notify except: {}'.format(e))
        return False
