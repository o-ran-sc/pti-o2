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

from o2common.config import config, conf
from o2common.domain.filter import gen_orm_filter
from o2common.service.unit_of_work import AbstractUnitOfWork
from o2common.adapter.notifications import AbstractNotifications

from o2ims.domain import commands, ocloud as cloud
from o2ims.domain.subscription_obj import Message2SMO, NotificationEventEnum

from .notify_handler import handle_filter, callback_smo

from o2common.helper import o2logging
logger = o2logging.get_logger(__name__)

apibase = config.get_o2ims_api_base()
api_monitoring_base = config.get_o2ims_monitoring_api_base()
inventory_api_version = config.get_o2ims_inventory_api_v1()


def registry_to_smo(
    cmd: commands.Register2SMO,
    uow: AbstractUnitOfWork,
    notifications: AbstractNotifications,
):
    logger.debug('In registry_to_smo')
    data = cmd.data
    logger.info('The Register2SMO notificationEventType is {}'.format(
        data.notificationEventType))
    with uow:
        ocloud = uow.oclouds.get(data.id)
        if ocloud is None:
            logger.warning('Ocloud {} does not exists.'.format(data.id))
            return
        logger.debug('O-Cloud Global UUID: {}'.format(ocloud.globalCloudId))
        ocloud_dict = ocloud.get_notification_dict()
        if data.notificationEventType == NotificationEventEnum.CREATE:
            register_smo(notifications, ocloud_dict)
        elif data.notificationEventType in [NotificationEventEnum.MODIFY,
                                            NotificationEventEnum.DELETE]:
            _notify_ocloud(uow, data, ocloud_dict)


class RegIMSToSMOExp(Exception):
    def __init__(self, value):
        self.value = value


def register_smo(notifications, ocloud_data):
    call_res = call_smo(notifications, ocloud_data)
    logger.debug('Call SMO response is {}'.format(call_res))
    if call_res is True:
        logger.info('Register to smo success response')
    else:
        raise RegIMSToSMOExp('Register o2ims to SMO failed')
    # TODO: record the result for the smo register


def _notify_ocloud(uow, data, ocloud_dict):
    ref = api_monitoring_base + inventory_api_version
    msg = Message2SMO(
        eventtype=data.notificationEventType, id=data.id,
        ref=ref, updatetime=data.updatetime)
    ocloud_dict.pop('globalCloudId')
    subs = uow.subscriptions.list()
    for sub in subs:
        sub_data = sub.serialize()
        logger.debug('Subscription: {}'.format(sub_data['subscriptionId']))
        filters = handle_filter(sub_data['filter'], 'CloudInfo')
        if not filters:
            callback_smo(sub, msg, ocloud_dict)
            continue
        filter_hit = False
        for filter in filters:
            try:
                args = gen_orm_filter(cloud.Ocloud, filter)
            except KeyError:
                logger.warning(
                    'Subscription {} filter {} has wrong attribute '
                    'name or value. Ignore the filter.'.format(
                        sub_data['subscriptionId'],
                        sub_data['filter']))
                continue
            if len(args) == 0 and 'objectType' in filter:
                filter_hit = True
                break
            args.append(cloud.Ocloud.oCloudId == data.id)
            ret = uow.oclouds.list(*args)
            if ret.count() > 0:
                filter_hit = True
                break
        if filter_hit:
            logger.info('Subscription {} filter hit, skip oCloud {}.'
                        .format(sub_data['subscriptionId'], data.id))
        else:
            callback_smo(sub, msg, ocloud_dict)


def call_smo(notifications: AbstractNotifications, reg_data: dict):
    smo_token = conf.DEFAULT.smo_token_data
    smo_token_info = {
        'iss': 'o2ims',
        'aud': 'smo',
        'smo_token_payload': smo_token,
        'smo_token_type': 'jwt',
        'smo_token_expiration': '',
        'smo_token_algo': 'RS256'
    }

    callback = {
        'globalCloudId': reg_data['globalCloudId'],
        'oCloudId': reg_data['oCloudId'],
        'IMS_EP': config.get_api_url(),
        'smo_token_data': smo_token_info
    }
    logger.info('callback URL: {}'.format(conf.DEFAULT.smo_register_url))
    logger.debug('callback data: {}'.format(json.dumps(callback)))
    return notifications.send(conf.DEFAULT.smo_register_url, callback)
