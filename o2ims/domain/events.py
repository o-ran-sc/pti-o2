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

# pylint: disable=too-few-public-methods
from dataclasses import dataclass, field
from datetime import datetime

from o2common.domain.events import Event
from o2ims.domain.subscription_obj import NotificationEventEnum
from o2ims.domain.alarm_obj import AlarmNotificationEventEnum


@dataclass
class OcloudChanged(Event):
    id: str
    notificationEventType: NotificationEventEnum
    updatetime: datetime.now()


@dataclass
class ResourceTypeChanged(Event):
    id: str
    notificationEventType: NotificationEventEnum
    updatetime: datetime.now()


@dataclass
class DmsChanged(Event):
    id: str
    notificationEventType: NotificationEventEnum
    updatetime: datetime.now()


@dataclass
class ResourcePoolChanged(Event):
    id: str
    notificationEventType: NotificationEventEnum
    updatetime: datetime.now()


@dataclass
class ResourceChanged(Event):
    id: str
    resourcePoolId: str
    notificationEventType: NotificationEventEnum
    updatetime: datetime.now()


@dataclass
class AlarmEventChanged(Event):
    id: str
    notificationEventType: AlarmNotificationEventEnum
    updatetime: datetime.now()


@dataclass
class AlarmEventCleared(Event):
    id: str
    notificationEventType: AlarmNotificationEventEnum
    updatetime: datetime = field(default_factory=datetime.now)


@dataclass
class AlarmEventPurged(Event):
    id: str
    notificationEventType: AlarmNotificationEventEnum
    updatetime: datetime = field(default_factory=datetime.now)
