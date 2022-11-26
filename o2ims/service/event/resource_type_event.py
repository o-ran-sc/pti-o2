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

from o2common.helper import o2logging
logger = o2logging.get_logger(__name__)


def notify_resourcetype_change(
    event: events.ResourceTypeChanged,
    publish: Callable,
):
    logger.debug('In notify_resourcetype_change')
    publish("ResourceTypeChanged", event)
    logger.debug("published Resource Type Changed: {}".format(
        event.id))
