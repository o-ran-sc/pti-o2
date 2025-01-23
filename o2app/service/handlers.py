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

# pylint: disable=unused-argument
from __future__ import annotations

from o2dms.service import nfdeployment_handler
# from dataclasses import asdict
from typing import Dict, Callable, Type
# TYPE_CHECKING
from o2ims.domain import commands, events

from o2dms.domain import commands as o2dms_cmmands
from o2dms.domain import events as o2dms_events
from o2ims.service.auditor import ocloud_handler, dms_handler, \
    resourcepool_handler, pserver_handler, pserver_cpu_handler, \
    pserver_mem_handler, pserver_port_handler, pserver_if_handler,\
    pserver_eth_handler, pserver_acc_handler, alarm_handler, \
    pserver_dev_handler, agg_compute_handler, agg_network_handler,\
    agg_storage_handler, agg_undefined_handler, measurement_handler
from o2ims.service.command import notify_handler, registration_handler,\
    notify_alarm_handler, clear_alarm_handler, purge_alarm_handler
from o2ims.service.event import ocloud_event, resource_event, \
    resource_pool_event, alarm_event, dms_event, resource_type_event

# if TYPE_CHECKING:
#     from . import unit_of_work


class InvalidResourceType(Exception):
    pass


EVENT_HANDLERS = {
    o2dms_events.NfDeploymentStateChanged: [
        nfdeployment_handler.publish_nfdeployment_state_change
    ],
    # o2dms_events.NfDeploymentCreated: [
    #     nfdeployment_handler.publish_nfdeployment_created],
    # o2dms_events.NfDeploymentInstalled: [
    #     nfdeployment_handler.publish_nfdeployment_installed],
    # o2dms_events.NfDeploymentUninstalling: [
    #     nfdeployment_handler.publish_nfdeployment_uninstalling],
    # o2dms_events.NfDeploymentUninstalled: [
    #     nfdeployment_handler.publish_nfdeployment_uninstalled]
    events.OcloudChanged: [ocloud_event.notify_ocloud_update],
    events.ResourceTypeChanged: [resource_type_event.\
                                 notify_resourcetype_change],
    events.DmsChanged: [dms_event.notify_dms_change],
    events.ResourceChanged: [resource_event.notify_resource_change],
    events.ResourcePoolChanged: [resource_pool_event.\
                                 notify_resourcepool_change],
    events.AlarmEventChanged: [alarm_event.\
                               notify_alarm_event_change],
    events.AlarmEventCleared: [alarm_event.\
                               notify_alarm_event_clear],
    events.AlarmEventPurged: [alarm_event.\
                              notify_alarm_event_purge],
}  # type: Dict[Type[events.Event], Callable]


COMMAND_HANDLERS = {
    commands.UpdateOCloud: ocloud_handler.update_ocloud,
    commands.UpdateDms: dms_handler.update_dms,
    commands.UpdateAlarm: alarm_handler.update_alarm,
    commands.UpdateResourcePool: resourcepool_handler.update_resourcepool,
    commands.UpdateComputeAgg: agg_compute_handler.update_compute_aggregate,
    commands.UpdateNetworkAgg: agg_network_handler.update_network_aggregate,
    commands.UpdateStorageAgg: agg_storage_handler.update_storage_aggregate,
    commands.UpdateUndefinedAgg:
    agg_undefined_handler.update_undefined_aggregate,
    commands.UpdatePserver: pserver_handler.update_pserver,
    commands.UpdatePserverCpu: pserver_cpu_handler.update_pserver_cpu,
    commands.UpdatePserverMem: pserver_mem_handler.update_pserver_mem,
    commands.UpdatePserverIf: pserver_if_handler.update_pserver_if,
    commands.UpdatePserverIfPort: pserver_port_handler.update_pserver_port,
    commands.UpdatePserverEth: pserver_eth_handler.update_pserver_eth,
    commands.UpdatePserverDev: pserver_dev_handler.update_pserver_dev,
    commands.UpdatePserverAcc: pserver_acc_handler.update_pserver_acc,
    o2dms_cmmands.HandleNfDeploymentStateChanged:
    nfdeployment_handler.handle_nfdeployment_statechanged,
    o2dms_cmmands.InstallNfDeployment:
    nfdeployment_handler.install_nfdeployment,
    o2dms_cmmands.UninstallNfDeployment:
    nfdeployment_handler.uninstall_nfdeployment,
    o2dms_cmmands.DeleteNfDeployment:
    nfdeployment_handler.delete_nfdeployment,
    commands.PubMessage2SMO: notify_handler.notify_change_to_smo,
    commands.PubAlarm2SMO: notify_alarm_handler.notify_alarm_to_smo,
    commands.Register2SMO: registration_handler.registry_to_smo,
    commands.ClearAlarmEvent: clear_alarm_handler.clear_alarm_event,
    commands.PurgeAlarmEvent: purge_alarm_handler.purge_alarm_event,
    commands.UpdateMeasurement: measurement_handler.update_measurement,
}  # type: Dict[Type[commands.Command], Callable]
