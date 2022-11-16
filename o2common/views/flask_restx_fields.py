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

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from flask_restx import fields
import json

from o2common.helper import o2logging
logger = o2logging.get_logger(__name__)

class Json2Dict(fields.Raw):

    def format(self, value):
        value2 = None
        try:
            value2 = json.loads(value) if value else None
        except Exception as ex:
            logger.warning(f"Failed to loads json string: {value}, exception: {str(ex)}")
            value2 = value
        return value2
