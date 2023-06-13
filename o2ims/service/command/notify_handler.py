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

# from o2common.config import conf
from o2common.domain.filter import gen_orm_filter
from o2common.service.unit_of_work import AbstractUnitOfWork
from o2common.adapter.notifications import AbstractNotifications

from o2ims.domain import commands, ocloud
from o2ims.domain.subscription_obj import Subscription, Message2SMO, \
    NotificationEventEnum

from o2common.helper import o2logging
logger = o2logging.get_logger(__name__)


# # Maybe another MQ server
# r = redis.Redis(**config.get_redis_host_and_port())


def notify_change_to_smo(
    cmd: commands.PubMessage2SMO,
    uow: AbstractUnitOfWork,
    notifications: AbstractNotifications,
):
    logger.debug('In notify_change_to_smo')
    msg_type = cmd.type
    if msg_type == 'ResourceType':
        _notify_resourcetype(uow, notifications, cmd.data)
    elif msg_type == 'ResourcePool':
        _notify_resourcepool(uow, notifications, cmd.data)
    elif msg_type == 'Dms':
        _notify_dms(uow, notifications, cmd.data)
    elif msg_type == 'Resource':
        _notify_resource(uow, notifications, cmd.data)


def __get_object_type_and_value(sub_filter):
    exprs = sub_filter.split(';')
    for expr in exprs:
        items = expr.strip(' ()').split(',')
        item_key = items[1].strip()
        if item_key == 'objectType':
            return True, items[2].strip()
    return False, ''


def handle_filter(filter: str, f_type: str):
    print(filter)
    if not filter:
        return

    filter_list = filter.strip(' []').split('|')
    if not filter_list:
        return

    match_type_count = 0
    filters = []
    for sub_filter in filter_list:
        objectType, objectTypeValue = __get_object_type_and_value(sub_filter)
        if objectTypeValue == f_type:
            match_type_count += 1
            filters.append(sub_filter)
        elif not objectType and f_type == 'ResourceInfo':
            match_type_count += 1
            filters.append(sub_filter)

    return match_type_count, filters


def check_filters(filters, sub_data, uow_cls, obj_cls, attr_id, id):
    for filter in filters[1]:
        logger.debug(f'filter: {filter}')
        try:
            args = gen_orm_filter(obj_cls, filter)
        except KeyError:
            logger.warning(
                'Subscription {} filter {} has wrong attribute '
                'name or value. Ignore the filter.'.format(
                    sub_data['subscriptionId'],
                    sub_data['filter']))
            continue
        logger.debug(f'args: {args}')

        if len(args) == 0 and 'objectType' in filter:
            return False

        args.append(attr_id == id)
        obj_count, _ = uow_cls.list_with_count(*args)
        if obj_count > 0:
            return True
    return False


def _notify_resourcetype(uow, notifications, data):
    with uow:
        resource_type = uow.resource_types.get(data.id)
        if resource_type is None:
            logger.warning('ResourceType {} does not exists.'.format(data.id))
            return

        resource_type_dict = resource_type.get_notification_dict()

        subs = uow.subscriptions.list()
        for sub in subs:
            sub_data = sub.serialize()
            logger.debug('Subscription: {}'.format(sub_data['subscriptionId']))
            filters = handle_filter(sub_data['filter'], 'ResourceTypeInfo')
            logger.debug(f'filters: {filters}, sub_data: {sub_data}')

            if not filters or filters[0] == 0 or check_filters(
                filters, sub_data, uow.resource_types, ocloud.ResourceType,
                    ocloud.ResourceType.resourceTypeId, data.id):
                callback_smo(notifications, sub, data, resource_type_dict)
                continue

            logger.info('Subscription {} filter hit, skip ResourceType {}.'
                        .format(sub_data['subscriptionId'], data.id))


def _notify_resourcepool(uow, notifications, data):
    with uow:
        resource_pool = uow.resource_pools.get(data.id)
        if resource_pool is None:
            logger.warning('ResourcePool {} does not exists.'.format(data.id))
            return

        resource_pool_dict = resource_pool.get_notification_dict()

        subs = uow.subscriptions.list()
        for sub in subs:
            sub_data = sub.serialize()
            logger.debug('Subscription: {}'.format(sub_data['subscriptionId']))
            filters = handle_filter(sub_data['filter'], 'ResourcePoolInfo')
            logger.debug(f'filters: {filters}, sub_data: {sub_data}')

            if not filters or filters[0] == 0 or check_filters(
                filters, sub_data, uow.resource_pools, ocloud.ResourcePool,
                    ocloud.ResourcePool.resourcePoolId, data.id):
                callback_smo(notifications, sub, data, resource_pool_dict)
                continue

            logger.info('Subscription {} filter hit, skip ResourcePool {}.'
                        .format(sub_data['subscriptionId'], data.id))


def _notify_dms(uow, notifications, data):
    with uow:
        dms = uow.deployment_managers.get(data.id)
        if dms is None:
            logger.warning(
                'DeploymentManager {} does not exists.'.format(data.id))
            return

        dms_dict = dms.get_notification_dict()

        subs = uow.subscriptions.list()
        for sub in subs:
            sub_data = sub.serialize()
            logger.debug('Subscription: {}'.format(sub_data['subscriptionId']))
            filters = handle_filter(
                sub_data['filter'], 'DeploymentManagerInfo')
            logger.debug(f'filters: {filters}, sub_data: {sub_data}')

            if not filters or filters[0] == 0 or check_filters(
                    filters, sub_data, uow.deployment_managers,
                    ocloud.DeploymentManager,
                    ocloud.DeploymentManager.deploymentManagerId, data.id):
                callback_smo(notifications, sub, data, dms_dict)
                continue

            logger.info('Subscription {} filter hit, skip '
                        'DeploymentManager {}.'
                        .format(sub_data['subscriptionId'], data.id))


def _notify_resource(uow, notifications, data):
    with uow:
        resource = uow.resources.get(data.id)
        if resource is None:
            logger.warning('Resource {} does not exists.'.format(data.id))
            return
        res_pool_id = resource.serialize()['resourcePoolId']
        logger.debug('res pool id is {}'.format(res_pool_id))

        res_dict = resource.get_notification_dict()

        subs = uow.subscriptions.list()
        for sub in subs:
            sub_data = sub.serialize()
            logger.debug('Subscription: {}'.format(sub_data['subscriptionId']))
            filters = handle_filter(sub_data['filter'], 'ResourceInfo')
            if not filters or filters[0] == 0:
                callback_smo(notifications, sub, data, res_dict)
                continue
            if filters[0] > 0 and not filters[1]:
                continue
            filter_hit = False
            for filter in filters[1]:
                try:
                    args = gen_orm_filter(ocloud.Resource, filter)
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
                args.append(ocloud.Resource.resourceId == data.id)
                obj_count, _ = uow.resources.list_with_count(
                    res_pool_id, *args)
                if obj_count > 0:
                    filter_hit = True
                    break
            if filter_hit:
                logger.info('Subscription {} filter hit, skip Resource {}.'
                            .format(sub_data['subscriptionId'], data.id))
            else:
                callback_smo(notifications, sub, data, res_dict)


def callback_smo(notifications: AbstractNotifications, sub: Subscription,
                 msg: Message2SMO, obj_dict: dict = None):
    sub_data = sub.serialize()
    callback = {
        'consumerSubscriptionId': sub_data['consumerSubscriptionId'],
        'notificationEventType': msg.notificationEventType,
        'objectRef': msg.objectRef,
        'updateTime': msg.updatetime
    }
    if msg.notificationEventType in [NotificationEventEnum.DELETE,
                                     NotificationEventEnum.MODIFY]:
        callback['priorObjectState'] = json.dumps(obj_dict)
    if msg.notificationEventType in [NotificationEventEnum.CREATE,
                                     NotificationEventEnum.MODIFY]:
        callback['postObjectState'] = json.dumps(obj_dict)
    if msg.notificationEventType == NotificationEventEnum.DELETE:
        callback.pop('objectRef')
    logger.info('callback URL: {}'.format(sub_data['callback']))
    logger.debug('callback data: {}'.format(json.dumps(callback)))

    return notifications.send(sub_data['callback'], callback)
