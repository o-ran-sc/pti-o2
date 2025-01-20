# Copyright (C) 2021-2024 Wind River Systems, Inc.
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

# import json

import redis
import json

from o2app import bootstrap
from o2common.adapter.notifications import SmoNotifications
from o2common.config import config
from o2common.helper import o2logging
from o2dms.domain import commands
from o2ims.domain import commands as imscmd
from o2ims.domain.subscription_obj import Message2SMO, RegistrationMessage, \
    NotificationEventEnum
from o2ims.domain.alarm_obj import AlarmEvent2SMO

logger = o2logging.get_logger(__name__)

r = redis.Redis(**config.get_redis_host_and_port())

apibase = config.get_o2ims_api_base()
api_monitoring_base = config.get_o2ims_monitoring_api_base()
monitor_api_version = config.get_o2ims_monitoring_api_v1()
inventory_api_version = config.get_o2ims_inventory_api_v1()


def main():
    logger.info("Redis pubsub starting")

    notifications = SmoNotifications()
    bus = bootstrap.bootstrap(notifications=notifications)

    pubsub = r.pubsub(ignore_subscribe_messages=True)
    pubsub.subscribe("NfDeploymentStateChanged")
    pubsub.subscribe('OcloudChanged')
    pubsub.subscribe('ResourceTypeChanged')
    pubsub.subscribe('ResourcePoolChanged')
    pubsub.subscribe('DmsChanged')
    pubsub.subscribe('ResourceChanged')
    pubsub.subscribe('AlarmEventChanged')
    pubsub.subscribe('AlarmEventCleared')
    pubsub.subscribe('AlarmEventPurged')

    for m in pubsub.listen():
        try:
            handle_changed(m, bus)
        except Exception as ex:
            logger.warning("{}".format(str(ex)))
            continue


def handle_changed(m, bus):
    logger.info("handling %s", m)
    channel = m['channel'].decode("UTF-8")
    if channel == "NfDeploymentStateChanged":
        datastr = m['data']
        data = json.loads(datastr)
        logger.info('HandleNfDeploymentStateChanged with cmd:{}'.format(data))
        cmd = commands.HandleNfDeploymentStateChanged(
            NfDeploymentId=data['NfDeploymentId'],
            FromState=data['FromState'],
            ToState=data['ToState']
        )
        bus.handle(cmd)
    elif channel == 'ResourceTypeChanged':
        datastr = m['data']
        data = json.loads(datastr)
        logger.info('ResourceTypeChanged with cmd:{}'.format(data))
        ref = apibase + inventory_api_version + '/resourceTypes/' + \
            data['id']
        cmd = imscmd.PubMessage2SMO(data=Message2SMO(
            id=data['id'], ref=ref,
            eventtype=data['notificationEventType'],
            updatetime=data['updatetime']),
            type='ResourceType')
        bus.handle(cmd)
    elif channel == 'ResourcePoolChanged':
        datastr = m['data']
        data = json.loads(datastr)
        logger.info('ResourcePoolChanged with cmd:{}'.format(data))
        ref = apibase + inventory_api_version + '/resourcePools/' + \
            data['id']
        cmd = imscmd.PubMessage2SMO(data=Message2SMO(
            id=data['id'], ref=ref,
            eventtype=data['notificationEventType'],
            updatetime=data['updatetime']),
            type='ResourcePool')
        bus.handle(cmd)
    elif channel == 'DmsChanged':
        datastr = m['data']
        data = json.loads(datastr)
        logger.info('ResourceChanged with cmd:{}'.format(data))
        ref = apibase + inventory_api_version + '/deploymentManagers/' + \
            data['id']
        cmd = imscmd.PubMessage2SMO(data=Message2SMO(
            id=data['id'], ref=ref,
            eventtype=data['notificationEventType'],
            updatetime=data['updatetime']),
            type='Dms')
        bus.handle(cmd)
    elif channel == 'ResourceChanged':
        datastr = m['data']
        data = json.loads(datastr)
        logger.info('ResourceChanged with cmd:{}'.format(data))
        ref = apibase + inventory_api_version + '/resourcePools/' + \
            data['resourcePoolId'] + '/resources/' + data['id']
        cmd = imscmd.PubMessage2SMO(data=Message2SMO(
            id=data['id'], ref=ref,
            eventtype=data['notificationEventType'],
            updatetime=data['updatetime']),
            type='Resource')
        bus.handle(cmd)
    elif channel == 'OcloudChanged':
        datastr = m['data']
        data = json.loads(datastr)
        logger.info('OcloudChanged with cmd:{}'.format(data))
        if data['notificationEventType'] == NotificationEventEnum.CREATE:
            cmd = imscmd.Register2SMO(data=RegistrationMessage(
                id=data['id'], eventtype=data['notificationEventType'],
                updatetime=data['updatetime']))
        elif data['notificationEventType'] == NotificationEventEnum.MODIFY:
            ref = apibase + inventory_api_version
            cmd = imscmd.PubMessage2SMO(data=Message2SMO(
                id=data['id'], ref=ref,
                eventtype=data['notificationEventType'],
                updatetime=data['updatetime']),
                type='OCloud')
        bus.handle(cmd)
    elif channel == 'AlarmEventChanged':
        datastr = m['data']
        data = json.loads(datastr)
        logger.info('AlarmEventChanged with cmd:{}'.format(data))
        ref = api_monitoring_base + \
            monitor_api_version + '/alarms/' + data['id']
        cmd = imscmd.PubAlarm2SMO(data=AlarmEvent2SMO(
            id=data['id'], ref=ref,
            eventtype=data['notificationEventType'],
            updatetime=data['updatetime']))
        bus.handle(cmd)
    elif channel == 'AlarmEventCleared':
        datastr = m['data']
        data = json.loads(datastr)
        logger.info('AlarmEventCleared with cmd:{}'.format(data))
        cmd = imscmd.ClearAlarmEvent(data=AlarmEvent2SMO(
            id=data['id'], ref="", eventtype=data['notificationEventType'],
            updatetime=data['updatetime']))
        bus.handle(cmd)
    elif channel == 'AlarmEventPurged':
        datastr = m['data']
        data = json.loads(datastr)
        logger.info('AlarmEventPurged with cmd:{}'.format(data))
        cmd = imscmd.PurgeAlarmEvent(data=AlarmEvent2SMO(
            id=data['id'], ref="", eventtype=data['notificationEventType'],
            updatetime=data['updatetime']))
        bus.handle(cmd)
    else:
        logger.info("unhandled:{}".format(channel))


if __name__ == "__main__":
    main()
