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

from typing import Callable

from o2ims.domain import events

from o2common.helper import o2logging
logger = o2logging.get_logger(__name__)


def notify_alarm_event_change(
    event: events.AlarmEventChanged,
    publish: Callable,
):
    publish("AlarmEventChanged", event)
    logger.debug("published Alarm Event Changed: {}".format(
        event.id))


def notify_alarm_event_clear(
    event: events.AlarmEventCleared,
    publish: Callable,
):
    publish("AlarmEventCleared", event)
    logger.debug("published Alarm Event Cleared: {}".format(
        event.id))


def notify_alarm_event_purge(
    event: events.AlarmEventPurged,
    publish: Callable,
):
    publish("AlarmEventPurged", event)
    logger.debug("published Alarm Event Purged: {}".format(
        event.id))
