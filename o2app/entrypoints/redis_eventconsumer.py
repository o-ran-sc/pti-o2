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

# import json
import redis
import json
from o2app import bootstrap
from o2common.config import config
# from o2common.domain import commands
from o2dms.domain import commands
from o2ims.domain import commands as imscmd

from o2common.helper import o2logging
from o2ims.domain.subscription_obj import Message2SMO, NotificationEventEnum, RegistrationMessage
logger = o2logging.get_logger(__name__)

r = redis.Redis(**config.get_redis_host_and_port())

apibase = config.get_o2ims_api_base()


def main():
    logger.info("Redis pubsub starting")
    bus = bootstrap.bootstrap()
    pubsub = r.pubsub(ignore_subscribe_messages=True)
    pubsub.subscribe("NfDeploymentStateChanged")
    pubsub.subscribe('ResourceChanged')
    pubsub.subscribe('ConfigurationChanged')
    pubsub.subscribe('OcloudChanged')

    for m in pubsub.listen():
        try:
            handle_dms_changed(m, bus)
        except Exception as ex:
            logger.warning("{}".format(str(ex)))
            continue


def handle_dms_changed(m, bus):
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
    elif channel == 'ResourceChanged':
        datastr = m['data']
        data = json.loads(datastr)
        logger.info('ResourceChanged with cmd:{}'.format(data))
        ref = apibase + '/resourcePools/' + data['resourcePoolId'] +\
            '/resources/' + data['id']
        cmd = imscmd.PubMessage2SMO(data=Message2SMO(
            id=data['id'], ref=ref,
            eventtype=data['notificationEventType'],
            updatetime=data['updatetime']))
        bus.handle(cmd)
    elif channel == 'ConfigurationChanged':
        datastr = m['data']
        data = json.loads(datastr)
        logger.info('ConfigurationChanged with cmd:{}'.format(data))
        cmd = imscmd.Register2SMO(data=RegistrationMessage(id=data['id']))
        bus.handle(cmd)
    elif channel == 'OcloudChanged':
        datastr = m['data']
        data = json.loads(datastr)
        logger.info('OcloudChanged with cmd:{}'.format(data))
        if data['notificationEventType'] == NotificationEventEnum.CREATE:
            cmd = imscmd.Register2SMO(data=RegistrationMessage(is_all=True))
            bus.handle(cmd)
    else:
        logger.info("unhandled:{}".format(channel))


if __name__ == "__main__":
    main()
