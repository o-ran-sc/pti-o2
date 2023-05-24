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


def _notify_resourcetype(uow, notifications, data):
    with uow:
        resource_type = uow.resource_types.get(data.id)
        if resource_type is None:
            logger.warning('ResourceType {} does not exists.'.format(data.id))
            return
        resource_type_dict = {
            'resourceTypeId': resource_type.resourceTypeId,
            'name': resource_type.name,
            'description': resource_type.description,
            'vendor': resource_type.vendor,
            'model': resource_type.model,
            'version': resource_type.version,
            # 'alarmDictionary': resource_type.alarmDictionary.serialize()
        }

        subs = uow.subscriptions.list()
        for sub in subs:
            sub_data = sub.serialize()
            logger.debug('Subscription: {}'.format(sub_data['subscriptionId']))
            filters = handle_filter(sub_data['filter'], 'ResourceTypeInfo')
            if not filters:
                callback_smo(notifications, sub, data, resource_type_dict)
                continue
            filter_hit = False
            for filter in filters:
                try:
                    args = gen_orm_filter(ocloud.ResourceType, filter)
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
                args.append(ocloud.ResourceType.resourceTypeId == data.id)
                obj_count, _ = uow.resource_types.list_with_count(*args)
                if obj_count > 0:
                    filter_hit = True
                    break
            if filter_hit:
                logger.info('Subscription {} filter hit, skip ResourceType {}.'
                            .format(sub_data['subscriptionId'], data.id))
            else:
                callback_smo(notifications, sub, data, resource_type_dict)


def _notify_resourcepool(uow, notifications, data):
    with uow:
        resource_pool = uow.resource_pools.get(data.id)
        if resource_pool is None:
            logger.warning('ResourcePool {} does not exists.'.format(data.id))
            return
        resource_pool_dict = {
            'resourcePoolId': resource_pool.resourcePoolId,
            'oCloudId': resource_pool.oCloudId,
            'globalLocationId': resource_pool.globalLocationId,
            'name': resource_pool.name,
            'description': resource_pool.description
        }

        subs = uow.subscriptions.list()
        for sub in subs:
            sub_data = sub.serialize()
            logger.debug('Subscription: {}'.format(sub_data['subscriptionId']))
            filters = handle_filter(sub_data['filter'], 'ResourcePoolInfo')
            if not filters:
                callback_smo(notifications, sub, data, resource_pool_dict)
                continue
            filter_hit = False
            for filter in filters:
                try:
                    args = gen_orm_filter(ocloud.ResourcePool, filter)
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
                args.append(ocloud.ResourcePool.resourcePoolId == data.id)
                obj_count, _ = uow.resource_pools.list_with_count(*args)
                if obj_count > 0:
                    filter_hit = True
                    break
            if filter_hit:
                logger.info('Subscription {} filter hit, skip ResourcePool {}.'
                            .format(sub_data['subscriptionId'], data.id))
            else:
                callback_smo(notifications, sub, data, resource_pool_dict)


def _notify_dms(uow, notifications, data):
    with uow:
        dms = uow.deployment_managers.get(data.id)
        if dms is None:
            logger.warning(
                'DeploymentManager {} does not exists.'.format(data.id))
            return
        dms_dict = {
            'deploymentManagerId': dms.deploymentManagerId,
            'name': dms.name,
            'description': dms.description,
            'oCloudId': dms.oCloudId,
            'serviceUri': dms.serviceUri
        }

        subs = uow.subscriptions.list()
        for sub in subs:
            sub_data = sub.serialize()
            logger.debug('Subscription: {}'.format(sub_data['subscriptionId']))
            filters = handle_filter(
                sub_data['filter'], 'DeploymentManagerInfo')
            if not filters:
                callback_smo(notifications, sub, data, dms_dict)
                continue
            filter_hit = False
            for filter in filters:
                try:
                    args = gen_orm_filter(ocloud.DeploymentManager, filter)
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
                args.append(
                    ocloud.DeploymentManager.deploymentManagerId == data.id)
                obj_count, _ = uow.deployment_managers.list_with_count(*args)
                if obj_count > 0:
                    filter_hit = True
                    break
            if filter_hit:
                logger.info('Subscription {} filter hit, skip '
                            'DeploymentManager {}.'
                            .format(sub_data['subscriptionId'], data.id))
            else:
                callback_smo(notifications, sub, data, dms_dict)


def _notify_resource(uow, notifications, data):
    with uow:
        resource = uow.resources.get(data.id)
        if resource is None:
            logger.warning('Resource {} does not exists.'.format(data.id))
            return
        res_pool_id = resource.serialize()['resourcePoolId']
        logger.debug('res pool id is {}'.format(res_pool_id))
        res_dict = {
            'resourceId': resource.resourceId,
            'description': resource.description,
            'resourceTypeId': resource.resourceTypeId,
            'resourcePoolId': resource.resourcePoolId,
            'globalAssetId': resource.globalAssetId
        }

        subs = uow.subscriptions.list()
        for sub in subs:
            sub_data = sub.serialize()
            logger.debug('Subscription: {}'.format(sub_data['subscriptionId']))
            filters = handle_filter(sub_data['filter'], 'ResourceInfo')
            if not filters:
                callback_smo(notifications, sub, data, res_dict)
                continue
            filter_hit = False
            for filter in filters:
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


def handle_filter(filter: str, f_type: str):
    if not filter:
        return
    filter_strip = filter.strip(' []')
    filter_list = filter_strip.split('|')
    filters = list()
    for sub_filter in filter_list:
        exprs = sub_filter.split(';')
        objectType = False
        objectTypeValue = ''
        for expr in exprs:
            expr_strip = expr.strip(' ()')
            items = expr_strip.split(',')
            item_key = items[1].strip()
            if item_key != 'objectType':
                continue
            objectType = True
            objectTypeValue = items[2].strip()
        if not objectType:
            if f_type == 'ResourceInfo':
                filters.append(sub_filter)
            continue
        if objectTypeValue == f_type:
            filters.append(sub_filter)
    return filters


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

    # Call SMO through the SMO callback url
    # o = urlparse(sub_data['callback'])
    # if o.scheme == 'https':
    #     conn = get_https_conn_default(o.netloc)
    # else:
    #     conn = get_http_conn(o.netloc)
    # try:
    #     rst, status = post_data(conn, o.path, callback_data)
    #     if rst is True:
    #         logger.info(
    #             'Notify to SMO successed with status: {}'.format(status))
    #         return
    #     logger.error('Notify Response code is: {}'.format(status))
    # except ssl.SSLCertVerificationError as e:
    #     logger.debug(
    #         'Notify try to post data with trusted ca failed: {}'.format(e))
    #     if 'self signed' in str(e):
    #         conn = get_https_conn_selfsigned(o.netloc)
    #         try:
    #             return post_data(conn, o.path, callback_data)
    #         except Exception as e:
    #             logger.info(
    #                 'Notify post data with self-signed ca \
    #                 failed: {}'.format(e))
    #             return False
    #     return False
    # except Exception as e:
    #     logger.critical('Notify except: {}'.format(e))
    #     return False
