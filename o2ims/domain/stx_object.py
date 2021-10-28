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

# from dataclasses import dataclass
# import datetime
import json


class MismatchedModel(Exception):
    pass


class StxGenericModel:
    def __init__(self, api_response: dict = None) -> None:
        if api_response:
            self.id = api_response.uuid
            self.content = json.dumps(api_response.to_dict())
            self.updatetime = api_response.updated_at
            self.createtime = api_response.created_at
            self.name = api_response.name

    def is_outdated(self, newmodel) -> bool:
        return self.updatetime < newmodel.updatetime

    def update_by(self, newmodel) -> None:
        if self.id != newmodel.id:
            raise MismatchedModel("Mismatched model")
        self.name = newmodel.name

        self.content = newmodel.content
        self.createtime = newmodel.createtime
        self.updatetime = newmodel.updatetime
