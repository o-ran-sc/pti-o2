# Copyright (C) 2021-2022 Wind River Systems, Inc.
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

from o2common.views.route import O2Namespace


api_ims_inventory_v1 = O2Namespace(
    "O2IMS_Inventory",
    description='IMS Inventory related operations.')

api_provision_v1 = O2Namespace(
    "PROVISION",
    description='Provision related operations.')

api_monitoring_v1 = O2Namespace(
    "O2IMS_InfrastructureMonitoring",
    description='O2 IMS Monitoring related operations.')
