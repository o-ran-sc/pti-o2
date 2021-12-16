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

from typing import Callable

from o2ims.domain import events
from o2common.config import config

from o2common.helper import o2logging
logger = o2logging.get_logger(__name__)

apibase = config.get_o2ims_api_base()


def notify_resource_change(
    event: events.ResourceChanged,
    publish: Callable,
):
    logger.info('In notify_resource_change')
    event.ref = apibase + '/resourcePools/' + event.resourcePoolId +\
        '/resources/' + event.id
    publish("NotifySmoChanged", event)
    logger.debug("published Resource Changed: {}".format(
        event.id))
