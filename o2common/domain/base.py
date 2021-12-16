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

from datetime import datetime
from typing import List
from sqlalchemy.inspection import inspect
from sqlalchemy.exc import NoInspectionAvailable
from .events import Event


class AgRoot:

    events = []

    def __init__(self) -> None:
        self.hash = ""
        self.updatetime = datetime.now()
        self.createtime = datetime.now()
        self.events = []  # type: List[Event]
        # self.id = ""

    # def append_event(self, event: Event):
    #     self.events = self.events.append(event)


class Serializer(object):

    def serialize(self):
        try:
            # d = {c: getattr(self, c) for c in inspect(self).attrs.keys()}
            # if 'createtime' in d:
            #     d['createtime'] = d['createtime'].isoformat()
            # if 'updatetime' in d:
            #     d['updatetime'] = d['updatetime'].isoformat()
            # return d
            return {c: getattr(self, c) for c in inspect(self).attrs.keys()}
        except NoInspectionAvailable:
            return self.__dict__

    @staticmethod
    def serialize_list(li):
        return [m.serialize() for m in li]
