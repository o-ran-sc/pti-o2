# Copyright (C) 2021-2025 Wind River Systems, Inc.
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
from . import api_ns, ocloud_route, alarm_route, performance_route

from o2common.config import config

from o2common.helper import o2logging
logger = o2logging.get_logger(__name__)


def configure_namespace(app):
    apiims = config.get_o2ims_api_base()
    apimonitoring = config.get_o2ims_monitoring_api_base()
    apiperformance = config.get_o2ims_performance_api_base()
    logger.info(
        "Expose the O2 IMS API:{}\n \
        Expose Monitoring API: {}".
        format(apiims, apimonitoring))

    ocloud_route.configure_api_route()
    alarm_route.configure_api_route()
    performance_route.configure_api_route()
    app.add_namespace(api_ns.api_ims_inventory, path=apiims)
    app.add_namespace(api_ns.api_ims_monitoring, path=apimonitoring)
    app.add_namespace(api_ns.api_ims_performance, path=apiperformance)
