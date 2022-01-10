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


from o2common.config import config
from . import ocloud_route, provision_route
from . import api_ns

from o2common.helper import o2logging
logger = o2logging.get_logger(__name__)


def configure_namespace(app):
    apiims = config.get_o2ims_api_base()
    apiprovision = config.get_provision_api_base()
    logger.info(
        "Expose the O2 IMS API:{}\nExpose Provision API: {}".
        format(apiims, apiprovision))

    ocloud_route.configure_api_route()
    provision_route.configure_api_route()
    app.add_namespace(api_ns.api_ims_inventory_v1, path=apiims)
    app.add_namespace(api_ns.api_provision_v1, path=apiprovision)
