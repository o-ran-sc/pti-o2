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

# pylint: disable=unused-argument
from __future__ import annotations

from o2dms.service import nfdeployment_handler
# from dataclasses import asdict
from typing import List, Dict, Callable, Type
# TYPE_CHECKING
from o2ims.domain import commands, events

from o2dms.domain import commands as o2dms_cmmands
from o2dms.domain import events as o2dms_events
from o2ims.service.auditor import ocloud_handler, dms_handler, \
    resourcepool_handler, pserver_handler, pserver_cpu_handler, \
    pserver_mem_handler, pserver_port_handler, pserver_if_handler,\
    pserver_eth_handler

# if TYPE_CHECKING:
#     from . import unit_of_work


class InvalidResourceType(Exception):
    pass


EVENT_HANDLERS = {
    o2dms_events.NfDeploymentCreated: [
        nfdeployment_handler.publish_nfdeployment_created],
    o2dms_events.NfDeploymentInstalled: [
        nfdeployment_handler.publish_nfdeployment_installed],
    o2dms_events.NfDeploymentUninstalling: [
        nfdeployment_handler.publish_nfdeployment_uninstalling],
    o2dms_events.NfDeploymentUninstalled: [
        nfdeployment_handler.publish_nfdeployment_uninstalled]
} # type: Dict[Type[events.Event], Callable]


COMMAND_HANDLERS = {
    commands.UpdateOCloud: ocloud_handler.update_ocloud,
    commands.UpdateDms: dms_handler.update_dms,
    commands.UpdateResourcePool: resourcepool_handler.update_resourcepool,
    commands.UpdatePserver: pserver_handler.update_pserver,
    commands.UpdatePserverCpu: pserver_cpu_handler.update_pserver_cpu,
    commands.UpdatePserverMem: pserver_mem_handler.update_pserver_mem,
    commands.UpdatePserverIf: pserver_if_handler.update_pserver_if,
    commands.UpdatePserverIfPort: pserver_port_handler.update_pserver_port,
    commands.UpdatePserverEth: pserver_eth_handler.update_pserver_eth,
    o2dms_cmmands.InstallNfDeployment: \
        nfdeployment_handler.install_nfdeployment,
    o2dms_cmmands.UninstallNfDeployment: \
        nfdeployment_handler.uninstall_nfdeployment,
    o2dms_cmmands.DeleteNfDeployment: \
        nfdeployment_handler.delete_nfdeployment,
}  # type: Dict[Type[commands.Command], Callable]
