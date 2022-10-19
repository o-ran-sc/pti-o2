# Copyright (C) 2022 Wind River Systems, Inc.
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

from typing import List

from o2ims.domain import alarm_obj
from o2ims.domain.alarm_repo import AlarmDictionaryRepository
from o2common.helper import o2logging
logger = o2logging.get_logger(__name__)


class AlarmDictionaryConfigFileRepository(AlarmDictionaryRepository):
    def __init__(self):
        super().__init__()
        self.dictionary = {}

    def _add(self, alarm_dict: alarm_obj.AlarmDictionary):
        self.dictionary[alarm_dict.entityType] = alarm_dict

    def _get(self, alarm_entity_type) -> alarm_obj.AlarmDictionary:
        return self.dictionary[alarm_entity_type]

    def _list(self) -> List[alarm_obj.AlarmDictionary]:
        return [alarm_dict for alarm_dict in self.dictionary.items()]

    def _update(self, alarm_dict: alarm_obj.AlarmDictionary):
        self.dictionary[alarm_dict.entityType] = alarm_dict

    def _delete(self, alarm_entity_type):
        if alarm_entity_type in self.dictionary.keys():
            del self.dictionary[alarm_entity_type]
