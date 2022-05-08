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

from o2dms.api.dms_api_ns import api_dms_lcm_v1
from . import dms_route
from . import nfdeployment_desc_route
from . import nfdeployment_route
from o2common.config import config

from o2common.helper import o2logging
logger = o2logging.get_logger(__name__)


def configure_namespace(app):
    apibase = config.get_o2dms_api_base()
    logger.info(
        "Expose O2DMS API:{}".format(apibase))

    dms_route.configure_api_route()
    nfdeployment_desc_route.configure_api_route()
    nfdeployment_route.configure_api_route()
    app.add_namespace(api_dms_lcm_v1, path=apibase)
