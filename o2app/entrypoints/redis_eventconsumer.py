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
from logging import log
import redis
import json
from o2app import bootstrap
from o2common.config import config
# from o2common.domain import commands
from o2dms.domain import commands
from o2dms.domain import events

from o2common.helper import o2logging
logger = o2logging.get_logger(__name__)

r = redis.Redis(**config.get_redis_host_and_port())


def main():
    logger.info("Redis pubsub starting")
    bus = bootstrap.bootstrap()
    pubsub = r.pubsub(ignore_subscribe_messages=True)
    pubsub.subscribe("NfDeploymentCreated")

    for m in pubsub.listen():
        try:
            handle_dms_changed(m, bus)
        except Exception as ex:
            logger.warning("{}".format(str(ex)))
            continue


def handle_dms_changed(m, bus):
    logger.info("handling %s", m)
    channel = m['channel'].decode("UTF-8")
    if channel == "NfDeploymentCreated":
        datastr = m['data']
        data = json.loads(datastr)
        logger.info('InstallNfDeployment with cmd:{}'.format(data))
        cmd = commands.InstallNfDeployment(NfDeploymentId = data['NfDeploymentId'])
        bus.handle(cmd)
    elif channel == "NfDeploymentUninstalling":
        datastr = m['data']
        data = json.loads(datastr)
        logger.info('UninstallNfDeployment with cmd:{}'.format(data))
        cmd = commands.UninstallNfDeployment(NfDeploymentId = data['NfDeploymentId'])
        bus.handle(cmd)
    elif channel == "NfDeploymentUninstalled":
        datastr = m['data']
        data = json.loads(datastr)
        logger.info('DeleteNfDeployment with cmd:{}'.format(data))
        cmd = commands.DeleteNfDeployment(NfDeploymentId = data['NfDeploymentId'])
        bus.handle(cmd)
    else:
        logger.info("unhandled:{}".format(channel))
    # data = json.loads(m["data"])
    # cmd = commands.UpdateDms(ref=data["dmsid"])
    # bus.handle(cmd)


if __name__ == "__main__":
    main()
