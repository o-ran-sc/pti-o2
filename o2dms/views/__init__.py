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

from flask_restx import Namespace
from o2common.config import config


api_dms_lcm_v1 = Namespace(
    "O2DMS_LCM", description='DMS LCM related operations.')
apibase = config.get_o2dms_api_base()


def configure_namespace(app):
    app.add_namespace(api_dms_lcm_v1, path=apibase)
