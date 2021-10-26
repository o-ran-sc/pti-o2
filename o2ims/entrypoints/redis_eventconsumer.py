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
import logging
import redis

from o2ims import bootstrap, config
from o2ims.domain import commands

logger = logging.getLogger(__name__)

r = redis.Redis(**config.get_redis_host_and_port())


def main():
    logger.info("Redis pubsub starting")
    bus = bootstrap.bootstrap()
    pubsub = r.pubsub(ignore_subscribe_messages=True)
    pubsub.subscribe("dms_changed")

    for m in pubsub.listen():
        handle_dms_changed(m, bus)


def handle_dms_changed(m, bus):
    logger.info("handling %s", m)
    data = json.loads(m["data"])
    cmd = commands.UpdateDms(ref=data["dmsid"])
    bus.handle(cmd)


if __name__ == "__main__":
    main()
