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
# from dataclasses import asdict
from typing import List, Dict, Callable, Type
# TYPE_CHECKING
from o2ims.domain import commands, events

from o2dms.domain import commands as o2dms_cmmands
from o2dms.domain import events as o2dms_events
from o2ims.service.auditor import ocloud_handler, dms_handler, \
    resourcepool_handler, pserver_handler, pserver_cpu_handler, \
    pserver_mem_handler, pserver_port_handler, pserver_if_handler
from o2dms.service.nfdeployment_handler import publish_nfdeployment_created
from o2dms.service.nfdeployment_handler import install_nfdeployment

# if TYPE_CHECKING:
#     from . import unit_of_work


class InvalidResourceType(Exception):
    pass


EVENT_HANDLERS = {
    o2dms_events.NfDeploymentCreated: [publish_nfdeployment_created]
}


COMMAND_HANDLERS = {
    commands.UpdateOCloud: ocloud_handler.update_ocloud,
    commands.UpdateDms: dms_handler.update_dms,
    commands.UpdateResourcePool: resourcepool_handler.update_resourcepool,
    commands.UpdatePserver: pserver_handler.update_pserver,
    commands.UpdatePserverCpu: pserver_cpu_handler.update_pserver_cpu,
    commands.UpdatePserverMem: pserver_mem_handler.update_pserver_mem,
    commands.UpdatePserverIf: pserver_if_handler.update_pserver_if,
    commands.UpdatePserverPort: pserver_port_handler.update_pserver_port,
    o2dms_cmmands.InstallNfDeployment: install_nfdeployment

}  # type: Dict[Type[commands.Command], Callable]
